from typing import List

from backend.processors.embedders import BaseProcessorEmbeddings
from langchain_ollama import OllamaEmbeddings


class OllamaEmbeddings(BaseProcessorEmbeddings):
    def __init__(self, model_name="llama3"):
        self.embed = OllamaEmbeddings(
            model=model_name
        )

    def is_available(self) -> bool:
        return True


    def embed_query(self, text: str) -> List[float]:
        return self.embed.embed_query(text)

    def embed_documents(
            self, texts: List[str]
    ) -> List[List[float]]:
        return self.embed.embed_documents(texts)

    # TODO implement other methods
