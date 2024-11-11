import random
from typing import List
from backend.processors.embedders import BaseProcessorEmbeddings
from langchain_openai import OpenAIEmbeddings

class OpenAIEmbeddings(BaseProcessorEmbeddings):
    def __init__(self,model_name="text-embedding-3-large"):
        self.embed = OpenAIEmbeddings(
            model=model_name
            # With the `text-embedding-3` class
            # of models, you can specify the size
            # of the embeddings you want returned.
            # dimensions=1024
        )

    def is_available(self) -> bool:
        return True


    def embed_query(self, text: str) -> List[float]:
        return self.embed.embed_query(text)

    def embed_documents(
            self, texts: List[str], chunk_size: int
    ) -> List[List[float]]:
        return self.embed.embed_documents(texts,chunk_size)

    # TODO implement other methods

