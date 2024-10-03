from typing import List
from backend.processors.BaseProcessor import BaseProcessor

class SimpleVectorStore(BaseProcessor):
    def __init__(self):
        self.store = {}

    def is_available(self) -> bool:
        return True

    async def process(self, collection_id: str, chunks: List[str], embeddings: List[List[float]]):
        self.store[collection_id] = list(zip(chunks, embeddings))

    async def search(self, collection_id: str, query_embedding: List[float], limit: int = 10) -> List[str]:
        if collection_id not in self.store:
            return []
        
        # Simple cosine similarity search
        def cosine_similarity(a, b):
            return sum(x*y for x, y in zip(a, b)) / (sum(x*x for x in a)**0.5 * sum(y*y for y in b)**0.5)
        
        similarities = [(chunk, cosine_similarity(embedding, query_embedding)) 
                        for chunk, embedding in self.store[collection_id]]
        
        return [chunk for chunk, _ in sorted(similarities, key=lambda x: x[1], reverse=True)[:limit]]
