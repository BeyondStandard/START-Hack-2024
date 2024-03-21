import whisper
import requests
from elevenlabs.client import ElevenLabs
from elevenlabs import play

# To add twilio/phone app thingy
file_path = "test_swiss_german.mp3"

audio = whisper.load_audio(file_path)
model = whisper.load_model("base")

# load audio and pad/trim it to fit 30 seconds
audio_trim = whisper.pad_or_trim(audio)

# make log-Mel spectrogram and move to the same device as the model
mel = whisper.log_mel_spectrogram(audio_trim).to(model.device)

# detect the spoken language
_, probs = model.detect_language(mel)
det_lang = max(probs, key=probs.get)

# decode the audio
options = whisper.DecodingOptions(language=det_lang)

# result = whisper.decode(model, mel, options)
result = model.transcribe(audio, language=det_lang)

# print the recognized text and language
print(result["text"])
print(det_lang)

response = requests.post(
    "http://localhost:8000/chat",
    json={"content": result["text"]}
)

#Reponse Text output
print(response.text)

client = ElevenLabs(
  api_key="41f1d61b1ce48269216086555aa78d33",
)


audio = client.generate(
    text=response.text,
    voice="Chris",
    model='eleven_multilingual_v1'
)

#print("Time elapsed for generating:", end - start)
play(audio)