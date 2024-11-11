from langchain_text_splitters import RecursiveCharacterTextSplitter

from typing import List, Optional
from backend.processors.text_splitters import BaseProcessorTextSplitter
from langchain_core.documents import BaseDocumentTransformer, Document


class RecursiveCharacterTextSplitter(BaseProcessorTextSplitter):

    def __init__(self):
        self.text_splitter = RecursiveCharacterTextSplitter(
            # Set a really small chunk size, just to show.
            chunk_size=100,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )

    def is_available(self) -> bool:
        return True


    def split_documents(
            self, texts: List[str]
    ) -> List[Document]:
        return self.text_splitter.create_documents(
            texts
        )

    def split_text(self, text: str) -> List[str]:
        return self.text_splitter.split_text(text)

    # TODO implement other methods
