from abc import ABC, abstractmethod
from backend.dependencies.DependencyState import DependencyState
import threading
import asyncio
import logging

logger = logging.getLogger(__name__)

class Dependency(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def handle_exception(self, exception):
        logger.error(f"Unexpected error: {exception}")
        return {"error": "An unexpected error occurred during dependency installation."}

    @abstractmethod
    def refresh_status(self, ability, dependency):
        pass

    @abstractmethod
    def start(self, ability, dependency, background=False):
        pass

    @abstractmethod
    def stop(self, ability, dependency, background=False):
        pass

    @abstractmethod
    async def _install(self, ability, dependency, background=False):
        pass

    async def install(self, ability, dependency, background=False):

        async def install_task(ability, dependency, background):
            try:
                logger.info(f"Started installation of dependency {dependency['id']}")
                await self._install(ability, dependency, background)
                logger.info(f"Completed installation of dependency {dependency['id']}")
            except Exception as e:
                self.handle_exception(e)

        if background:
            logger.info(f"Installation of dependency {dependency['id']} started in background")
            self._run_in_background(install_task, ability, dependency, background)
        else:
            logger.info(f"Installation of dependency {dependency['id']} started")
            return await install_task(ability, dependency, background)

    def _default_callback(self, result):
        try:
            if result is None:
                logger.info("Task completed successfully.")
            elif isinstance(result, dict) and 'message' in result:
                logger.info(result['message'])
            else:
                logger.error(f"Unexpected result: {result}")
        except Exception as e:
            logger.error(f"Error in default callback: {e}")

    def _run_in_background(self, task_function, *args, callback_function=None):
        def task_callback(loop):
            try:
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(task_function(*args))
                if callback_function:
                    callback_function(result)
                else:
                    self._default_callback(result)
            except Exception as e:
                logger.error(f"Unexpected error during the background task: {e}", exc_info=True)
                if callback_function:
                    callback_function({"message": f"An unexpected error occurred: {str(e)}"})
                else:
                    self._default_callback({"message": f"An unexpected error occurred: {str(e)}"})

        loop = asyncio.new_event_loop()
        task_thread = threading.Thread(target=task_callback, args=(loop,))
        task_thread.start()
