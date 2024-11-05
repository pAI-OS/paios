from starlette.responses import JSONResponse, Response
from common.paths import api_base_url
from backend.managers.SharesManager import SharesManager
from backend.managers.ResourcesManager import ResourcesManager
from backend.pagination import parse_pagination_params
from datetime import datetime, timezone

class SharesView:
    def __init__(self):
        self.slm = SharesManager()
        self.rm = ResourcesManager()

    async def get(self, id: str):
        share = await self.slm.retrieve_share(id)
        if share is None:
            return JSONResponse(headers={"error": "Share not found"}, status_code=404)
        return JSONResponse(share.model_dump(), status_code=200)

    async def post(self, body: dict):
        expiration_dt = None
        if 'expiration_dt' in body and body['expiration_dt'] is not None:
            expiration_dt = datetime.fromisoformat(body['expiration_dt']).astimezone(tz=timezone.utc)
        user_id = None
        if 'user_id' in body and body['user_id']:
            valid = await self.slm.validate_assistant_user_id(body['resource_id'], body['user_id'])
            if valid is not None:
                return JSONResponse({"error": valid}, status_code=400)
            user_id = body['user_id']
        new_share = await self.slm.create_share(resource_id=body['resource_id'],
                                                user_id=user_id,
                                                expiration_dt=expiration_dt,
                                                is_revoked=False)
        return JSONResponse(new_share.model_dump(), status_code=201, headers={'Location': f'{api_base_url}/shares/{new_share.id}'})

    async def put(self, id: str, body: dict):
        expiration_dt = None
        if 'expiration_dt' in body and body['expiration_dt'] is not None:
            expiration_dt = datetime.fromisoformat(body['expiration_dt']).astimezone(tz=timezone.utc)
        user_id = None
        if 'user_id' in body and body['user_id']:
            user_id = body['user_id']
        updated_share = await self.slm.update_share(id,
                                                    resource_id=body['resource_id'],
                                                    user_id=user_id,
                                                    expiration_dt=expiration_dt,
                                                    is_revoked=body['is_revoked'])
        if updated_share is None:
            return JSONResponse({"error": "Share not found"}, status_code=404)
        return JSONResponse(updated_share.model_dump(), status_code=200)

    async def delete(self, id: str):
        success = await self.slm.delete_share(id)
        if not success:
            return JSONResponse({"error": "Share not found"}, status_code=404)
        return Response(status_code=204)

    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        shares, total_count = await self.slm.retrieve_shares(limit=limit, offset=offset, sort_by=sort_by, sort_order=sort_order, filters=filters)
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'shares {offset}-{offset + len(shares) - 1}/{total_count}'
        }
        return JSONResponse([share.model_dump() for share in shares], status_code=200, headers=headers)