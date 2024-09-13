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
        xi_api_key = os.environ.get('XI_API_KEY')
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

                # Get total count
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
            
    
    async def text_to_speech(self, voice_id: str, body) -> str:
        xi_api_key = os.environ.get('XI_API_KEY')
        xi_id = body['xi_id']
        OUTPUT_PATH = f"{xi_id}.mp3"  # Path to save the output audio file

        tts_url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream"

        headers = {
            "Accept": "application/json",
            "xi-api-key": xi_api_key
        }

        data = {
            "text": "Hola" ,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "style": 0.0,
                "use_speaker_boost": True
            }
        }

        response = requests.post(tts_url, headers=headers, json=data, stream=True)

        if response.ok:
            with open(OUTPUT_PATH, "wb") as f:
                for chunk in response.iter_content(chunk_size=os.environ.get('XI_CHUNK_SIZE')):
                    f.write(chunk)
            print("Audio stream saved successfully.")
        else:
            print(response.text)
            return response.text
        
    
