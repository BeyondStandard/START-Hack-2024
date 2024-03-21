import asyncio
import aiohttp
import httpx
import base64
import datetime
import json
import os
import shutil
import subprocess
from datetime import datetime

import websockets
import whisper
from dotenv import load_dotenv
from openai import AsyncOpenAI


text_to_speech_start_time = None
gpt_start_time = None


load_dotenv()

# Define API keys and voice ID
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_KEY"]
VOICE_ID = "iP95p4xoKVk53GoZ742B"

# Set OpenAI API key
aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)


def do_sentiment_analysis(text):
    subprocess.Popen(["python", os.path.join("backend", "sentiment-analysis-request.py"), text])


async def main():
    # Load and process audio file with Whisper (synchronous part)
    file_path = "gras.mp3"
    start = datetime.now()
    audio = whisper.load_audio(file_path)
    model = whisper.load_model("base")
    audio_trim = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio_trim).to(model.device)

    # Detects language that the speaker is using and chooses model accordingly
    _, probs = model.detect_language(mel)
    det_lang = max(probs, key=probs.get)
    result = model.transcribe(audio, language=det_lang)
    print(result["text"])

    speech_to_text_duration = datetime.now() - start

    # do_sentiment_analysis(result["text"])
    print(f"Speech to text duration: {speech_to_text_duration}")

    global gpt_start_time
    gpt_start_time = datetime.now()

    # Asynchronous chat completion and text-to-speech conversion
    await chat_completion(result["text"])


def is_installed(lib_name):
    return shutil.which(lib_name) is not None


async def text_chunker(chunks):
    """Split text into chunks, ensuring to not break sentences."""
    splitters = (".", ",", "?", "!", ";", ":", "—", "-", "(", ")", "[", "]", "}", " ")
    buffer = ""

    async for text in chunks:
        if text is None:
            continue  # Skip None values
        if buffer.endswith(splitters):
            yield buffer + " "
            buffer = text
        elif text.startswith(splitters):
            yield buffer + text[0] + " "
            buffer = text[1:]
        else:
            buffer += text

    if buffer:
        yield buffer + " "


async def stream(audio_stream):
    """Stream audio data using mpv player."""
    global text_to_speech_start_time
    if not is_installed("mpv"):
        raise ValueError(
            "mpv not found, necessary to stream audio. "
            "Install instructions: https://mpv.io/installation/"
        )

    mpv_process = subprocess.Popen(
        ["mpv", "--no-cache", "--no-terminal", "--", "fd://0"],
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    print("Started streaming audio")
    first_chunk = True
    async for chunk in audio_stream:
        if chunk:
            if first_chunk:
                # Messung der Zeit bis zum Beginn der Sprachausgabe
                speech_start_duration = datetime.now() - text_to_speech_start_time
                print(f"Time until speech starts: {speech_start_duration}")
                first_chunk = False
            mpv_process.stdin.write(chunk)
            mpv_process.stdin.flush()

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()


async def text_to_speech_input_streaming(voice_id, text_iterator):
    """Send text to ElevenLabs API and stream the returned audio."""
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_multilingual_v1"
    global text_to_speech_start_time
    text_to_speech_start_time = datetime.now()

    async with websockets.connect(uri) as websocket:
        await websocket.send(
            json.dumps(
                {
                    "text": " ",
                    "voice_settings": {"stability": 0.5, "similarity_boost": 0.8},
                    "xi_api_key": ELEVENLABS_API_KEY,
                }
            )
        )

        async def listen():
            """Listen to the websocket for audio data and stream it."""
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    if data.get("audio"):
                        yield base64.b64decode(data["audio"])
                    elif data.get("isFinal"):
                        break
                except websockets.exceptions.ConnectionClosed:
                    print("Connection closed")
                    break

        listen_task = asyncio.create_task(stream(listen()))

        async for text in text_chunker(text_iterator):
            await websocket.send(
                json.dumps({"text": text, "try_trigger_generation": True})
            )

        await websocket.send(json.dumps({"text": ""}))

        await listen_task


async def chat_completion(query):
    """Retrieve text from the server and pass it to the text-to-speech function."""
    url = 'http://localhost:8000/chat/'  # Replace with your actual server URL if different

    # Mark the start time before sending the request
    request_start_time = datetime.now()

    # Use aiohttp to send the query to the server
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json={"query": query}) as response:
            # Ensure the request was successful
            response.raise_for_status()

            # Parse the JSON response containing the text responses
            data = await response.json()

    # Extract the text responses from the server's response
    text_responses = data['response']  # Adjust if the key is different

    # Print the time it takes until the first sentence is received
    first_response_duration = datetime.now() - request_start_time
    print(f"Time until first sentence is received: {first_response_duration}")

    # Define the text_iterator as an asynchronous generator
    async def text_iterator():
        for content in text_responses:
            # Print each sentence as it is received
            print(content)
            yield content

    # Pass the text responses to the text-to-speech function
    await text_to_speech_input_streaming(VOICE_ID, text_iterator())



# Main execution
if __name__ == "__main__":
    asyncio.run(main())
