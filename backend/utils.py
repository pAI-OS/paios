from backend.db import db_session_context
from sqlalchemy import select
from backend.models import Session
from connexion.exceptions import OAuthProblem
import jwt

# Returns dict with null fields removed (e.g., for OpenAPI spec compliant
# responses without having to set nullable: true)
def remove_null_fields(data):
    if isinstance(data, dict):
        return {k: remove_null_fields(v) for k, v in data.items() if v is not None}
    elif isinstance(data, list):
        return [remove_null_fields(item) for item in data if item is not None]
    else:
        return data

# Returns dict with only keys_to_include (e.g., for OpenAPI spec compliant
# responses without unexpected fields present)
def filter_dict(data, keys_to_include):
    return {k: data[k] for k in keys_to_include if k in data}

# Converts a db result into a dict with named fields (e.g.,
# ["x", "y"], [1, 2] -> { "x": 1, "y": 2})
def zip_fields(fields, result):
    return {field: result[i] for i, field in enumerate(fields)}

async def apikey_auth(token):
    async with db_session_context() as session:
            session_token_res = await session.execute(select(Session).where(Session.token == token))
            session_token = session_token_res.scalar_one_or_none()

            if not session_token:
                raise OAuthProblem("Invalid token")
            
            return {"uid": session_token.user_id}
    
def generate_jwt(payload: dict):
    header = {
            "alg": "HS256",
            "typ": "JWT"
    }

    secret = "362584ff7539d6d15cfd7e10613f30dd38fa535e264a4e252636a2e46e04d9f8"

    encoded_jwt = jwt.encode(payload,secret, algorithm='HS256', headers=header)
    return encoded_jwt

def decode_token(token):
    secret = "362584ff7539d6d15cfd7e10613f30dd38fa535e264a4e252636a2e46e04d9f8"

    try:
        decoded = jwt.decode(token, secret, algorithms=["HS256"])
        print("DECODE...",decoded)
        return {"uid": decoded['sub']}
    
    except jwt.ExpiredSignatureError:
        raise OAuthProblem("Token expired")
    except jwt.InvalidTokenError:
        raise OAuthProblem("Invalid token")
    
