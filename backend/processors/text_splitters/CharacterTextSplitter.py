from typing import List, Optional
from backend.processors.text_splitters import BaseProcessorTextSplitter
from langchain_text_splitters import CharacterTextSplitter
from langchain_core.documents import BaseDocumentTransformer, Document


class CharacterTextSplitter(BaseProcessorTextSplitter):

    def __init__(self):
        self.text_splitter = CharacterTextSplitter(
            separator="\n\n",
            chunk_size=1000,
            chunk_overlap=200,
            length_function=len,
            is_separator_regex=False,
        )

    def is_available(self) -> bool:
        return True


    def split_documents(
            self, texts: List[str], metadatas: Optional[List[dict]]
    ) -> List[Document]:
        return self.text_splitter.create_documents(
            texts, metadatas=metadatas
        )

    def split_text(self, text: str) -> List[str]:
        return self.text_splitter.split_text(text)

    # TODO implement other methods
