from typing import Any
from abc import ABC, abstractmethod

class BaseProcessor(ABC):
    @abstractmethod
    def is_available(self) -> bool:
        """Check if the processor is available (dependencies installed)."""
        pass

    @abstractmethod
    async def process(self, content: str) -> Any:
        """Process the content."""
        pass
