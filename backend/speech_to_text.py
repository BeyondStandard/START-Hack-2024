import os
import subprocess
from datetime import datetime

import requests
import whisper
from elevenlabs import play
from elevenlabs.client import ElevenLabs

import sys

def do_sentiment_analysis(text):
    subprocess.Popen(["python", os.path.join("backend","sentiment-analysis-request.py"), text])

def do_speech_to_text():
    # To add twilio/phone app thingy
    # file_path = "test_swiss_german.mp3"
    file_path = sys.argv[1] #"recorded.mp3"

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
    time_stamp_1 = datetime.now()
    print("Speech to text: " + str(speech_to_text))

    client = ElevenLabs(
        api_key="41f1d61b1ce48269216086555aa78d33",
    )

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

            # Perform text-to-speech on the sentence
            audio = client.generate(
                text=sentence, voice="Chris", model="eleven_multilingual_v1"
            )

            # Calculate the time taken for text-to-speech conversion
            text_to_speech_time = datetime.now() - time_stamp_text_to_speech_start
            print("Text-to-Speech time: " + str(text_to_speech_time))

            # Play the audio or process it as needed
            print("Playing audio")
            play(audio)
            print("Audio played")

    # print("Time elapsed for generating:", end - start)
    # print("Text to speech: "+str(text_to_speech))


do_speech_to_text()
