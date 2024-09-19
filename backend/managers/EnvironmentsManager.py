import os
from sqlmodel import select
from backend.models import Environment
from backend.db import db_session_context
from common.constants import DEFAULT_ENVIRONMENT
from common.paths import envs_dir

class EnvironmentsManager:
    def __init__(self):
        self.ensure_default_environment_directory()

    def ensure_default_environment_directory(self):
        default_env_dir = os.path.join(envs_dir, DEFAULT_ENVIRONMENT['id'])
        if not os.path.exists(default_env_dir):
            os.makedirs(default_env_dir, exist_ok=True)

    async def retrieve_environments(self):
        async with db_session_context() as session:
            result = await session.execute(select(Environment))
            db_environments = result.scalars().all()
            # Convert SQLModel objects to dictionaries and set is_default to False
            environments = [
                {**env.dict(), 'is_default': False}
                for env in db_environments
            ]
            # Prepend the default environment
            return [DEFAULT_ENVIRONMENT] + environments

    async def retrieve_environment(self, env_id: str):
        if env_id == DEFAULT_ENVIRONMENT['id']:
            return DEFAULT_ENVIRONMENT
        async with db_session_context() as session:
            env = await session.get(Environment, env_id)
            return {**env.dict(), 'is_default': False} if env else None

    async def create_environment(self, env_data: dict):
        if env_data.get('id') == DEFAULT_ENVIRONMENT['id']:
            raise ValueError("Cannot create an environment with the reserved 'default' id")
        async with db_session_context() as session:
            new_env = Environment(**env_data)
            session.add(new_env)
            await session.commit()
            await session.refresh(new_env)
            
            # Create the environment directory
            env_dir = os.path.join(envs_dir, new_env.id)
            os.makedirs(env_dir, exist_ok=True)
            
            return {**new_env.to_dict(), 'is_default': False}

    async def update_environment(self, env_id: str, env_data: dict):
        if env_id == DEFAULT_ENVIRONMENT['id']:
            raise ValueError("Cannot update the default environment")
        async with db_session_context() as session:
            env = await session.get(Environment, env_id)
            if env:
                old_id = env.id
                for key, value in env_data.items():
                    setattr(env, key, value)
                await session.commit()
                await session.refresh(env)
                
                # Rename the environment directory if the ID has changed
                if old_id != env.id:
                    old_dir = os.path.join(envs_dir, old_id)
                    new_dir = os.path.join(envs_dir, env.id)
                    if os.path.exists(old_dir):
                        os.rename(old_dir, new_dir)
                
                return {**env.dict(), 'is_default': False}
            return None

    async def delete_environment(self, env_id: str):
        if env_id == DEFAULT_ENVIRONMENT['id']:
            raise ValueError("Cannot delete the default environment")
        async with db_session_context() as session:
            env = await session.get(Environment, env_id)
            if env:
                await session.delete(env)
                await session.commit()
                
                # Remove the environment directory
                env_dir = os.path.join(envs_dir, env_id)
                if os.path.exists(env_dir):
                    import shutil
                    shutil.rmtree(env_dir)
                
                return True
            return False
    