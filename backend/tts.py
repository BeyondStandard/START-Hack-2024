from elevenlabs.client import ElevenLabs
from elevenlabs import play
from datetime import datetime
from pydub import AudioSegment, playback

import subprocess
import requests
import whisper
import dotenv
import json
import sys
import io
import os


dotenv.load_dotenv()

client = ElevenLabs(api_key=os.environ["ELEVENLABS_KEY"])
PLAYHT_UID = os.getenv("PLAYHT_UID")
PLAYHT_KEY = os.getenv("PLAYHT_KEY")


def do_sentiment_analysis(text):
    subprocess.Popen(
        ["python", os.path.join("backend", "sentiment-analysis-request.py"), text]
    )


def do_speech_to_text(file_path):
    # To add twilio/phone app thingy
    # file_path = "test_swiss_german.mp3"
    # print(sys.argv)
    # file_path = sys.argv[1]  # "recorded.mp3"

    start = datetime.now()
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
    do_sentiment_analysis(result["text"])
    # print the recognized text and language
    # print(result["text"])
    # print(det_lang)
    speech_to_text = datetime.now() - start
    print("Speech to text: " + str(speech_to_text))
    print_response_time = True

    response = requests.post(
        "http://localhost:8000/chat",
        json={"content": result["text"]},
        stream=True,
    )

    # Time when the request was sent (for measuring GPT response time)
    time_stamp_request_sent = datetime.now()

    for line in response.iter_lines():
        if line:
            # Decode the line to get the sentence
            sentence = line.decode("utf-8")
            print(sentence)

            # If this is the first line, print the time taken by GPT to respond
            if print_response_time:
                time_stamp_first_response = datetime.now()
                gpt_response_time = time_stamp_first_response - time_stamp_request_sent
                print("Time for first GPT response: " + str(gpt_response_time))
                print_response_time = False

            # Time when text-to-speech starts (for measuring text-to-speech time)
            time_stamp_text_to_speech_start = datetime.now()

            if os.environ["swissVoice"] == "false":
                audio = client.generate(
                    text=sentence,
                    voice=os.environ["voice"],
                    model="eleven_multilingual_v1",
                )
            else:
                audio = tts_swiss(sentence)
                # TODO: 'tts_swiss' doesn't return anything

            # Calculate the time taken for text-to-speech conversion
            text_to_speech_time = datetime.now() - time_stamp_text_to_speech_start
            print("Text-to-Speech time: " + str(text_to_speech_time))

            # Play the audio or process it as needed
            print("Playing audio")
            play(audio)
            print("Audio played")
            os.system("python backend/stt.py")

    # print("Time elapsed for generating:", end - start)
    # print("Text to speech: "+str(text_to_speech))


def tts_swiss(text):
    start_time = datetime.now()
    url = "https://api.play.ht/api/v1/convert"

    payload = {"content": [text], "voice": "de-CH-LeniNeural"}
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "AUTHORIZATION": PLAYHT_KEY,
        "X-USER-ID": PLAYHT_UID,
    }

    response = requests.post(url, json=payload, headers=headers)

    print(response.text)
    print(json.loads(response.text))

    url = (
        "https://api.play.ht/api/v1/articleStatus?transcriptionId="
        + json.loads(response.text)["transcriptionId"]
    )

    converted = False
    while not converted:
        response = requests.get(url, headers=headers)
        print(json.loads(response.text))
        if json.loads(response.text)["converted"]:
            converted = True

    response = requests.get(url, headers=headers)
    mp3_url = json.loads(response.text)["audioUrl"]

    response = requests.get(mp3_url)
    audio_data = io.BytesIO(response.content)

    # Load the audio file using pydub
    audio = AudioSegment.from_file(audio_data, format="mp3")

    # Play the audio file
    print("Time elapsed for generating:", datetime.now() - start_time)
    playback.play(audio)


if __name__ == "__main__":
    if len(sys.argv) > 0:
        path = sys.argv[1]
        sys.argv = [sys.argv[0]]
        do_speech_to_text(path)
