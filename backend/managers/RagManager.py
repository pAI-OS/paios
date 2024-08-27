from threading import Lock
from backend.schemas import DocsPathsCreateSchema
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
from typing import List
from starlette.datastructures import UploadFile
from uuid import uuid4
from backend.models import File
from backend.db import db_session_context
from sqlalchemy import delete

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

    async def create_index(self, resource_id: str, path_files: List[str]) -> str:

        all_docs = []
        all_ids = []

        for path in path_files:
            loader = PyPDFLoader(path)
            docs = loader.load()  
            all_docs.append(docs[0])
            file_id = str(uuid4())
            all_ids.append(file_id)

        print(f"all_ids = {all_ids}")
        await self.create_files_for_resource(resource_id, path_files, all_ids)
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )

        splits=text_splitter.split_documents(all_docs)                      
        path = Path(chroma_db_path)

        vectorstore = await self.initialize_chroma(resource_id)
        print(f"splits.len = {len(all_docs)}")
        vectorstore.add_documents(documents=all_docs, ids=all_ids)
        return resource_id
       
    async def create_files_for_resource(self, resource_id: str, files: List[str], ids: List[str]):
        for file_name, file_id in zip(files, ids):
            await self.create_file(file_name, resource_id, file_id)
    
    async def create_file(self, file_name: str, assistant_id: str, file_id: str):        
        async with db_session_context() as session:
            new_file = File(id=file_id, name=file_name, assistant_id=assistant_id)
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
        embed = OllamaEmbeddings(model="llama3")
        
        path = Path(chroma_db_path)
        vectorstore = Chroma(persist_directory=str(path),
                             collection_name=collection_name,
                             embedding_function=embed)
        return vectorstore
    
    
    async def retrive_and_generate(self, collection_name, query, llm) -> str:
        system_prompt = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer "
            "the question. If you don't know the answer, say that you "
            "don't know. Use three sentences maximum and keep the "
            "answer concise."
            "\n\n"
            "{context}"
        )
    
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
    
    
    async def upload_file(self, resource_id: str, files: List[UploadFile]) -> str:
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

            await self.create_index(resource_id, all_docs)   
            return "Files uploaded"
        except Exception as e:
            print(f"An error occurred while uploading files: {e}")
            return "File upload failed"