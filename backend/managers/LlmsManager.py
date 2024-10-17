import asyncio
import httpx
from threading import Lock
from sqlalchemy import select, insert, update, delete, func
from backend.models import Llm
from backend.db import db_session_context
from backend.schemas import LlmSchema
from backend.utils import get_env_key
from typing import List, Tuple, Optional, Dict, Any, Union
from litellm import Router
from litellm.utils import CustomStreamWrapper, ModelResponse

import logging
logger = logging.getLogger(__name__)

class LlmsManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(LlmsManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):  # Ensure initialization happens only once
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self.router = None
                    router_init_task = asyncio.create_task(self._init_router())
                    asyncio.gather(router_init_task, return_exceptions=True)
                    self._initialized = True

    async def _init_router(self):
        try:
            # load models
            ollama_task = asyncio.create_task(self._load_ollama_models())
            await asyncio.gather(ollama_task, return_exceptions=True)
            # collect the available LLMs
            llms, total_llms = await self.retrieve_llms()
            # configure router
            model_list = []
            for llm in llms:
                params = {}
                params["model"] = llm.llm_name
                if llm.provider == "ollama":
                    params["api_base"] = llm.api_base
                model = {
                    "model_name": llm.llm_name,
                    "litellm_params": params,
                }
                model_list.append(model)
            print(model_list)
            self.router = Router(model_list=model_list)
        except Exception as e:
            logger.exception(e)

    async def _load_ollama_models(self):
        try:
            ollama_urlroot = get_env_key("OLLAMA_URLROOT")  # eg: http://localhost:11434
        except ValueError:
            return  # no Ollama server specified
        # retrieve list of installed models
        async with httpx.AsyncClient() as client:
            response = await client.get("{}/api/tags".format(ollama_urlroot))
            if response.status_code == 200:
                data = response.json()
                available_models = [model_data['model'] for model_data in data.get("models", [])]
                print(available_models)      
            else:
                pass # FIX
        # create / update Ollama family Llm objects
        provider = "ollama"
        async with db_session_context() as session:
            # mark existing models as inactive
            stmt = update(Llm).where(Llm.provider == provider).values(is_active=False)
            result = await session.execute(stmt)
            if result.rowcount > 0:
                await session.commit()
            # insert / update models
            for model in available_models:
                name = model.removesuffix(":latest")
                llm_name = "{}/{}".format(provider,name)  # what LiteLLM expects
                safe_name = llm_name.replace("/", "-").replace(":", "-")
                result = await session.execute(select(Llm).filter(Llm.id == safe_name))
                llm = result.scalar_one_or_none()
                if llm:
                    stmt = update(Llm).where(Llm.id == safe_name).values(name=name,
                                                                         llm_name=llm_name,
                                                                         provider=provider,
                                                                         api_base=ollama_urlroot,
                                                                         is_active=True)
                    result = await session.execute(stmt)
                    if result.rowcount > 0:
                        await session.commit()
                else:
                    new_llm = Llm(id=safe_name, name=name, llm_name=llm_name,
                                  provider=provider, api_base=ollama_urlroot,
                                  is_active=True)
                    session.add(new_llm)
                    await session.commit()

    async def get_llm(self, id: str) -> Optional[LlmSchema]:
        async with db_session_context() as session:
            result = await session.execute(select(Llm).filter(Llm.id == id))
            llm = result.scalar_one_or_none()
            if llm:
                return LlmSchema(id=llm.id, name=llm.name, llm_name=llm.llm_name,
                                 provider=llm.provider, api_base=llm.api_base, is_active=llm.is_active)
            return None

    async def retrieve_llms(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None,
                            sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None) -> Tuple[List[LlmSchema], int]:
        async with db_session_context() as session:
            query = select(Llm).filter(Llm.is_active == True)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.filter(getattr(Llm, key).in_(value))
                    else:
                        query = query.filter(getattr(Llm, key) == value)

            if sort_by and sort_by in ['id', 'name', 'llm_name', 'provider', 'api_base', 'is_active']:
                order_column = getattr(Llm, sort_by)
                query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            llms = [LlmSchema(id=llm.id, name=llm.name, llm_name=llm.llm_name,
                              provider=llm.provider, api_base=llm.api_base,
                              is_active=llm.is_active) 
                        for llm in result.scalars().all()]

            # Get total count
            count_query = select(func.count()).select_from(Llm).filter(Llm.is_active == True)
            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        count_query = count_query.filter(getattr(Llm, key).in_(value))
                    else:
                        count_query = count_query.filter(getattr(Llm, key) == value)

            total_count = await session.execute(count_query)
            total_count = total_count.scalar()

            return llms, total_count

    def completion(self, llm, messages, **optional_params) -> Union[ModelResponse, CustomStreamWrapper]:
        response = self.router.completion(model=llm.llm_name,
                                          messages=messages,
                                          kwargs=optional_params)
        print("completion response: {}".format(response))
        #message = response.choices[0].message.content
        #return message
        return response

    async def acompletion(self, llm, messages, **optional_params) -> Union[CustomStreamWrapper, ModelResponse]:
        response = await self.router.acompletion(model=llm.llm_name,
                                                 messages=messages,
                                                 kwargs=optional_params)
        print("acompletion response: {}".format(response))
        return response
    