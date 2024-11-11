from typing import Any, List, Optional
from abc import ABC, abstractmethod
from langchain_core.documents import BaseDocumentTransformer, Document
class BaseProcessorTextSplitter(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the processor is available (dependencies installed)."""
        pass

    @abstractmethod
    def split_documents(
            self, texts: List[str], metadatas: Optional[List[dict]]
    ) -> List[Document]:
        pass

    @abstractmethod
    def split_text(self, text: str) -> List[str]:
        pass
