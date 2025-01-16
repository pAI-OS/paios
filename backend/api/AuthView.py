from starlette.responses import JSONResponse
from backend.managers.AuthManager import AuthManager
from backend.managers.CasbinRoleManager import CasbinRoleManager
from backend.schemas import AuthOptionsRequest, RegistrationOptions, VerifyAuthentication, AuthenticationOptions, VerifyRegistration
from connexion import request
from uuid import uuid4
from backend.models import Session
from sqlalchemy import delete

GENERIC_AUTH_ERROR = "Something went wrong"


class AuthView:
    def __init__(self):
        self.am = AuthManager()
        self.cb = CasbinRoleManager()

    async def auth_options(self, body: AuthOptionsRequest):
        challenge, options, type = await self.am.auth_options(body["email"])

        if not options:
            return JSONResponse({"error": GENERIC_AUTH_ERROR}, status_code=500)

        response = JSONResponse({"options": options, "flow": type}, status_code=200)
        response.set_cookie(key="challenge",value=challenge, secure=True, httponly=True, samesite='strict')
        return response

    async def webauthn_register_options(self, body: RegistrationOptions):
        challenge, options = await self.am.webauthn_register_options(body["email"])

        if not options:
            return JSONResponse({"error": GENERIC_AUTH_ERROR}, status_code=500)
        
        response = JSONResponse({"options": options}, status_code=200)
        response.set_cookie(key="challenge",value=challenge, secure=True, httponly=True, samesite='strict')
        return response
    
    async def webauthn_register(self, body: VerifyRegistration):
        challenge = request.cookies.get("challenge")
        res = await self.am.webauthn_register(challenge, body["email"], body["user_id"], body["att_resp"])
        if not res:
            return JSONResponse({"message": GENERIC_AUTH_ERROR}, status_code=401)
        
        response = JSONResponse({"message": "Success"}, status_code=200)
        response.set_cookie(key="challenge",value="", expires=0,secure=True, httponly=True, samesite='strict')
        
        return response
    
    async def webauthn_login_options(self, body: AuthenticationOptions):
        challenge, options = await self.am.webauthn_login_options(body["email"])

        if not options:
            return JSONResponse({"error": GENERIC_AUTH_ERROR}, status_code=500)
         
        response = JSONResponse({"options": options}, status_code=200)
        response.set_cookie(key="challenge", value=challenge, secure=True, httponly=True, samesite='strict')
        return response

    async def webauthn_login(self, body: VerifyAuthentication):
        challenge = request.cookies.get("challenge")
        token, role = await self.am.webauthn_login(challenge, body["email"], body["auth_resp"])
        if not token:
            return JSONResponse({"message": "Failed"}, status_code=401)
        
        permissions = self.cb.get_resource_access(role,"ADMIN_PORTAL")
        response = JSONResponse({"message": "Success", "token": token, "permissions": permissions}, status_code=200)
        response.set_cookie(key="challenge",value="", expires=0,secure=True, httponly=True, samesite='strict')
        
        return response
    
    async def verify_email(self, body):
        isValid = await self.am.verify_email(body["token"])

        if not isValid:
            return JSONResponse({"message": "Email validation failed."}, status_code=400)
        
        return JSONResponse({"message": "Success"}, status_code=200)
        
    async def logout(self):
        session_token = request.cookies.get("session_token")
        if session_token:
            await self.am.delete_session(session_token)
        
        response = JSONResponse({"message": "Logged out successfully"}, status_code=200)
        response.delete_cookie(key="session_token", secure=True, httponly=True, samesite='strict')
        return response
