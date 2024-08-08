from starlette.responses import JSONResponse
from backend.managers.AuthManager import AuthManager
import logging
from backend.schemas import RegistrationOptions, VerifyAuthentication, AuthenticationOptions, VerifyRegistration
from connexion import request
from connexion.exceptions import OAuthProblem
logger = logging.getLogger(__name__)

class AuthView:
    def __init__(self):
        self.am = AuthManager()

    async def generate_registration_options(self, body: RegistrationOptions):
        challenge, options = await self.am.registration_options(body["email"])

        if not options:
            return JSONResponse({"error": "Something went wrong"}, status_code=500)
        
        response = JSONResponse({"options": options}, status_code=200)
        response.set_cookie(key="challenge",value=challenge)
        return response
    

    async def verify_registration(self, body: VerifyRegistration):
        challenge = request.cookies.get("challenge")
        user = await self.am.registrationResponse(challenge, body["email"], body["user_id"], body["att_resp"])
        if not user:
            return JSONResponse({"message": "Failed"}, status_code=401)
        
        response = JSONResponse({"message": "Success"}, status_code=200)
        response.set_cookie(key="challenge",value="", expires=0)
        response.set_cookie(key="user", value=user)
        return response
    
    async def generate_authentication_options(self, body: AuthenticationOptions):
        challenge, options = await self.am.signinRequestOptions(body["email"])

        if not options:
            return JSONResponse({"error": "Something went wrong"}, status_code=500)
         
     
        response = JSONResponse({"options": options}, status_code=200)
        response.set_cookie(key="challenge", value=challenge)
        return response
    
    async def verify_authentication(self, body: VerifyAuthentication):
        user = await self.am.signinResponse(body["challenge"], body["email"],body["auth_resp"])

        if not user:
            return JSONResponse({"error": "Authentication failed."}, status_code=401)
         
        response = JSONResponse({"message": "Success"}, status_code=200)
        response.set_cookie(key="challenge", value="", expires=0)
        response.set_cookie(key="user", value=user)
        return response
    
    async def apikey_auth(self, user_id, scopes):
        user = await self.am.apikey_auth(user_id)

        if not user:
            raise OAuthProblem("Invalid token")
        
        return user
    