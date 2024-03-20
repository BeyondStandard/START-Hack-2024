'''
from openai import OpenAI
client = OpenAI(api_key = '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')

audio_file= open("test_swiss_german.mp3", "rb")
transcription = client.audio.transcriptions.create(
  model="whisper-1", 
  file=audio_file
)
print(transcription.text)
'''

import whisper

file_path = 'test_swiss_german.mp3'

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
options = whisper.DecodingOptions(language = det_lang)

#result = whisper.decode(model, mel, options)
result = model.transcribe(audio, language=det_lang)

# print the recognized text and language
print(result["text"])
print(det_lang)

prompt = result['text']

