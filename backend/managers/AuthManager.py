from threading import Lock
from webauthn import (
    verify_registration_response,
    verify_authentication_response, 
    generate_authentication_options, 
    generate_registration_options, 
    options_to_json,
    base64url_to_bytes)
from sqlalchemy import select, update, delete
from backend.models import User, Cred, Session
from backend.db import db_session_context
import os
import base64
from uuid import uuid4
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
import json
from datetime import datetime, timedelta, timezone

from backend.utils import generate_jwt

class AuthManager:
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

    async def registration_options(self, email_id: str):
        async with db_session_context() as session:
            result = await session.execute(select(User).where(User.email == email_id))
            user = result.scalar_one_or_none()
            user_id = base64url_to_bytes(user.webauthn_user_id) if user else os.urandom(32)

            exclude_credentials = []

            if user:
                creds_result = await session.execute(select(Cred).filter(Cred.webauthn_user_id == user.webauthn_user_id))
                creds = creds_result.scalars().all()

                for cred in creds:
                    transports = [AuthenticatorTransport[transport.upper()] for transport in json.loads(cred.transports)]
                    exclude_credentials.append(PublicKeyCredentialDescriptor(
                        id=base64url_to_bytes(cred.id),
                        type=PublicKeyCredentialType.PUBLIC_KEY,
                        transports=transports
                    ))

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

            return challenge, options_to_json(options)
        
    async def registrationResponse(self, challenge: str, email_id: str,user_id: str, response):
        async with db_session_context() as session:
            expected_origin = "https://localhost:8443"
            expected_rpid = "localhost"

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

            # _, token = await self.create_session(user.id)
            
            base64url_cred_id = base64.urlsafe_b64encode(res.credential_id).decode("utf-8").rstrip("=")
            base64url_public_key = base64.urlsafe_b64encode(res.credential_public_key).decode("utf-8").rstrip("=")


            transports = json.dumps(response["response"]["transports"])
            new_cred = Cred(id=base64url_cred_id, public_key=base64url_public_key, webauthn_user_id=user.webauthn_user_id, backed_up=res.credential_backed_up, name=email_id, transports=transports)
            session.add(new_cred)
            await session.commit()

            payload = {
                "sub": user.id,
                "iat": datetime.now(timezone.utc),
                "exp": datetime.now(timezone.utc) + timedelta(days=1)
            }

            token = generate_jwt(payload)
            return token

    async def signinRequestOptions(self, email_id: str):
        async with db_session_context() as session:
            user_result = await session.execute(select(User).where(User.email == email_id))
            user = user_result.scalar_one_or_none()

            if not user:
                return None, None
            
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
            return challenge, options_to_json(options)
        
    async def signinResponse(self, challenge: str,email_id:str, response):
        async with db_session_context() as session:
            expected_origin = "https://localhost:8443"
            expected_rpid = "localhost"
            credential_result = await session.execute(select(Cred).where(Cred.id == response["id"]))
            credential = credential_result.scalar_one_or_none()

            if not credential:
                return None
            
            user_result = await session.execute(select(User).where(User.email == email_id))
            user = user_result.scalar_one_or_none()

            if not user:
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
            
            # _, session_token = await self.create_session(user.id)
            payload = {
                "sub": user.id,
                "iat": datetime.utcnow(),
                "exp": datetime.utcnow() + timedelta(days=1)
            }
            token = generate_jwt(payload)
            
            return token

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