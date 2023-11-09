import os
from elevenlabs import Voice, generate, set_api_key, save

openai_key = os.getenv('OPENAI_API_KEY')
elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')

FILE_PATH_NARRATION = './narration.mp3'
VOICE_ID_SCOTT = 'lW13fUK7lgqUyRVrI0OL'

set_api_key(elevenlabs_key)

def generate_narration_audio(text: str):
  audio = generate(
    text=text,
    voice=Voice(voice_id=VOICE_ID_SCOTT),
    model="eleven_multilingual_v2"
  )
  return audio
  
def save_narration(audio):
  save(audio, FILE_PATH_NARRATION)
  return FILE_PATH_NARRATION

