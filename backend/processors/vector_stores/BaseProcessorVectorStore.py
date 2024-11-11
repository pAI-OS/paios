from typing import Any
from abc import ABC, abstractmethod
from langchain_core.documents import Document

from langchain_aws.vectorstores import InMemoryVectorStore

from langchain_aws.vectorstores.inmemorydb.filters import InMemoryDBFilterExpression
class BaseProcessorVectorStore(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the processor is available (dependencies installed)."""
        pass

    @abstractmethod
    # returns list of ids of added docs
    def add_document(self, documents):
        pass

    @abstractmethod
    def similarity_search(
            self,
            query: str,
            k: int = 4,
            filter: Optional[InMemoryDBFilterExpression] = None,
            return_metadata: bool = True,
            distance_threshold: Optional[float] = None
    ) -> List[Document]:
        """Run similarity search with AWS."""
        pass

    @abstractmethod
    def cosine_similarity(self, b: np.array(), a: np.array()):
        pass
