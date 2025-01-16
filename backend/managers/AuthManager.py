import os
import json
import base64
import jwt
import secrets
from threading import Lock
from datetime import datetime, timedelta, timezone
from sqlalchemy import select, update, delete
from backend.models import User, Cred, Session
from backend.db import db_session_context
from uuid import uuid4
from webauthn import (
    verify_registration_response,
    verify_authentication_response, 
    generate_authentication_options, 
    generate_registration_options, 
    options_to_json,
    base64url_to_bytes
)
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorAttachment,
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement,
    PublicKeyCredentialDescriptor,
    PublicKeyCredentialType,
    AuthenticatorTransport,
    UserVerificationRequirement
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
from connexion.exceptions import Unauthorized
from common.utils import get_env_key
import os
from pathlib import Path
from common.mail import send
from itsdangerous import URLSafeTimedSerializer, BadSignature, SignatureExpired
from jinja2 import Environment, FileSystemLoader
from backend.managers.CasbinRoleManager import CasbinRoleManager
# set up logging
from common.log import get_logger
logger = get_logger(__name__)

def generate_jwt(payload: dict):
    header = {
        "alg": "HS256",
        "typ": "JWT"
    }

    jwt_secret = get_env_key('PAIOS_JWT_SECRET', lambda: secrets.token_urlsafe(32))

    encoded_jwt = jwt.encode(payload, jwt_secret, algorithm='HS256', headers=header)
    return encoded_jwt

def generate_verification_token(email: str):
    SECRET_KEY = get_env_key('PAIOS_JWT_SECRET', lambda: secrets.token_urlsafe(32))
    SALT = "email-confirmation-salt"
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    return serializer.dumps(email, salt=SALT)

def verify_email_token(token):
    SECRET_KEY = get_env_key('PAIOS_JWT_SECRET', lambda: secrets.token_urlsafe(32))
    SALT = "email-confirmation-salt"
    serializer = URLSafeTimedSerializer(SECRET_KEY)
    try:
        user_id = serializer.loads(token, salt=SALT, max_age=900)
    except SignatureExpired:
        return None 
    except BadSignature:
        return None
    return user_id

async def send_verification_email(user_id, email_id):
    token = generate_verification_token(user_id)
    host = get_env_key('PAIOS_HOST', 'localhost')
    port = get_env_key('PAIOS_PORT', '8443')
    verification_url = f"https://{host}:{port}/#/verify-email/{token}"
    
    template_path = Path(__file__).parent.parent / 'templates'
    env = Environment(loader=FileSystemLoader(template_path))
    template = env.get_template('email_verification_template.html')
    html_content = template.render(verification_url=verification_url)
    
    try:
        await send(
            to=email_id,
            subject="Verify pAI-OS Email",
            body_text=f"Please verify your email by clicking: {verification_url}",
            body_html=html_content
        )
    except Exception as e:
        logger.error(f"Failed to send verification email: {str(e)}")
        raise

def decode_jwt(token):
    jwt_secret = get_env_key('PAIOS_JWT_SECRET', lambda: secrets.token_urlsafe(32))

    try:
        decoded = jwt.decode(token, jwt_secret, algorithms=["HS256"])
        logger.debug("Decoded JWT: %s", decoded)
        return {"uid": decoded['sub'], "role": decoded['role']}
    
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise Unauthorized("Token expired")
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        raise Unauthorized("Invalid token")
    except Exception as e:
        logger.error(f"Unexpected error decoding token: {str(e)}")
        raise Unauthorized("Invalid token")


