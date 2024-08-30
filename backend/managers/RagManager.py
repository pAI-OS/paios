from threading import Lock
from backend.schemas import FileSchema
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from common.paths import chroma_db_path
from pathlib import Path
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
import shutil
from starlette.datastructures import UploadFile
from uuid import uuid4
from backend.models import File
from backend.db import db_session_context
from sqlalchemy import delete, select, func
from pathlib import Path
from typing import List, Tuple, Optional, Dict, Any
from common.config import text_splitter_config, system_prompt_config,embedder_config


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

        all_docs = []
        all_ids = []
        file_names = []
        file_info_list = []
        all_chunks = []

        for path in path_files:
            loader = PyPDFLoader(path)
            docs = loader.load()  
            all_docs.append(docs[0])
            file_id = str(uuid4())
            all_ids.append(file_id)
            
            # Extract just the file name
            file_name = Path(path).name
            file_names.append(file_name)
            
            # Collect file_id and file_name into a dictionary
            file_info_list.append({"file_id": file_id, "file_name": file_name})
        
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=text_splitter_config.get("chunk_size"), 
            chunk_overlap=text_splitter_config.get("chunk_overlap"), 
            add_start_index=text_splitter_config.get("add_start_index")
        )
        
        # Split documents while retaining metadata
        split_documents = []
        split_ids = []
        
        for doc, doc_id in zip(all_docs, all_ids):
            #split the document into smaller chunks
            splits = text_splitter.split_documents([doc])
            all_chunks.append(len(splits))
            # Append each chunk to the split_documents list
            for i, split in enumerate(splits):
                split.metadata["original_id"] = doc_id
                split_documents.append(split)
                # Create unique IDs for each split based on the original ID and chunk index
                split_ids.append(f"{doc_id}-{i}")
        
        await self.create_files_for_resource(resource_id, file_names, all_ids, all_chunks)
        
        # add the split documents to the vectorstore
        vectorstore = await self.initialize_chroma(resource_id)
        vectorstore.add_documents(documents=split_documents, ids=split_ids)
        return file_info_list
       
    async def create_files_for_resource(self, resource_id: str, files: List[str], ids: List[str], num_chunks:List[int]):
        for file_name, file_id, chunk in zip(files, ids, num_chunks):
            await self.create_file(file_name, resource_id, file_id, chunk)
    
    async def create_file(self, file_name: str, assistant_id: str, file_id: str, num_chunks: int = 0):        
        async with db_session_context() as session:
            new_file = File(id=file_id, name=file_name, assistant_id=assistant_id, num_chunks=str(num_chunks))
            session.add(new_file)
            await session.commit()
            await session.refresh(new_file)
            return
    
    async def update_file(self, assistant_id: str, file_name: str) -> str:
        async with db_session_context() as session:
            # delete the file from the database if it exists
            stmt = delete(File).where(File.assistant_id == assistant_id)
            await session.execute(stmt)
            await session.commit()
            return self.create_file(file_name, assistant_id)
            
    async def initialize_chroma(self, collection_name: str):
        embed = OllamaEmbeddings(model=embedder_config.get("model_name"))
        
        path = Path(chroma_db_path)
        vectorstore = Chroma(persist_directory=str(path),
                             collection_name=collection_name,
                             embedding_function=embed)
        return vectorstore
    
    async def retrieve_and_generate(self, collection_name, query, llm) -> str:
        system_prompt = ( system_prompt_config.get("text"))
    
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                ("human", "{input}"),
            ]
        )
        vectorstore = await self.initialize_chroma(collection_name)
        retriever = vectorstore.as_retriever()
        question_answer_chain = create_stuff_documents_chain(llm, prompt)
        rag_chain = create_retrieval_chain(retriever, question_answer_chain)
        response = rag_chain.invoke({"input": query})
        return response  
    
    async def upload_file(self, resource_id: str, files: List[UploadFile]) -> List[dict]:
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

            return await self.create_index(resource_id, all_docs)   
        except Exception as e:
            print(f"An error occurred while uploading files: {e}")
            return "File upload failed"

    async def retrieve_file(self, id:str) -> Optional[FileSchema]:
        async with db_session_context() as session:            
            result = await session.execute(select(File).filter(File.id == id))
            file = result.scalar_one_or_none()
            if file:
                return FileSchema(
                    id=file.id,
                    name=file.name,
                    num_chunks = file.num_chunks             
                )
            return None
    
    async def delete_documents_from_chroma(self, resource_id: str, file_ids=List[str]):
            for file_id in file_ids:
                file = await self.retrieve_file(file_id)
                if file:
                    num_chunks = int(file.num_chunks)            
                    vectorstore = await self.initialize_chroma(resource_id)
                    
                    #iterate over num_chunks to create list of embeddings {file.id}-{chunk}
                    list_chunks_id = []
                    for n in range(0, num_chunks):
                        chunk_id = f"{file_id}-{n}"
                        list_chunks_id.append(chunk_id)
                    vectorstore.delete(ids=list_chunks_id)
                else:
                    return None
            return "Documents deleted"
       
    async def delete_file_from_db(self, file_ids: List[str]):        
        async with db_session_context() as session:
            try:                            
                stmt = delete(File).where(File.id.in_(file_ids))
                result = await session.execute(stmt)
                await session.commit()
                return result.rowcount > 0
            except Exception as e:
                print(e)
                return None

    async def retrieve_files(self, resource_id: str, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None,
                                sort_order:str = 'asc',  filters: Optional[Dict[str, Any]] = None) -> Tuple[List[FileSchema], int]:
        async with db_session_context() as session:
            query = select(File).filter(File.assistant_id == resource_id)
            
            if filters:
                for key, value in filters.items():
                    if key == 'name':
                        query = query.filter(File.name.ilike(f"%{value}%"))
                    elif isinstance(value, list):
                        query = query.filter(getattr(File, key).in_(value))
                    else:
                        query = query.filter(getattr(File, key) == value)

            if sort_by and sort_by in ['name']:
                order_column = getattr(File, sort_by)
                query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            files = [FileSchema.from_orm(file) for file in result.scalars().all()]

            # Get total count
            count_query = select(func.count()).select_from(File)
            if filters:
                for key, value in filters.items():
                    if key == 'name':
                        count_query = count_query.filter(File.name.ilike(f"%{value}%"))
                    elif isinstance(value, list):
                        count_query = count_query.filter(getattr(File, key).in_(value))
                    else:
                        count_query = count_query.filter(getattr(File, key) == value)

            total_count = await session.execute(count_query)
            total_count = total_count.scalar()

            return files, total_count