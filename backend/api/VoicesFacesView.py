from starlette.responses import JSONResponse
from backend.managers.VoicesFacesManager import VoicesFacesManager
from common.paths import api_base_url
from backend.pagination import parse_pagination_params
from backend.schemas import VoiceCreateSchema



class VoicesFacesView:
    def __init__(self):
        self.vfm = VoicesFacesManager()  
    # TODO: Finish text to speech
    async def post(self, id: str, body: VoiceCreateSchema):
        response, error_message = await self.vfm.text_to_speech(id, body)
        if error_message:
            return JSONResponse({"error": error_message}, status_code=404)
        else:
            return JSONResponse(response, status_code=200)
          
    
    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result

        voices, total_count = await self.vfm.retrieve_voices(
            limit=limit,
            offset=offset,
            sort_by=sort_by,
            sort_order=sort_order,
            filters=filters
        )
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'voices {offset}-{offset + len(voices) - 1}/{total_count}'
        }
        return JSONResponse([voice.dict() for voice in voices], status_code=200, headers=headers)