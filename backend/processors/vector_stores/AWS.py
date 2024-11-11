from typing import List, Optional, Dict, Union, Type

import numpy as np

from backend.processors.vector_stores import BaseProcessorVectorStore
from langchain_core.documents import Document

from langchain_aws.vectorstores import InMemoryVectorStore

from langchain_aws.vectorstores.inmemorydb.filters import InMemoryDBFilterExpression
from langchain_aws.utilities.math import cosine_similarity
from langchain_core.embeddings.embeddings import Embeddings


class AWS(BaseProcessorVectorStore):
    def __init__(self, documents, embeddings, redis="redis://cluster_endpoint:6379"):
        self.aws = InMemoryVectorStore.from_documents(
            documents,  # a list of Document objects from loaders or created
            embeddings,  # an Embeddings object
            redis_url=redis,
        )

    def is_available(self) -> bool:
        return True

    # returns list of ids of added docs
    def add_document(self, documents):
        return self.aws.add_documents(documents=documents)

    def search(
            self,
            query: str,
            k: int = 4,
            filter: Optional[InMemoryDBFilterExpression] = None,
            return_metadata: bool = True,
            distance_threshold: Optional[float] = None
    ) -> List[Document]:
        """Run similarity search with AWS."""
        return self.aws.similarity_search(query, k)

    def from_texts(self,
                   #cls: Type[InMemoryVectorStore],
                   texts: List[str],
                   embedding: Embeddings,
                   metadatas: Optional[List[dict]] = None,
                   index_name: Optional[str] = None,
                   # index_schema: Optional[Union[Dict[str, ListOfDict], str, os.PathLike]] = None,
                   # vector_schema: Optional[Dict[str, Union[str, int]]] = None,
                   # **kwargs: Any,
                   ) -> InMemoryVectorStore:
        return self.aws.from_texts(texts, embedding)

    def cosine_similarity(self, b: np.array(), a: np.array()):
        return cosine_similarity(a, b)

    # TODO implement other methods
