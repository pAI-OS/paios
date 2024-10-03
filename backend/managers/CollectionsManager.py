from uuid import uuid4
from threading import Lock
from sqlalchemy import select, insert, update, delete, func, or_
from backend.models import Asset, AssetCollection
from backend.db import db_session_context
from backend.schemas import AssetSchema, AssetCreateSchema, AssetCollectionSchema, AssetCollectionCreateSchema
from typing import List, Tuple, Optional, Dict, Any
from backend.processors.BaseProcessor import BaseProcessor
from backend.processors.SimpleTextSplitter import SimpleTextSplitter
from backend.processors.SimpleEmbedder import SimpleEmbedder
from backend.processors.SimpleVectorStore import SimpleVectorStore

class AssetsManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AssetsManager, cls).__new__(cls, *args, **kwargs)
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

    async def create_asset_collection(self, collection_data: AssetCollectionCreateSchema) -> AssetCollectionSchema:
        async with db_session_context() as session:
            new_collection = AssetCollection(id=str(uuid4()), **collection_data.model_dump())
            session.add(new_collection)
            await session.commit()
            await session.refresh(new_collection)
            return AssetCollectionSchema.from_orm(new_collection)

    async def process_asset_collection(self, collection_id: str, text_splitter: str, embedder: str, vector_store: str):
        collection = await self.retrieve_asset_collection(collection_id)
        if not collection:
            raise ValueError(f"Asset collection with id {collection_id} not found")

        text_splitter = next((ts for ts in self.text_splitters if ts.__class__.__name__ == text_splitter), None)
        embedder = next((emb for emb in self.embedders if emb.__class__.__name__ == embedder), None)
        vector_store = next((vs for vs in self.vector_stores if vs.__class__.__name__ == vector_store), None)

        if not all([text_splitter, embedder, vector_store]):
            raise ValueError("Invalid processor selection")

        if collection.track_individual_assets:
            assets = await self.retrieve_assets(filters={"collection_id": collection_id})
            for asset in assets:
                await self._process_asset(asset, text_splitter, embedder, vector_store)
        else:
            await self._process_large_collection(collection, text_splitter, embedder, vector_store)

    async def _process_asset(self, asset: Asset, text_splitter: BaseProcessor, embedder: BaseProcessor, vector_store: BaseProcessor):
        chunks = await text_splitter.process(asset.content)
        embeddings = await embedder.process(chunks)
        await vector_store.process(asset.id, chunks, embeddings)

    async def _process_large_collection(self, collection: AssetCollection, text_splitter: BaseProcessor, embedder: BaseProcessor, vector_store: BaseProcessor):
        # Implement a method to process large collections in batches
        # This could involve streaming data from an external source, like an email server
        # For demonstration, we'll use a dummy generator
        for batch in self._large_collection_batch_generator(collection):
            chunks = await text_splitter.process(batch)
            embeddings = await embedder.process(chunks)
            await vector_store.process(f"{collection.id}_{uuid4()}", chunks, embeddings)

    def _large_collection_batch_generator(self, collection: AssetCollection):
        # This is a dummy generator. In a real scenario, this would fetch data from the actual source
        for i in range(10):  # Simulate 10 batches
            yield f"This is batch {i} of collection {collection.name}"

    async def retrieve_asset_collection(self, id: str) -> Optional[AssetCollectionSchema]:
        async with db_session_context() as session:
            result = await session.execute(select(AssetCollection).filter(AssetCollection.id == id))
            collection = result.scalar_one_or_none()
            if collection:
                return AssetCollectionSchema(
                    id=collection.id,
                    name=collection.name,
                    description=collection.description
                )
            return None

    async def retrieve_asset_collections(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None, 
                                         sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None, 
                                         query: Optional[str] = None) -> Tuple[List[AssetCollectionSchema], int]:
        async with db_session_context() as session:
            stmt = select(AssetCollection)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        stmt = stmt.filter(getattr(AssetCollection, key).in_(value))
                    else:
                        stmt = stmt.filter(getattr(AssetCollection, key) == value)

            if query:
                search_condition = or_(
                    AssetCollection.name.ilike(f"%{query}%"),
                    AssetCollection.description.ilike(f"%{query}%")
                )
                stmt = stmt.filter(search_condition)

            if sort_by and hasattr(AssetCollection, sort_by):
                order_column = getattr(AssetCollection, sort_by)
                stmt = stmt.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            stmt = stmt.offset(offset).limit(limit)

            result = await session.execute(stmt)
            collections = [AssetCollectionSchema(
                id=collection.id,
                name=collection.name,
                description=collection.description
            ) for collection in result.scalars().all()]

            # Get total count
            count_stmt = select(func.count()).select_from(AssetCollection)
            if filters or query:
                count_stmt = count_stmt.filter(stmt.whereclause)
            total_count = await session.execute(count_stmt)
            total_count = total_count.scalar()

            return collections, total_count

    async def create_asset(self, asset_data: AssetCreateSchema) -> AssetSchema:
        collection = await self.retrieve_asset_collection(asset_data.collection_id)
        if not collection.track_individual_assets:
            raise ValueError("This collection does not track individual assets")
        
        async with db_session_context() as session:
            new_asset = Asset(id=str(uuid4()), **asset_data.model_dump())
            session.add(new_asset)
            await session.commit()
            await session.refresh(new_asset)
            return AssetSchema.from_orm(new_asset)

    async def update_asset(self, id: str, asset_data: AssetCreateSchema) -> Optional[AssetSchema]:
        async with db_session_context() as session:
            stmt = update(Asset).where(Asset.id == id).values(**asset_data.model_dump(exclude_unset=True))
            result = await session.execute(stmt)
            if result.rowcount > 0:
                await session.commit()
                updated_asset = await session.get(Asset, id)
                return AssetSchema(id=updated_asset.id, **asset_data.model_dump())
            return None

    async def delete_asset(self, id: str) -> bool:
        async with db_session_context() as session:
            stmt = delete(Asset).where(Asset.id == id)
            result = await session.execute(stmt)
            await session.commit()
            return result.rowcount > 0

    async def retrieve_asset(self, id: str) -> Optional[AssetSchema]:
        async with db_session_context() as session:
            result = await session.execute(select(Asset).filter(Asset.id == id))
            asset = result.scalar_one_or_none()
            if asset:
                return AssetSchema(
                    id=asset.id,
                    title=asset.title,
                    user_id=asset.user_id,
                    creator=asset.creator,
                    subject=asset.subject,
                    description=asset.description
                )
            return None

    async def retrieve_assets(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None, 
                              sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None, 
                              query: Optional[str] = None) -> Tuple[List[AssetSchema], int]:
        async with db_session_context() as session:
            stmt = select(Asset)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        stmt = stmt.filter(getattr(Asset, key).in_(value))
                    else:
                        stmt = stmt.filter(getattr(Asset, key) == value)

            if query:
                search_condition = or_(
                    Asset.title.ilike(f"%{query}%"),
                    Asset.description.ilike(f"%{query}%"),
                    Asset.creator.ilike(f"%{query}%"),
                    Asset.subject.ilike(f"%{query}%")
                )
                stmt = stmt.filter(search_condition)

            if sort_by and hasattr(Asset, sort_by):
                order_column = getattr(Asset, sort_by)
                stmt = stmt.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            # Add a join to check if the collection tracks individual assets
            stmt = stmt.join(AssetCollection).filter(AssetCollection.track_individual_assets == True)

            stmt = stmt.offset(offset).limit(limit)

            result = await session.execute(stmt)
            assets = [AssetSchema.from_orm(asset) for asset in result.scalars().all()]

            # Get total count
            count_stmt = select(func.count()).select_from(Asset).join(AssetCollection).filter(AssetCollection.track_individual_assets == True)
            if filters or query:
                count_stmt = count_stmt.filter(stmt.whereclause)
            total_count = await session.execute(count_stmt)
            total_count = total_count.scalar()

            return assets, total_count

    def get_available_processors(self):
        return {
            "text_splitters": [ts.__class__.__name__ for ts in self.text_splitters if ts.is_available()],
            "embedders": [emb.__class__.__name__ for emb in self.embedders if emb.is_available()],
            "vector_stores": [vs.__class__.__name__ for vs in self.vector_stores if vs.is_available()]
        }