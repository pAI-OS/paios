from threading import Lock
from webauthn import verify_registration_response,verify_authentication_response, generate_authentication_options, generate_registration_options, options_to_json
from sqlalchemy import select
from backend.models import User
from backend.db import db_session_context
import os
import json
from webauthn.helpers.structs import (
    AttestationConveyancePreference,
    AuthenticatorAttachment,
    AuthenticatorSelectionCriteria,
    ResidentKeyRequirement
)
from webauthn.helpers.cose import COSEAlgorithmIdentifier

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
            user_id = user.id if user else os.urandom(32)
            options = generate_registration_options(
                rp_name="pAI-OS",
                rp_id="localhost",
                user_name=email_id,
                user_id=user_id,
                attestation=AttestationConveyancePreference.NONE,
                authenticator_selection=AuthenticatorSelectionCriteria(
                    authenticator_attachment=AuthenticatorAttachment.PLATFORM,
                    resident_key=ResidentKeyRequirement.REQUIRED
                ),
                supported_pub_key_algs=[COSEAlgorithmIdentifier.ECDSA_SHA_512],
                timeout=12000
            )

            return options_to_json(options)
            

            
