from threading import Lock
import os
import requests
from backend.schemas import VoiceCreateSchema
from backend.db import db_session_context
from uuid import uuid4
from backend.models import Voice
from typing import List, Tuple, Optional, Dict, Any
from sqlalchemy import select, func
from backend.schemas import VoiceSchema
from pathlib import Path
from backend.models import Resource, Persona
 
XI_API_KEY = os.environ.get('XI_API_KEY')

class VoicesFacesManager:
    _instance = None
    _lock = Lock()    

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(VoicesFacesManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def __init__(self):
        if not hasattr(self, '_initialized'):
            with self._lock:
                if not hasattr(self, '_initialized'):
                    self._initialized = True        
        
    async def map_xi_to_voice(self):
        xi_voices = []
        xi_api_key = XI_API_KEY
        xi_url = "https://api.elevenlabs.io/v1/voices"
        headers = {
                    "Accept": "application/json",
                    "xi-api-key": xi_api_key,
                    "Content-Type": "application/json"
                }
        
        response = requests.get(xi_url, headers=headers)
        data = response.json()
        for voice in data['voices']:
            voice_data = {
                'xi_id': voice['voice_id'],
                'name': voice['name'],                
                'image_url': '/voice-icon.png',
                'sample_url': '/' + voice['name'] + '.mp3' 
                }
            xi_voices.append(voice_data)
        return xi_voices
    

    async def create_voice(self, voice_data: VoiceCreateSchema) -> str:
        async with db_session_context() as session:
            new_voice = Voice(id=str(uuid4()), xi_id=voice_data['xi_id'], name=voice_data['name'], image_url=voice_data['image_url'], sample_url=voice_data['sample_url'])
            session.add(new_voice)
            await session.commit() 
            await session.refresh(new_voice)
            return new_voice.id
        
    async def retrieve_voice(self, voice_id: str) -> Optional[VoiceSchema]:
        async with db_session_context() as session:
            query = select(Voice).filter(Voice.id == voice_id)
            result = await session.execute(query)
            voice = result.scalar_one_or_none()
            if voice:
                return VoiceSchema.from_orm(voice)
            return None    

    async def retrieve_voices(self, offset: int = 0, limit: int = 100, sort_by: Optional[str] = None,
                                    sort_order:str = 'asc',  filters: Optional[Dict[str, Any]] = None) -> Tuple[List[VoiceSchema], int]:
            async with db_session_context() as session:
                query = select(Voice)
                result = await session.execute(query)
                db_voice = result.scalars().all()
                if db_voice == []:
                    xi_voices = await self.map_xi_to_voice()
                    for voice in xi_voices:
                        await self.create_voice(voice)                        

                if filters:
                    for key, value in filters.items():
                        if key == 'name':
                            query = query.filter(Voice.name.ilike(f"%{value}%"))
                        elif isinstance(value, list):
                            query = query.filter(getattr(Voice, key).in_(value))
                        else:
                            query = query.filter(getattr(Voice, key) == value)

                if sort_by and sort_by in ['id','xi_id', 'name','image_url','sample_url']:
                    order_column = getattr(Voice, sort_by)
                    query = query.order_by(order_column.desc() if sort_order.lower() == 'desc' else order_column)

                query = query.offset(offset).limit(limit)

                result = await session.execute(query)
                voices = [VoiceSchema.from_orm(voice) for voice in result.scalars().all()]

                if not voices:
                    return [], 0

                count_query = select(func.count()).select_from(Voice)
                if filters:
                    for key, value in filters.items():
                        if key == 'name':
                            count_query = count_query.filter(Voice.name.ilike(f"%{value}%"))
                        elif isinstance(value, list):
                            count_query = count_query.filter(getattr(Voice, key).in_(value))
                        else:
                            count_query = count_query.filter(getattr(Voice, key) == value)

                total_count = await session.execute(count_query)
                total_count = total_count.scalar()

                return voices, total_count
            
    async def text_to_speech(self, voice_id: str, body: str, assistant_id: str, msg_id: str) -> Tuple[Optional[dict], Optional[str]]:
        voice = await self.retrieve_voice(voice_id)
        xi_api_key = XI_API_KEY
        xi_id = voice.xi_id
        temp = os.path.dirname(os.path.realpath(__file__))
        directory = Path(os.path.join(os.path.dirname(temp), f'public/{assistant_id}'))
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f'{msg_id}.mp3'
        audio_msg_path = str(file_path)
        print('audio_msg_path: ', audio_msg_path)
        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{xi_id}/stream"

        headers = {
            "Accept": "application/json",
            "xi-api-key": xi_api_key
        }

        data = {
            "text": body,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }
        try:
            response = requests.post(tts_url, headers=headers, json=data, stream=True)
            if response.ok:
                with open(audio_msg_path, "wb") as f:
                    for chunk in response.iter_content(chunk_size=int(os.environ.get('XI_CHUNK_SIZE'))):
                        f.write(chunk)
                print("Audio stream saved successfully.")
                return {"message": "Audio stream saved successfully.", "audio_msg_path": audio_msg_path}, None
            else:
                error_message = response.text
                print(error_message)
                return None, error_message
        except Exception as e:
            error_message = str(e)
            print(f"An error occurred: {error_message}")
            return None, error_message
        
    async def generate_voice_response(self, assistant_id, chat_response, message_id) -> Tuple[Optional[dict], Optional[str]]:
        try:
            async with db_session_context() as session:                
                resource = await session.execute(select(Resource).filter(Resource.id == assistant_id))
                resource = resource.scalar_one_or_none()                    
                persona_id = resource.persona_id                        
                if persona_id:
                    persona = await session.execute(select(Persona).filter(Persona.id == persona_id))
                    persona = persona.scalar_one_or_none()
                    voice_id = persona.voice_id
                    vfm = VoicesFacesManager()                            
                    response, error_message = await vfm.text_to_speech(voice_id, chat_response, assistant_id, message_id)
                    if error_message:
                        return None, error_message                   
                    return response.get("audio_msg_path"), None
        except Exception as e:        
            return None, f"An unexpected error occurred while generating a voice response: {str(e)}"        

    async def async_file_generator(self, file_path):
        with open(file_path, 'rb') as audio_file:
            while chunk := audio_file.read(1024):
                yield chunk