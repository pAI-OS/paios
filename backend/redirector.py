from threading import Lock
from starlette.responses import RedirectResponse, PlainTextResponse
from backend.managers.SharesManager import SharesManager
from backend.managers.ResourcesManager import ResourcesManager

# set up logging
from common.log import get_logger
logger = get_logger(__name__)

async def redirector(request):
    response = await Redirector().handle_get(request)
    return response

class Redirector:
    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    logger.info("Creating Redirector instance.")
                    cls._instance = super(Redirector, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        self.slm = SharesManager()
        self.rm = ResourcesManager()

    async def handle_get(self, request):
        logger.debug("redirection request for url_key = {}".format(request.path_params['url_key']))
        url_key = request.path_params['url_key']
        share = await self.slm.retrieve_share(url_key)
        logger.debug("share: {}".format(share))
        if share is None or share.is_revoked:
            logger.error("Redirection failed: share link {} doesn't exist or has been revoked.".format(url_key))
            return PlainTextResponse(f"Invalid Share Link.", status_code=404)
        resource = await self.rm.retrieve_resource(share.resource_id)
        logger.debug("resource: {}".format(resource))
        if resource is None:
            logger.error("Redirection failed: share link {} resource not found.".format(url_key))
            return PlainTextResponse(f"Unknown Resource.", status_code=500) # should not happen
        redirect_url = resource.uri
        logger.info("Share link {} ({}) redirected to {}.".format(url_key, resource.name, redirect_url))
        return RedirectResponse(url=redirect_url)
