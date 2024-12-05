import asyncio
import httpx
from threading import Lock
from sqlalchemy import select, insert, update, delete, func
from backend.models import Llm
from backend.db import db_session_context
from backend.utils import get_env_key
from typing import List, Tuple, Optional, Dict, Any, Union
from litellm import Router, completion
from litellm.utils import CustomStreamWrapper, ModelResponse

import logging
logger = logging.getLogger(__name__)

class ModelsManager:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(ModelsManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):  # Ensure initialization happens only once
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self.router = None
                    router_init_task = asyncio.create_task(self._init_router())
                    asyncio.gather(router_init_task, return_exceptions=True)
                    self._initialized = True

    async def get_llm(self, id: str) -> Optional[Llm]:
        async with db_session_context() as session:
            result = await session.execute(select(Llm).filter(Llm.id == id))
            llm = result.scalar_one_or_none()
            if llm:
                return llm
            return None

    async def retrieve_llms(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None,
                            sort_order: str = 'asc', filters: Optional[Dict[str, Any]] = None) -> Tuple[List[Llm], int]:
        async with db_session_context() as session:
            query = select(Llm).filter(Llm.is_active == True)

            if filters:
                for key, value in filters.items():
                    if isinstance(value, list):
                        query = query.filter(getattr(Llm, key).in_(value))
                    else:
                        query = query.filter(getattr(Llm, key) == value)

            if sort_by and sort_by in ['id', 'name', 'provider', 'api_base', 'is_active']:
                order_column = getattr(Llm, sort_by)
                query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

            query = query.offset(offset).limit(limit)

            result = await session.execute(query)
            llms = result.scalars().all()

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
        try:
            response = self.router.completion(model=llm.llm_name,
                                              messages=messages,
                                              **optional_params)
            # below is the direct way to call the model (i.e. not using the router):
            #response = completion(model=llm.llm_name,
            #                      messages=messages,
            #                      **optional_params)
            print("completion response: {}".format(response))
            return response
        except Exception as e:
            logger.info(f"completion failed with error: {e.message}")
            raise

    async def _init_router(self):
        try:
            # load models
            ollama_task = asyncio.create_task(self._load_ollama_models())
            openai_task = asyncio.create_task(self._load_openai_models())
            await asyncio.gather(ollama_task,
                                 openai_task,
                                 return_exceptions=True)
            # collect the available models
            llms, total_llms = await self.retrieve_llms()
            # configure router
            model_list = []
            for llm in llms:
                model_name = f"{llm.provider}/{llm.name}"
                params = {}
                params["model"] = llm.llm_name
                if llm.provider == "ollama":
                    params["api_base"] = llm.api_base
                if llm.provider == "openai":
                    params["api_key"] = get_env_key("OPENAI_API_KEY")
                model = {
                    "model_name": model_name,
                    "litellm_params": params,
                }
                model_list.append(model)
            #import pprint
            #pprint.pprint(model_list)
            self.router = Router(model_list=model_list)
        except Exception as e:
            logger.exception(e)

    async def _load_ollama_models(self):
        try:
            ollama_urlroot = get_env_key("OLLAMA_URLROOT")
        except ValueError:
            print("No Ollama server specified.  Skipping.")
            return  # no Ollama server specified, skip
        # retrieve list of installed models
        async with httpx.AsyncClient() as client:
            response = await client.get("{}/api/tags".format(ollama_urlroot))
            if response.status_code == 200:
                data = response.json()
                available_models = [model_data['model'] for model_data in data.get("models", [])]
            else:
                print(f"Error: {response.status_code} - {response.text}")
        # create / update Ollama family Llm objects
        provider = "ollama"
        models = {}
        for model in available_models:
            name = model.removesuffix(":latest")
            llm_name = "{}/{}".format(provider,name)  # what LiteLLM expects
            safe_name = llm_name.replace("/", "-").replace(":", "-")  # URL-friendly ID
            models[model] = {"id": safe_name, "name": name, "llm_name": llm_name, "provider": provider, "api_base": ollama_urlroot}
        await self._persist_models(provider=provider, models=models)

    async def _load_openai_models(self):
        try:
            openai_key = get_env_key("OPENAI_API_KEY")
        except ValueError:
            print("No OpenAI API key specified.  Skipping.")
            return  # no OpenAI API key specified, skip
        # retrieve list of installed models
        async with httpx.AsyncClient() as client:
            openai_urlroot = get_env_key("OPENAI_URLROOT", "https://api.openai.com")
            headers = {
                "Authorization": f"Bearer {openai_key}"
            }
            response = await client.get(f"{openai_urlroot}/v1/models", headers=headers)
            if response.status_code == 200:
                data = response.json()
                available_models = [model_data['id'] for model_data in data.get("data", [])]
            else:
                print(f"Error: {response.status_code} - {response.text}")
        # create / update OpenAI family Llm objects
        provider = "openai"
        models = {}
        for model in available_models:
            llm_provider = None
            if any(substring in model for substring in {"gpt","o1","chatgpt"}):
                llm_provider = "openai"
            if any(substring in model for substring in {"ada","babbage","curie","davinci","instruct"}):
                llm_provider = "text-completion-openai"
            if llm_provider:
                name = model
                llm_name = "{}/{}".format(llm_provider,name)  # what LiteLLM expects
                safe_name = f"{provider}/{name}".replace("/", "-").replace(":", "-")  # URL-friendly ID
            models[model] = {"id": safe_name, "name": name, "llm_name": llm_name, "provider": provider, "api_base": openai_urlroot}
        await self._persist_models(provider=provider, models=models)

    async def _persist_models(self, provider, models):
        async with db_session_context() as session:
            # mark existing models as inactive
            stmt = update(Llm).where(Llm.provider == provider).values(is_active=False)
            result = await session.execute(stmt)
            if result.rowcount > 0:
                await session.commit()
            # insert / update models
            for model in models:
                parameters = models[model]
                model_id = parameters["id"]
                llm = await self.get_llm(model_id)
                if llm:
                    stmt = update(Llm).where(Llm.id == model_id).values(name=parameters["name"],
                                                                        llm_name=parameters["llm_name"],
                                                                        provider=parameters["provider"],
                                                                        api_base=parameters["api_base"],
                                                                        is_active=True)
                    result = await session.execute(stmt)
                    if result.rowcount > 0:
                        await session.commit()
                else:
                    new_llm = Llm(id=model_id,
                                  name=parameters["name"],
                                  llm_name=parameters["llm_name"],
                                  provider=parameters["provider"],
                                  api_base=parameters["api_base"],
                                  is_active=True)
                    session.add(new_llm)
                    await session.commit()

