from threading import Lock
from backend.schemas import DocsPathsCreateSchema
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_openai import OpenAIEmbeddings
from common.paths import chroma_db_path
from pathlib import Path
import os

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

    async def create_index(self, channel_id: str, docs_paths_data: DocsPathsCreateSchema) -> str: 
        
        all_docs = []
        
        for path in docs_paths_data["docs_paths"]:
            loader = PyPDFLoader(path)
            docs = loader.load()    
            all_docs.extend(docs) 


        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000, chunk_overlap=200, add_start_index=True
        )
        
        splits=text_splitter.split_documents(all_docs)                      
        path = Path(chroma_db_path)

        os.environ.get('OPENAI_API_KEY')        

        if not os.path.exists(path): 
            vectorstore = Chroma.from_documents(documents=splits, 
                                    embedding=OpenAIEmbeddings(),
                                    persist_directory=str(path),
                                    collection_name = channel_id,
                                    )
            print(vectorstore)
        else:
            vectorstore = Chroma(persist_directory=str(path),embedding_function=OpenAIEmbeddings())
            vectorstore.add_documents(splits, collection_name=channel_id)
        return channel_id