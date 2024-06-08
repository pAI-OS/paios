from abc import ABC, abstractmethod
import threading
import asyncio
import logging

logger = logging.getLogger(__name__)

class Dependency(ABC):
    def __init__(self):
        pass

    @abstractmethod
    def refresh_status(self, ability, dependency):
        pass

    @abstractmethod
    def start(self, ability, dependency):
        pass

    @abstractmethod
    def stop(self, ability, dependency):
        pass

    @abstractmethod
    async def install(self, ability, dependency):
        pass

    # asyncio event loops are not thread safe but package installation is blocking so we need to run it in a separate thread without creating a new event loop.
    async def install_in_background(self, ability, dependency, callback=None):
        def install_callback(loop):
            try:
                asyncio.set_event_loop(loop)
                result = loop.run_until_complete(self.install(ability, dependency))
                if callback:
                    callback(result)
            except Exception as e:
                logger.error(f"Unexpected error during dependency installation: {e}", exc_info=True)
                if callback:
                    callback({"message": f"An unexpected error occurred: {str(e)}"})

        loop = asyncio.new_event_loop()
        install_thread = threading.Thread(target=install_callback, args=(loop,))
        install_thread.start()
