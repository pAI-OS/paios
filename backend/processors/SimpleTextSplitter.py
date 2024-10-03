from typing import List
from backend.processors.BaseProcessor import BaseProcessor

class SimpleTextSplitter(BaseProcessor):
    def is_available(self) -> bool:
        return True

    async def process(self, content: str) -> List[str]:
        return [content[i:i+1000] for i in range(0, len(content), 1000)]
