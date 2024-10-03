import random
from typing import List
from backend.processors.BaseProcessor import BaseProcessor

class SimpleEmbedder(BaseProcessor):
    def is_available(self) -> bool:
        return True

    async def process(self, chunks: List[str]) -> List[List[float]]:
        return [[random.random() for _ in range(100)] for _ in chunks]
