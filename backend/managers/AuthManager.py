from threading import Lock
from webauthn import (
    verify_registration_response,
    verify_authentication_response, 
    generate_authentication_options, 
    generate_registration_options, 
    options_to_json,
    base64url_to_bytes)
from sqlalchemy import select, update
from backend.models import User, PublicKeyCred
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
    AuthenticatorTransport
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier
import json
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
            user_id = base64url_to_bytes(user.passkey_user_id) if user else os.urandom(32)

            exclude_credentials = []

            if user:
                creds_result = await session.execute(select(PublicKeyCred).filter(PublicKeyCred.passkey_user_id == user.passkey_user_id))
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

            return options_to_json(options)
        
    async def registrationResponse(self, challenge: str, email_id: str,user_id: str, response):
        async with db_session_context() as session:
            expected_origin = "http://localhost:3080"
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
                new_user = User(id=str(uuid4()), name=email_id, email=email_id, passkey_user_id=user_id)
                session.add(new_user)
                await session.commit()
                await session.refresh(new_user)
                user = new_user
                
            base64_cred_id = base64.b64encode(res.credential_id).decode("utf-8")
            base64_public_key = base64.b64encode(res.credential_public_key).decode("utf-8")


            transports = json.dumps(response["response"]["transports"])
            new_cred = PublicKeyCred(id=base64_cred_id, public_key=base64_public_key, passkey_user_id=user.passkey_user_id, backed_up=res.credential_backed_up, name=email_id, transports=transports)
            session.add(new_cred)
            await session.commit()

            return True
            

            