class AuthManager:
    # AuthManager: manages authentication processes: registration, login

    _instance = None
    _lock = Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(AuthManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance
    
    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._initialized = True
                    # self._load_rbac_model()

    # def _load_rbac_model(self):
    #     model_path = Path(__file__).parent.parent / 'rbac_model.conf'
    #     policy_path = Path(__file__).parent.parent / 'rbac_policy.csv'
    #     self.enforcer = casbin.Enforcer(str(model_path), str(policy_path))

    
    async def auth_options(self, email_id: str):
        async with db_session_context() as session:
            result = await session.execute(select(User).where(User.email == email_id))
            user = result.scalar_one_or_none()

            if not user or not user.emailVerified:
                return self.webauthn_register_options(email_id, user)
            
            return await self.webauthn_login_options(user)

    def webauthn_register_options(self, email_id, user):
        # result = await session.execute(select(User).where(User.email == email_id))
        # user = result.scalar_one_or_none()
        user_id = base64url_to_bytes(user.webauthn_user_id) if user else os.urandom(32)

        exclude_credentials = []

        # if user:
        #     creds_result = await session.execute(select(Cred).filter(Cred.webauthn_user_id == user.webauthn_user_id))
        #     creds = creds_result.scalars().all()

        #     for cred in creds:
        #         transports = [AuthenticatorTransport[transport.upper()] for transport in json.loads(cred.transports)]
        #         exclude_credentials.append(PublicKeyCredentialDescriptor(
        #             id=base64url_to_bytes(cred.id),
        #             type=PublicKeyCredentialType.PUBLIC_KEY,
        #             transports=transports
        #         ))

        options = generate_registration_options(
            rp_name="pAI-OS",
            rp_id="localhost",
            user_name=email_id,
            user_id=user_id,
            attestation=AttestationConveyancePreference.DIRECT,
            authenticator_selection=AuthenticatorSelectionCriteria(
                authenticator_attachment=AuthenticatorAttachment.CROSS_PLATFORM,
                resident_key=ResidentKeyRequirement.REQUIRED
            ),
            supported_pub_key_algs=[COSEAlgorithmIdentifier.ECDSA_SHA_256],
            timeout=12000,
            exclude_credentials=exclude_credentials
        )

        challenge = base64.urlsafe_b64encode(options.challenge).decode("utf-8").rstrip("=")

        return challenge, options_to_json(options), "REGISTER"
        
    async def webauthn_register(self, challenge: str, email_id: str, user_id: str, response):
        async with db_session_context() as session:
            host = get_env_key('PAIOS_HOST', 'localhost')
            port = get_env_key('PAIOS_PORT', '8443')
            expected_origin = f"https://{host}:{port}"
            expected_rpid = host

            res = verify_registration_response(credential=response, 
                                               expected_challenge=base64url_to_bytes(challenge),
                                               expected_origin=expected_origin,
                                               expected_rp_id=expected_rpid,
                                               require_user_verification=False
                                               )
            if not res:
                return False
            
            user_result = await session.execute(select(User).where(User.email == email_id))
            user = user_result.scalar_one_or_none()
            
            if not user:    
                new_user = User(id=str(uuid4()), name=email_id, email=email_id, webauthn_user_id=user_id)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                user = new_user
            else:
                await session.execute(delete(Cred).where(Cred.webauthn_user_id == user.webauthn_user_id))
                await session.commit()
                # Add default role for new user
                # self.add_role_for_user(str(user.id), 'user')

            base64url_cred_id = base64.urlsafe_b64encode(res.credential_id).decode("utf-8").rstrip("=")
            base64url_public_key = base64.urlsafe_b64encode(res.credential_public_key).decode("utf-8").rstrip("=")

            transports = json.dumps(response["response"]["transports"])
            new_cred = Cred(id=base64url_cred_id, public_key=base64url_public_key, webauthn_user_id=user.webauthn_user_id, backed_up=res.credential_backed_up, name=email_id, transports=transports)
            session.add(new_cred)
            await session.commit()
            await send_verification_email(user.id, email_id)
            # payload = {
            #     "sub": user.id,
            #     "iat": datetime.now(timezone.utc),
            #     "exp": datetime.now(timezone.utc) + timedelta(days=1),
            #     "roles": self.get_roles_for_user(str(user.id))  # Include roles in the token
            # }

            # token = generate_jwt(payload)
            
            return True

    async def webauthn_login_options(self, user):
        async with db_session_context() as session:
            # user_result = await session.execute(select(User).where(User.email == email_id))
            # user = user_result.scalar_one_or_none()

            # if not user:
            #     return None, None
            
            allow_credentials = []

            creds_result = await session.execute(select(Cred).filter(Cred.webauthn_user_id == user.webauthn_user_id))
            creds = creds_result.scalars().all()

            for cred in creds:
                transports = [AuthenticatorTransport[transport.upper()] for transport in json.loads(cred.transports)]
                allow_credentials.append(PublicKeyCredentialDescriptor(
                        id=base64url_to_bytes(cred.id),
                        type=PublicKeyCredentialType.PUBLIC_KEY,
                        transports=transports
                ))

            options = generate_authentication_options(
                rp_id="localhost",
                timeout=12000,
                allow_credentials=allow_credentials,
                user_verification=UserVerificationRequirement.REQUIRED
            )

            challenge = base64.urlsafe_b64encode(options.challenge).decode("utf-8").rstrip("=")
            return challenge, options_to_json(options), "LOGIN"
        
    async def webauthn_login(self, challenge: str, email_id:str, response):
        async with db_session_context() as session:
            host = get_env_key('PAIOS_HOST', 'localhost')
            port = get_env_key('PAIOS_PORT', '8443')
            expected_origin = f"https://{host}:{port}"
            expected_rpid = host
            
            user_result = await session.execute(select(User).where(User.email == email_id, User.emailVerified == True))
            user = user_result.scalar_one_or_none()

            if not user:
                return None
            
            credential_result = await session.execute(select(Cred).where(Cred.id == response["id"]))
            credential = credential_result.scalar_one_or_none()

            if not credential:
                return None
            
            res = verify_authentication_response(credential=response,
                                                 expected_challenge=base64url_to_bytes(challenge),
                                                 expected_origin=expected_origin,
                                                 expected_rp_id=expected_rpid,
                                                 credential_public_key=base64url_to_bytes(credential.public_key),
                                                 credential_current_sign_count=0,
                                                 require_user_verification=True
                                                 )

            if not res.new_sign_count != 1:
                return None
            
            cb = CasbinRoleManager()
            role = cb.get_user_role(user.id, "ADMIN_PORTAL")
            payload = {
                "sub": user.id,
                "role": role,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(days=1)
            }
            token = generate_jwt(payload)
            return token, role
        
    async def verify_email(self, token: str):
        async with db_session_context() as session:
            user_id = verify_email_token(token)

            if not user_id:
                return None
            
            user_result = await session.execute(select(User).where(User.id == user_id))
            user = user_result.scalar_one_or_none()
            if not user or user.emailVerified:
                return None

            user.emailVerified = True

            cb = CasbinRoleManager()
            admin_users = cb.get_admin_users("ADMIN_PORTAL")
            if not admin_users:
                cb.assign_user_role(user.id, "ADMIN_PORTAL", "admin") # assign admin role to first user created
            else:
                cb.assign_user_role(user.id, "ADMIN_PORTAL", "user")

            await session.commit()
            
            return True


    async def create_session(self, user_id: str):
        async with db_session_context() as session:
            new_session = Session(
                id=str(uuid4()),
                user_id=user_id,
                token=str(uuid4()),  # Generate a unique token
                expires_at=datetime.utcnow() + timedelta(days=1)  # Set expiration to 1 day from now
            )
            session.add(new_session)
            await session.commit()
            await session.refresh(new_session)
            return new_session.id, new_session.token

    async def delete_session(self, token: str):
        async with db_session_context() as session:
            stmt = delete(Session).where(Session.token == token)
            await session.execute(stmt)
            await session.commit()
