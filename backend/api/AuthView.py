from starlette.responses import JSONResponse
from backend.managers.AuthManager import AuthManager
import logging
from backend.schemas import RegistrationOptions, VerifyAuthentication, AuthenticationOptions, VerifyRegistration

logger = logging.getLogger(__name__)

class AuthView:
    def __init__(self):
        self.am = AuthManager()

    async def generate_registration_options(self, body: dict):
        options = await self.am.registration_options(body["email"])

        if not options:
            return JSONResponse({"error": "Something went wrong"}, status_code=500)
        return JSONResponse({"option": options}, status_code=200)
    

    async def verify_registration(self):
        return JSONResponse({"message": "Success"}, status_code=200)
    async def generate_authentication_options(self):
        return JSONResponse({"message": "Success"}, status_code=200)
    async def verify_authentication(self):
        return JSONResponse({"message": "Success"}, status_code=200)
    