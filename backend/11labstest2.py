import datetime as dt
import os

from elevenlabs import play
from elevenlabs.client import ElevenLabs

start = dt.datetime.now()

client = ElevenLabs(api_key=os.environ['ELEVENLABS_KEY'])

audio = client.generate(
    text="Weiß ich nicht, lass mal wieder gehen und Bäume fällen.",
    voice="Chris",
    model="eleven_multilingual_v1",
)

end = dt.datetime.now()

play(audio)
