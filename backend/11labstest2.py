import datetime as dt

from elevenlabs import play
from elevenlabs.client import ElevenLabs

start = dt.datetime.now()

client = ElevenLabs(
    api_key="41f1d61b1ce48269216086555aa78d33",
)


audio = client.generate(
    text="Weiß ich nicht, lass mal wieder gehen und Bäume fällen.",
    voice="Chris",
    model="eleven_multilingual_v1",
)

end = dt.datetime.now()

# print("Time elapsed for generating:", end - start)
play(audio)
