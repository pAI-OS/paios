from typing import List, Optional, Dict, Type

import numpy as np

from backend.processors.vector_stores import BaseProcessorVectorStore
from langchain_core.documents import Document

from langchain_chroma import Chroma
from langchain_chroma.vectorstores import cosine_similarity
from langchain_core.embeddings.embeddings import Embeddings


class Chroma(BaseProcessorVectorStore):
    _LANGCHAIN_DEFAULT_COLLECTION_NAME = "langchain"
    def __init__(self, collection_name, embeddings, persist_dir="./chroma_langchain_db"):
        self.vector_store = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=persist_dir  # Where to save data locally, remove if not necessary
        )

    def is_available(self) -> bool:
        return True

    # returns list of ids of added docs
    def add_document(self, documents):
        return self.vector_store.add_documents(documents=documents)

    def from_texts(self,
                   #cls: Type[Chroma],
                   texts: List[str],
                   embedding: Optional[Embeddings] = None,
                   metadatas: Optional[List[dict]] = None,
                   ids: Optional[List[str]] = None,
                   collection_name: str = _LANGCHAIN_DEFAULT_COLLECTION_NAME,
                   # persist_directory: Optional[str] = None,
                   # client_settings: Optional[chromadb.config.Settings] = None,
                   # client: Optional[chromadb.ClientAPI] = None,
                   # collection_metadata: Optional[Dict] = None,
                   # ** kwargs: Any,
                   ) -> Chroma:
        return self.vector_store.from_texts(texts, embedding)

    def search(
            self,
            query: str,
            k: int = 1,
            filter: Optional[Dict[str, str]] = None
    ) -> List[Document]:
        """Run similarity search with Chroma."""
        return self.vector_store.similarity_search(query, k)

    def cosine_similarity(self, b: np.array(), a: np.array()):
        return cosine_similarity(a, b)

    # TODO implement other methods
