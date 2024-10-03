from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func, or_
from backend.models import Collection
from backend.schemas import CollectionCreate  # Import from schemas.py
from backend.db import db_session_context
from backend.processors.BaseProcessor import BaseProcessor
from backend.processors.SimpleTextSplitter import SimpleTextSplitter
from backend.processors.SimpleEmbedder import SimpleEmbedder
from backend.processors.SimpleVectorStore import SimpleVectorStore
from typing import List, Tuple, Optional, Dict, Any

class CollectionsManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(CollectionsManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._initialized = True
                    self._load_processors()

    def _load_processors(self):
        self.text_splitters = [SimpleTextSplitter()]
        self.embedders = [SimpleEmbedder()]
        self.vector_stores = [SimpleVectorStore()]

        # Load additional processors if available
        try:
            from backend.processors.LangchainTextSplitter import LangchainTextSplitter
            self.text_splitters.append(LangchainTextSplitter())
        except ImportError:
            pass

        try:
            from backend.processors.OpenAIEmbedder import OpenAIEmbedder
            self.embedders.append(OpenAIEmbedder())
        except ImportError:
            pass

        try:
            from backend.processors.ChromaVectorStore import ChromaVectorStore
            self.vector_stores.append(ChromaVectorStore())
        except ImportError:
            pass

    async def create_collection(self, collection_data: CollectionCreate) -> Collection:
        async with db_session_context() as session:
            new_collection = Collection(**collection_data.dict())
            session.add(new_collection)
            await session.commit()
            await session.refresh(new_collection)
            return new_collection

    async def process_collection(self, collection_id: str, text_splitter: str, embedder: str, vector_store: str):
        collection = await self.retrieve_collection(collection_id)
        if not collection:
            raise ValueError(f"Collection with id {collection_id} not found")

        text_splitter = next((ts for ts in self.text_splitters if ts.__class__.__name__ == text_splitter), None)
        embedder = next((emb for emb in self.embedders if emb.__class__.__name__ == embedder), None)
        vector_store = next((vs for vs in self.vector_stores if vs.__class__.__name__ == vector_store), None)

        if not all([text_splitter, embedder, vector_store]):
            raise ValueError("Invalid processor selection")

        await self._process_collection(collection, text_splitter, embedder, vector_store)

    async def _process_collection(self, collection: Collection, text_splitter: BaseProcessor, embedder: BaseProcessor, vector_store: BaseProcessor):
        # Implement a method to process collections
        # This could involve streaming data from an external source, like an email server
        for batch in self._collection_batch_generator(collection):
            chunks = await text_splitter.process(batch)
            embeddings = await embedder.process(chunks)
            await vector_store.process(f"{collection.id}_{uuid4()}", chunks, embeddings)

    def _collection_batch_generator(self, collection: Collection):
        # This is a dummy generator. In a real scenario, this would fetch data from the actual source
        for i in range(10):  # Simulate 10 batches
            yield f"This is batch {i} of collection {collection.name}"

    async def retrieve_collection(self, id: str) -> Optional[Collection]:
        async with db_session_context() as session:
            result = await session.execute(select(Collection).filter(Collection.id == id))
            collection = result.scalar_one_or_none()
            return Collection.from_orm(collection) if collection else None

    async def update_collection(self, id: str, collection_data: CollectionCreate) -> Optional[Collection]:
        async with db_session_context() as session:
            stmt = update(Collection).where(Collection.id == id).values(**collection_data.model_dump(exclude_unset=True))
            result = await session.execute(stmt)
            if result.rowcount > 0:
                await session.commit()
                updated_collection = await session.get(Collection, id)
                return Collection.from_orm(updated_collection)
            return None

    async def delete_collection(self, id: str) -> bool:
        async with db_session_context() as session:
            stmt = delete(Collection).where(Collection.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def list_collections(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None, 
                               sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None, 
                               query: Optional[str] = None) -> Tuple[List[Collection], int]:
        async with db_session_context() as session:
            stmt = select(Collection)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        stmt = stmt.filter(getattr(Collection, key).in_(value))
                    else:
                        stmt = stmt.filter(getattr(Collection, key) == value)

            if query:
                search_condition = or_(
                    Collection.name.ilike(f"%{query}%"),
                    Collection.description.ilike(f"%{query}%")
                )
                stmt = stmt.filter(search_condition)

            if sort_by and hasattr(Collection, sort_by):
                order_column = getattr(Collection, sort_by)
                stmt = stmt.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            total_count = await session.execute(select(func.count()).select_from(stmt.subquery()))
            total_count = total_count.scalar_one()

            stmt = stmt.offset(offset).limit(limit)
            result = await session.execute(stmt)
            collections = [Collection.from_orm(c) for c in result.scalars().all()]

            return collections, total_count

    async def search_collection(self, collection_id: str, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        collection = await self.retrieve_collection(collection_id)
        if not collection:
            raise ValueError(f"Collection with id {collection_id} not found")

        # Implement vector search here
        # This is a simplified example
        # results = vector_store.search(collection_id, query, limit)
        # return [{"content": result.content, "metadata": result.metadata} for result in results]
        return []  # Placeholder

    def get_available_processors(self):
        return {
            "text_splitters": [ts.__class__.__name__ for ts in self.text_splitters if ts.is_available()],
            "embedders": [emb.__class__.__name__ for emb in self.embedders if emb.is_available()],
            "vector_stores": [vs.__class__.__name__ for vs in self.vector_stores if vs.is_available()]
        }
