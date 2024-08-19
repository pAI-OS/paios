from starlette.responses import JSONResponse
from backend.managers.AuthManager import AuthManager
import logging
from backend.schemas import RegistrationOptions, VerifyAuthentication, AuthenticationOptions, VerifyRegistration
from connexion import request
logger = logging.getLogger(__name__)
from uuid import uuid4
from backend.models import Session
from sqlalchemy import delete

class AuthView:
    def __init__(self):
        self.am = AuthManager()

    async def generate_registration_options(self, body: RegistrationOptions):
        challenge, options = await self.am.registration_options(body["email"])

        if not options:
            return JSONResponse({"error": "Something went wrong"}, status_code=500)
        
        response = JSONResponse({"options": options}, status_code=200)
        response.set_cookie(key="challenge",value=challenge, secure=True, httponly=True, samesite='strict')
        return response
    

    async def verify_registration(self, body: VerifyRegistration):
        challenge = request.cookies.get("challenge")
        token = await self.am.registrationResponse(challenge, body["email"], body["user_id"], body["att_resp"])
        if not token:
            return JSONResponse({"message": "Failed"}, status_code=401)
        
        response = JSONResponse({"message": "Success"}, status_code=200)
        response.set_cookie(key="challenge",value="", expires=0,secure=True, httponly=True, samesite='strict')
        response.set_cookie(key="session_token", value=token,secure=True, httponly=True, samesite='strict')
        return response
    
    async def generate_authentication_options(self, body: AuthenticationOptions):
        challenge, options = await self.am.signinRequestOptions(body["email"])

        if not options:
            return JSONResponse({"error": "Something went wrong"}, status_code=500)
         
     
        response = JSONResponse({"options": options}, status_code=200)
        response.set_cookie(key="challenge", value=challenge, secure=True, httponly=True, samesite='strict')
        return response
    
    async def verify_authentication(self, body: VerifyAuthentication):
        token = await self.am.signinResponse(body["challenge"], body["email"], body["auth_resp"])

        if not token:
            return JSONResponse({"error": "Authentication failed."}, status_code=401)
         
        response = JSONResponse({"message": "Success"}, status_code=200)
        response.set_cookie(key="challenge", value="", expires=0, secure=True, httponly=True, samesite='strict')
        response.set_cookie(key="session_token", value=token, secure=True, httponly=True, samesite='strict')
        return response
        
    async def logout(self):
        session_token = request.cookies.get("session_token")
        if session_token:
            await self.am.delete_session(session_token)
        
        response = JSONResponse({"message": "Logged out successfully"}, status_code=200)
        response.delete_cookie(key="session_token", secure=True, httponly=True, samesite='strict')
        return response