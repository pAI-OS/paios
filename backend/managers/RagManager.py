from threading import Lock
from backend.schemas import FileSchema
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from common.paths import chroma_db_path
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import shutil
from starlette.datastructures import UploadFile
from uuid import uuid4
from backend.models import File
from backend.db import db_session_context
from sqlalchemy import delete, select, func
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any, Union
from backend.managers import ResourcesManager, PersonasManager
from distutils.util import strtobool
import os
import logging
from enum import Enum

logger = logging.getLogger(__name__)

class FileStatus(Enum):
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

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._initialized = True

    async def create_index(self, resource_id: str, path_files: List[str]) -> List[dict]:
        # Define the text splitter
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=int(os.environ.get('CHUNK_SIZE')),
            chunk_overlap=int(os.environ.get('CHUNK_OVERLAP')),
            add_start_index=bool(strtobool(os.environ.get('ADD_START_INDEX')))
        )
        
        file_info_list = []
        
        # Initialize the vector store once
        vectorstore = await self.initialize_chroma(resource_id)
        
        # Iterate over all the files
        for path in path_files:
            file_id = str(uuid4())
            file_name = Path(path).name
            
            try:
                # Load the PDF
                loader = PyPDFLoader(path)
                docs = loader.load()  # Load all pages at once
                
                split_documents = []
                split_ids = []
                
                # Process each page in the PDF
                for doc in docs:
                    page_id = str(uuid4())  # Unique ID for each page
                    
                    # Create a File entry in the database with status 'splitting'
                    await self.create_file(
                        assistant_id=resource_id,
                        file_id=file_id,
                        file_name=file_name,
                        page_id=page_id,  # Unique page ID
                        indexing_status=FileStatus.SPLITTING.value
                    )
                    
                    file_info_list.append({"file_id": file_id, "file_name": file_name, "page_id": page_id})
                    
                    # Split the document into smaller chunks
                    splits = text_splitter.split_documents([doc])
                    
                    # Update num_chunks for all File records with the current file_id
                    await self.update_file_num_chunks(file_id, len(splits))
                    
                    for i, split in enumerate(splits):
                        split.metadata["original_id"] = page_id
                        split_documents.append(split)
                        split_ids.append(f"{page_id}-{i}")
                    
                    # Update status to 'split' after splitting
                    await self.update_file_status(file_id, FileStatus.SPLIT.value)

                # Add the split documents to the vectorstore and update status to 'indexing'
                await self.update_file_status(file_id, FileStatus.INDEXING.value)
                vectorstore.add_documents(documents=split_documents, ids=split_ids)
                
                # Update status to 'done' once indexing is complete
                await self.update_file_status(file_id, FileStatus.DONE.value)

            except Exception as e:
                # Update status to 'failed' if an error occurs
                await self.update_file_status(file_id, FileStatus.FAILED.value)
                raise e
        
        return file_info_list

    async def update_file_num_chunks(self, file_id: str, num_chunks: int):
        async with db_session_context() as session:
            stmt = select(File).filter(File.file_id == file_id)
            files = (await session.execute(stmt)).scalars().all()
            
            for file in files:
                file.num_chunks = str(num_chunks)
            
            await session.commit()

    async def update_file_status(self, file_id: str, status: str):
        async with db_session_context() as session:
            stmt = select(File).filter(File.file_id == file_id)
            files = (await session.execute(stmt)).scalars().all()
            for file in files:
                file.indexing_status = status
                await session.commit()
       
    async def create_files_for_resource(self, resource_id: str, file_info_list: List[dict]):
        for file_info in file_info_list:
            await self.create_file(
                assistant_id=resource_id,
                file_id=file_info['file_id'],
                file_name=file_info['file_name'],
                page_id=file_info['page_id'],
                indexing_status=file_info.get('indexing_status', 'initializing'),
                num_chunks=file_info.get('num_chunks', 0)  # Default to 0 if not set
            )            
    
    async def create_file(self, assistant_id: str, file_id: str, file_name: str, page_id: str,  indexing_status: str, num_chunks: int = 0):
        async with db_session_context() as session:
            try:
                new_file = File(id=page_id, name=file_name, assistant_id=assistant_id, file_id=file_id, num_chunks=str(num_chunks), indexing_status=indexing_status)            
                session.add(new_file)
                await session.commit()
                await session.refresh(new_file)
            except Exception as e:                
                print(f"An error occurred: {e}")

            
    async def initialize_chroma(self, collection_name: str):
        embed = OllamaEmbeddings(model=os.environ.get('EMBEDDER_MODEL'))
        
        path = Path(chroma_db_path)
        vectorstore = Chroma(persist_directory=str(path),
                             collection_name=collection_name,
                             embedding_function=embed)
        return vectorstore
    
    async def retrieve_and_generate(self, collection_name, query, llm) -> str:
        resources_m = ResourcesManager()
        personas_m = PersonasManager()
        resource = await resources_m.retrieve_resource(collection_name)        
        persona_id = resource.persona_id
        persona = await personas_m.retrieve_persona(persona_id)
        personality_prompt = persona.description
        # Combine the system prompt and context        
        system_prompt = (os.environ.get('SYSTEM_PROMPT') + "\n\n{context}" +
                        "\n\nHere is some information about the assistant expertise to help you answer your questions: " +
                        personality_prompt)
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
            ])
        print(f"\n\nPrompt: {prompt}\n")
        vectorstore = await self.initialize_chroma(collection_name)
        retriever = vectorstore.as_retriever()

        # Use the LLM chain with the prompt
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        
        async for chunk in rag_chain.astream({"input": query}):
            print("chunk:", chunk)
        print("Query: ", query)
        # Invoke the RAG chain with query as input
        response = rag_chain.invoke({"input": query})
        return response  
    
    async def upload_file(self, resource_id: str, files: List[UploadFile]) -> Union[List[dict], str]:
        try:
            all_docs = []
            for file in files:
                # Define the directory where files will be saved
                directory = Path(f"./uploads/{resource_id}")                
                directory.mkdir(parents=True, exist_ok=True)
                
                # Save the file
                file_path = directory / file.filename
                path = str(file_path.absolute())
                all_docs.append(path)
                with open(file_path, "wb") as buffer:
                    shutil.copyfileobj(file.file, buffer)

            result = await self.create_index(resource_id, all_docs)   
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
            result = await session.execute(select(File).filter(File.file_id == file_id))
            files = [FileSchema.from_orm(file) for file in result.scalars().all()]
            if files:
                return files
            return None
    
    async def delete_documents_from_chroma(self, resource_id: str, file_ids=List[str]):
        vectorstore = await self.initialize_chroma(resource_id)
        for file_id in file_ids:
            files = await self.retrieve_file(file_id)
            
            if files:
                page_ids = []
                for file in files:
                    num_chunks = int(file.num_chunks)
                    page_id = file.id
                    page_ids.append(page_id)        
                
                    list_chunks_id = []
                    for n in range(0, num_chunks):
                        chunk_id = f"{page_id}-{n}"
                        list_chunks_id.append(chunk_id)
                    
                    vectorstore.delete(ids=list_chunks_id)
            else:
                return None
        return "Documents deleted"
       
    async def delete_file_from_db(self, file_ids: List[str]):
        page_ids = []
        for file_id in file_ids:
            files = await self.retrieve_file(file_id)
            if files:                
                for file in files:
                    page_id = file.id
                    page_ids.append(page_id)
        async with db_session_context() as session:
            try:                            
                stmt = delete(File).where(File.id.in_(page_ids))
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0
            except Exception as e:
                print("error in delete from db",e)
                return None

    async def retrieve_files(self, resource_id: str, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None,
                         sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None) -> Tuple[List[FileSchema], int]:
        async with db_session_context() as session:
            query = self._apply_filters(select(File).filter(File.assistant_id == resource_id), filters)
            query = self._apply_sorting(query, sort_by, sort_order)
            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            files = [FileSchema.from_orm(file) for file in result.scalars().all()]
            seen_file_ids = set()
            unique_files = []
            for file in files:
                if file.file_id not in seen_file_ids:
                    unique_files.append(file)
                    seen_file_ids.add(file.file_id)           

            total_count = await self._get_total_count(filters)

            return unique_files, total_count

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
