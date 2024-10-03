from typing import List
from backend.processors.BaseProcessor import BaseProcessor

class SimpleVectorStore(BaseProcessor):
    def __init__(self):
        self.store = {}

    def is_available(self) -> bool:
        return True

    async def process(self, asset_id: str, chunks: List[str], embeddings: List[List[float]]):
        self.store[asset_id] = list(zip(chunks, embeddings))
