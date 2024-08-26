from threading import Lock
from backend.schemas import DocsPathsCreateSchema
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings
from common.paths import chroma_db_path
from pathlib import Path
import os
from langchain_core.prompts import ChatPromptTemplate
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain

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

    async def create_index(self, resource_id: str, docs_paths_data: DocsPathsCreateSchema) -> str: 
        
        all_docs = []
        
        for path in docs_paths_data["docs_paths"]:
            loader = PyPDFLoader(path)
            docs = loader.load()    
            all_docs.extend(docs) 


        #ToDo: Make chunk_size and chunk_overlap configurable
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )
        
        splits=text_splitter.split_documents(all_docs)                      
        path = Path(chroma_db_path)

        vectorstore = await self.initialize_chroma(resource_id)
        vectorstore.add_documents(splits)

        return resource_id
       
    
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
    
    