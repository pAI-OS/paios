from threading import Lock
from backend.schemas import FileSchema
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from common.paths import chroma_db_path
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain, create_history_aware_retriever
import shutil
from starlette.datastructures import UploadFile
from uuid import uuid4
from backend.models import File, Page, Chunk
from backend.db import db_session_context
from sqlalchemy import delete, select, func
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Union
from backend.managers import ResourcesManager, PersonasManager
from distutils.util import strtobool
import os
import logging
from enum import Enum
import aiofiles
import asyncio
from dotenv import load_dotenv, set_key
from common.paths import base_dir
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

logger = logging.getLogger(__name__)

class FileStatus(Enum):
    WAITING = 'waiting'
    UPLOADED = 'uploaded'
    SPLITTING = 'splitting'
    SPLIT = 'split'
    INDEXING = 'indexing'
    DONE = 'done'
    FAILED = 'failed'

class RagManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(RagManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self, chunk_size=None, chunk_overlap=None, add_start_index=None, embedder_model=None, system_prompt=None):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._initialized = True
                    load_dotenv(base_dir / '.env')
                    self.chunk_size = chunk_size if chunk_size else self.get_params('CHUNK_SIZE')
                    self.chunk_overlap = chunk_overlap if chunk_overlap else self.get_params('CHUNK_OVERLAP')
                    self.add_start_index = add_start_index if add_start_index else self.get_params('ADD_START_INDEX')
                    self.embedder_model = embedder_model if embedder_model else self.get_params('EMBEDDER_MODEL')
                    self.system_prompt = system_prompt if system_prompt else self.get_params('SYSTEM_PROMPT')
                    print("params:::", self.chunk_size, self.chunk_overlap, self.add_start_index, self.embedder_model, self.system_prompt)           
                    
    def get_params(self, param_name: str):
        if param_name == 'CHUNK_SIZE':
            chunk_size=os.environ.get('CHUNK_SIZE')
            if not chunk_size:
                chunk_size = 2000
            set_key(base_dir / '.env', 'CHUNK_SIZE', str(chunk_size))
            return chunk_size
        if param_name == 'CHUNK_OVERLAP':            
            chunk_overlap=os.environ.get('CHUNK_OVERLAP')
            if not chunk_overlap:
                chunk_overlap = 400 
            set_key(base_dir / '.env', 'CHUNK_OVERLAP', str(chunk_overlap))
            return chunk_overlap
        if param_name == 'ADD_START_INDEX':
            add_start_index=os.environ.get('ADD_START_INDEX')
            if not add_start_index:                
                add_start_index = 'True'
            set_key(base_dir / '.env', 'ADD_START_INDEX', str(add_start_index))        
            return add_start_index
        if param_name == 'EMBEDDER_MODEL':
            embedder_model=os.environ.get('EMBEDDER_MODEL')
            if not embedder_model:                
                embedder_model = 'llama3:latest'
            set_key(base_dir / '.env', 'EMBEDDER_MODEL', str(embedder_model))        
            return embedder_model
        if param_name == 'SYSTEM_PROMPT':
            system_prompt=os.environ.get('SYSTEM_PROMPT')
            if not system_prompt:                
                system_prompt = "You are a helpful assistant for students learning needs."
            set_key(base_dir / '.env', 'SYSTEM_PROMPT', str(system_prompt))        
            return system_prompt 

    async def create_index(self, resource_id: str, path_files: List[str], files_ids:List[str]) -> List[dict]:
        loop = asyncio.get_running_loop()        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(self.chunk_size),
            chunk_overlap=int(self.chunk_overlap),
            add_start_index=bool(strtobool(self.add_start_index))
        )
        file_info_list = []
        vectorstore = await self.initialize_chroma(resource_id) 
        
        for path, file_id in zip(path_files, files_ids):
            file_name = Path(path).name
            
            try:
                # Load the PDF
                loader = PyPDFLoader(path)
                
                docs = await loop.run_in_executor(None, loader.load)  # Load all pages at once
                split_documents = []
                split_ids = []
                
                # Process each page in the PDF
                for doc in docs:
                    page_id = str(uuid4())  # Unique ID for each page
                    file_info_list.append({"file_id": file_id, "file_name": file_name, "page_id": page_id})
                    
                    await self.update_file_status(file_id, FileStatus.SPLITTING.value)
                    # Split the document into smaller chunks
                    splits = text_splitter.split_documents([doc])
                    await self.create_page(page_id, file_id, resource_id)
                    
                    for split in splits:
                        chunk_id = str(uuid4())  # Unique ID for each chunk
                        await self.create_chunk(chunk_id, page_id, file_id, resource_id)
                        split.metadata["original_id"] = page_id
                        split_documents.append(split)
                        split_ids.append(chunk_id)
                    
                    # Update status to 'split' after splitting
                    await self.update_file_status(file_id, FileStatus.SPLIT.value)

                # Add the split documents to the vectorstore and update status to 'indexing'
                await self.update_file_status(file_id, FileStatus.INDEXING.value)
                await loop.run_in_executor(None, lambda: vectorstore.add_documents(documents=split_documents, ids=split_ids))
                
                # Update status to 'done' once indexing is complete
                await self.update_file_status(file_id, FileStatus.DONE.value)

            except Exception as e:
                # Update status to 'failed' if an error occurs
                await self.update_file_status(file_id, FileStatus.FAILED.value)
                raise e

        return file_info_list   

    async def update_file_status(self, file_id: str, status: str):
        async with db_session_context() as session:
            stmt = select(File).filter(File.id == file_id)
            files = (await session.execute(stmt)).scalars().all()
            for file in files:
                file.indexing_status = status
                await session.commit()         
    
    async def create_file(self, file_id: str, assistant_id: str, file_name: str, indexing_status: str):
        async with db_session_context() as session:
            try:
                new_file = File(id=file_id, name=file_name, assistant_id=assistant_id, indexing_status=indexing_status)            
                session.add(new_file)
                await session.commit()
                await session.refresh(new_file)
            except Exception as e:                
                print(f"An error occurred creating a file: {e}")

    async def create_page(self, page_id: str, file_id: str,  assistant_id: str):
        async with db_session_context() as session:
            try:
                new_page = Page(id=page_id, file_id=file_id, assistant_id=assistant_id)            
                session.add(new_page)
                await session.commit()
                await session.refresh(new_page) 
            except Exception as e:                
                print(f"An error occurred creating a page: {e}")
    
    async def create_chunk(self, chunk_id:str, page_id: str, file_id: str,  assistant_id: str):
        async with db_session_context() as session:
            try:
                new_chunk = Chunk(id=chunk_id, page_id=page_id, file_id=file_id, assistant_id=assistant_id)            
                session.add(new_chunk)
                await session.commit()
                await session.refresh(new_chunk)
            except Exception as e:                
                print(f"An error occurred creating a chunk: {e}")

            
    async def initialize_chroma(self, collection_name: str):
        embed = OllamaEmbeddings(model=self.embedder_model)
        
        path = Path(chroma_db_path)
        vectorstore = Chroma(persist_directory=str(path),
                             collection_name=collection_name,
                             embedding_function=embed)
        return vectorstore

    def create_history_aware_retriever(self, llm, retriever):
        contextualize_q_system_prompt = """Given a chat history and the latest user question \
        which might reference context in the chat history, formulate a standalone question \
        which can be understood without the chat history. Do NOT answer the question, \
        just reformulate it if needed and otherwise return it as is."""

        contextualize_q_prompt = ChatPromptTemplate.from_messages([
                                    ("system", contextualize_q_system_prompt),
                                    MessagesPlaceholder("chat_history"),
                                    ("human", "{input}"),
                                ])
        return create_history_aware_retriever(llm, retriever, contextualize_q_prompt)

    async def create_question_answer_chain(self, llm, name=None, expertise=None):

        qa_system_prompt = """You are a helpful assistant for students' learning needs. \
                        Your name is```{persona_name}``` your capabilities and expertise are: ```{persona_expertise}```. \
                        Focus solely on answering their questions without repeating your greeting. \
                        Use the following pieces of retrieved context to answer the question. \
                        If you don't know the answer, just say that you don't know. \
                        You are expected to answer questions about the following context: '{context}'"""
        qa_system_prompt = qa_system_prompt.format(persona_name=name, persona_expertise= expertise, context="{context}")
        qa_prompt = ChatPromptTemplate.from_messages([
            ("system", qa_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])        
        return create_stuff_documents_chain(llm, qa_prompt)
    
    def create_conversational_chain(self,rag_chain, get_session_history):
        return RunnableWithMessageHistory(
            rag_chain,
            get_session_history,
            input_messages_key="input",
            history_messages_key="chat_history",
            output_messages_key="answer",
        )
    
    def get_session_history(self,store, session_id: str):
        if session_id not in store:
            store[session_id] = ChatMessageHistory()
        return store[session_id]
    

    async def retrieve_and_generate_chat_context(self, collection_name, query, llm, session_id =None) -> str:
        resources_m = ResourcesManager()
        personas_m = PersonasManager()

        resource = await resources_m.retrieve_resource(collection_name)
        persona_id = resource.persona_id
        persona = await personas_m.retrieve_persona(persona_id)        
        expertise = persona.description
        name= persona.name
        
        vectorstore = await self.initialize_chroma(collection_name)
        retriever = vectorstore.as_retriever()

        history_aware_retriever = self.create_history_aware_retriever(llm, retriever)
        question_answer_chain = await self.create_question_answer_chain(llm, name, expertise)

        rag_chain = create_retrieval_chain(history_aware_retriever, question_answer_chain)
        
        store = {}
        conversational_rag_chain = self.create_conversational_chain(rag_chain, lambda session_id: self.get_session_history(store, session_id))

        response = conversational_rag_chain.invoke({
            "input": query},
            config={
                "configurable": {
                    "session_id": session_id}},
                    )
        print("Response: ", response)
        return response    
    
    async def retrieve_and_generate(self, collection_name, query, llm) -> str:
        resources_m = ResourcesManager()
        personas_m = PersonasManager()

        resource = await resources_m.retrieve_resource(collection_name)        
        persona_id = resource.persona_id
        persona = await personas_m.retrieve_persona(persona_id)        
        expertise = persona.description
        name= persona.name

        system_prompt = self.system_prompt + """
                    \n-First, you greet them with your name ```{persona_name}``` and with no more than 30 words explain very briefly your capabilities and expertise using the description: ```{persona_expertise}```.      
                    \n-Then focus solely on answering their questions without repeating your introduction.
                    \nYou are expected to answer questions about the following context: \'{context}\'                                                                                   
                    """
        system_prompt = system_prompt.format(persona_name=name, persona_expertise= expertise, context="{context}")        

        prompt = ChatPromptTemplate.from_messages([
                    ("system", system_prompt),                   
                    ("human", "{input}"),
                ])        
        print(f"\n\nPrompt: {prompt}\n")

        vectorstore = await self.initialize_chroma(collection_name)
        retriever = vectorstore.as_retriever()

        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        async for chunk in rag_chain.astream({"input": query}):
            print("chunk:", chunk)
        print("Query: ", query)

        response = rag_chain.invoke({"input": query})
        return response
    
    async def save_file(self, file: UploadFile, directory: Path):
        file_path = directory / file.filename
        async with aiofiles.open(file_path, 'wb') as out_file:
            while content := await file.read(1024):  # Read in chunks
                await out_file.write(content)
        return str(file_path.absolute())

    
    async def upload_file(self, resource_id: str, files: List[UploadFile]) -> Union[List[dict], str]:
        all_files_paths = []
        all_files_ids = []
        for file in files:
            file_id = str(uuid4())
            # Create a File entry in the database with status 'splitting'
            await self.create_file(
                file_id=file_id,
                assistant_id=resource_id,
                file_name=file.filename,
                indexing_status=FileStatus.WAITING.value
            )
            all_files_ids.append(file_id)
        try:
            
            for file, file_id in zip(files, all_files_ids):
                
                directory = Path(f"./uploads/{resource_id}")
                directory.mkdir(parents=True, exist_ok=True)
                
                path = await self.save_file(file, directory)
                await self.update_file_status(file_id, FileStatus.UPLOADED.value)
                all_files_paths.append(path)

            result = await self.create_index(resource_id, all_files_paths, all_files_ids)   
            await self.delete_tmp_files(resource_id)
            return result
        except Exception as e:
            print(f"An error occurred while uploading files: {e}")
            return "File upload failed"


    async def delete_tmp_files(self, assistant_id: str):
        try:
            # Define the directory path using the assistant_id
            directory = Path(f"./uploads/{assistant_id}")
            
            # Check if the directory exists
            if directory.exists() and directory.is_dir():
                # Remove the directory and all its contents
                shutil.rmtree(directory)
            else:
                logger.error(f"Directory for assistant {assistant_id} does not exist.", exc_info=True)
        except Exception as e:
            logger.error(f"An error occurred while deleting folder for assistant {assistant_id}: {e}", exc_info=True)
        
    async def retrieve_file(self, file_id:str) -> Optional[List[FileSchema]]:
        async with db_session_context() as session:            
            result = await session.execute(select(File).filter(File.id == file_id))
            files = [FileSchema.from_orm(file) for file in result.scalars().all()]
            if files:
                return files
            return None
        
    # Method to retrieve pages for a given file_id
    async def retrieve_pages(self, file_id: str) -> List[Page]:
        async with db_session_context() as session:
            result = await session.execute(select(Page).filter(Page.file_id == file_id))
            pages = result.scalars().all()
            return pages

    # Method to retrieve chunks for a given page_id
    async def retrieve_chunks(self, page_id: str) -> List[Chunk]:
        async with db_session_context() as session:
            result = await session.execute(select(Chunk).filter(Chunk.page_id == page_id))
            chunks = result.scalars().all()
            return chunks
    
    async def delete_documents_from_chroma(self, resource_id: str, file_ids: List[str]):
        vectorstore = await self.initialize_chroma(resource_id)
        
        for file_id in file_ids:
            # Retrieve the files
            files = await self.retrieve_file(file_id)
            
            if not files:
                return None
            
            # Collect and delete chunks for the files
            await self._process_files_for_deletion(files, vectorstore)

        return "Documents deleted"

    async def _process_files_for_deletion(self, files: List[File], vectorstore):
        list_chunks_id = []
        
        for file in files:
            # Collect chunk IDs for each file
            chunk_ids = await self._collect_chunk_ids(file.id)
            list_chunks_id.extend(chunk_ids)
        
        # Delete all chunks from ChromaDB
        if list_chunks_id:
            vectorstore.delete(ids=list_chunks_id)

    async def _collect_chunk_ids(self, file_id: int) -> List[str]:
        list_chunks_id = []
        
        # Retrieve pages for the file
        pages = await self.retrieve_pages(file_id)
        
        for page in pages:
            # Retrieve chunks for each page and collect their IDs
            chunks = await self.retrieve_chunks(page.id)
            list_chunks_id.extend([chunk.id for chunk in chunks])
        
        return list_chunks_id

       
    async def delete_file_from_db(self, file_ids: List[str]):
        async with db_session_context() as session:
            try:
                for file_id in file_ids:
                    # Retrieve the file (you already have this step)
                    files = await self.retrieve_file(file_id)

                    if not files:
                        continue

                    await self._delete_files(files, session)

                await session.commit()
                return True
            except Exception as e:
                print("Error in delete from db:", e)
                return None

    async def _delete_files(self, files: List[FileSchema], session: db_session_context):
        for file in files:
            await self._delete_pages_and_chunks(file.id, session)
            stmt_delete_file = delete(File).where(File.id == file.id)
            await session.execute(stmt_delete_file)

    async def _delete_pages_and_chunks(self, file_id: str, session: db_session_context):
        pages = await self.retrieve_pages(file_id)
        if not pages:
            return
        
        for page in pages:
            # Retrieve and delete chunks
            await self._delete_chunks(page.id, session)

        # Delete all pages for the file
        stmt_delete_pages = delete(Page).where(Page.id.in_([page.id for page in pages]))
        await session.execute(stmt_delete_pages)

    async def _delete_chunks(self, page_id: int, session):
        chunks = await self.retrieve_chunks(page_id)
        if chunks:
            stmt_delete_chunks = delete(Chunk).where(Chunk.id.in_([chunk.id for chunk in chunks]))
            print("delete chunk")
            await session.execute(stmt_delete_chunks)

    async def retrieve_files(self, resource_id: str, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None,
                         sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None) -> Tuple[List[FileSchema], int]:
        async with db_session_context() as session:
            query = self._apply_filters(select(File).filter(File.assistant_id == resource_id), filters)
            query = self._apply_sorting(query, sort_by, sort_order)
            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            files = [FileSchema.from_orm(file) for file in result.scalars().all()]
            total_count = await self._get_total_count(filters)

            return files, total_count

    def _apply_filters(self, query, filters: Optional[Dict[str, Any]]):
        if filters:
            for key, value in filters.items():
                if key == 'name':
                    query = query.filter(File.name.ilike(f"%{value}%"))
                elif isinstance(value, list):
                    query = query.filter(getattr(File, key).in_(value))
                else:
                    query = query.filter(getattr(File, key) == value)
        return query

    def _apply_sorting(self, query, sort_by: Optional[str], sort_order: str):
        if sort_by and sort_by in ['name']:
            order_column = getattr(File, sort_by)
            query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)
        return query

    async def _get_total_count(self, filters: Optional[Dict[str, Any]]) -> int:
        async with db_session_context() as session:
            count_query = select(func.count()).select_from(File)
            count_query = self._apply_filters(count_query, filters)

            total_count = await session.execute(count_query)
            return total_count.scalar()