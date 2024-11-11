from typing import Any, List
from abc import ABC, abstractmethod

class BaseProcessorEmbeddings(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the processor is available (dependencies installed)."""
        pass

    @abstractmethod
    def embed_query(self, text: str) -> List[float]:
        pass

    @abstractmethod
    def embed_documents(
            self, texts: List[str], chunk_size: int
    ) -> List[List[float]]:
        pass
