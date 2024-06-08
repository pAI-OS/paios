from abc import ABC, abstractmethod
from backend.dependencies.DependencyState import DependencyState
import threading
import asyncio
import logging

logger = logging.getLogger(__name__)

class Dependency(ABC):
    def __init__(self):
        self.state = DependencyState.AVAILABLE

    def set_state(self, state: DependencyState):
        self.state = state

    def get_state(self):
        return self.state
    
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
    async def install(self, ability, dependency, background=False):
        pass

    def _default_callback(self, result):
        try:
            if isinstance(result, dict) and 'message' in result:
                logger.info(result['message'])
            else:
                logger.error(f"Unexpected result: {result}")
        except Exception as e:
            logger.error(f"Error in default callback: {e}")

    async def _run_in_background(self, task_function, *args, callback_function=None):
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
                    self.default_callback({"message": f"An unexpected error occurred: {str(e)}"})

        loop = asyncio.new_event_loop()
        task_thread = threading.Thread(target=task_callback, args=(loop,))
        task_thread.start()
