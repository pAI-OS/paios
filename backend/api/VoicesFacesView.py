from starlette.responses import JSONResponse, Response
from backend.managers.VoicesFacesManager import VoicesFacesManager
from backend.managers.MessagesManager import MessagesManager
from common.paths import api_base_url
from backend.pagination import parse_pagination_params
from backend.schemas import VoiceCreateSchema
from starlette.responses import JSONResponse, StreamingResponse
import os
from pathlib import Path
import shutil



class VoicesFacesView:
    def __init__(self):
        self.vfm = VoicesFacesManager()
        self.mm = MessagesManager() 
    
    async def search(self, filter: str = None, range: str = None, sort: str = None):
        result = parse_pagination_params(filter, range, sort)
        if isinstance(result, JSONResponse):
            return result

        offset, limit, sort_by, sort_order, filters = result
        try:
            voices, total_count = await self.vfm.retrieve_voices(
                limit=limit,
                offset=offset,
                sort_by=sort_by,
                sort_order=sort_order,
                filters=filters
            )            
            if voices == [] and total_count == 0:
                return JSONResponse({"error": "No voices found"}, status_code=404)
            
        except Exception as e:
            return JSONResponse({"error": str(e)}, status_code=500)
        
        headers = {
            'X-Total-Count': str(total_count),
            'Content-Range': f'voices {offset}-{offset + len(voices) - 1}/{total_count}'
        }
        return JSONResponse([voice.dict() for voice in voices], status_code=200, headers=headers)
    

    async def post(self, body: VoiceCreateSchema):
        msg_id = body.get('msg_id')
        message = await self.mm.retrieve_message(msg_id)
        if message.voice_active == 'True':
            audio_msg_path, error_message = await self.vfm.generate_voice_response(message.assistant_id, message.chat_response, msg_id)
            if error_message:
                return JSONResponse({"error": error_message}, status_code=404)
            if audio_msg_path and os.path.exists(audio_msg_path):
                streaming_response = StreamingResponse(
                    self.vfm.async_file_generator(audio_msg_path),
                    media_type='audio/mpeg',
                    headers={
                        "Content-Disposition": f"attachment; filename={os.path.basename(audio_msg_path)}"
                    }
                )                                                                     
                return streaming_response
            else:
                return JSONResponse({"error": "File not found"}, status_code=404)
            
    async def delete(self, id: str):
        print('msg_id: ', id)
        message = await self.mm.retrieve_message(id)
        assistant_id = message.assistant_id
        temp = os.path.dirname(os.path.realpath(__file__))
        directory = Path(os.path.join(os.path.dirname(temp), f'public/{assistant_id}'))
        file_path = directory / f'{id}.mp3'        

        if directory.exists():
            shutil.rmtree(directory)
            return JSONResponse({"success": "Directory deleted successfully"}, status_code=200)
        else:
            return JSONResponse({"error": "Directory not found"}, status_code=404)