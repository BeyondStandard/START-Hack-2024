import asyncio
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

load_dotenv()

# Define API keys and voice ID
OPENAI_API_KEY = os.environ["OPENAI_API_KEY"]
ELEVENLABS_API_KEY = os.environ["ELEVENLABS_KEY"]
VOICE_ID = "iP95p4xoKVk53GoZ742B"

# Set OpenAI API key
aclient = AsyncOpenAI(api_key=OPENAI_API_KEY)


async def main():
    # Load and process audio file with Whisper (synchronous part)
    file_path = "gras.mp3"
    start = datetime.now()
    audio = whisper.load_audio(file_path)
    model = whisper.load_model("base")
    audio_trim = whisper.pad_or_trim(audio)
    mel = whisper.log_mel_spectrogram(audio_trim).to(model.device)
    _, probs = model.detect_language(mel)
    det_lang = max(probs, key=probs.get)
    result = model.transcribe(audio, language=det_lang)
    print(result["text"])

    speech_to_text_duration = datetime.now() - start
    print(f"Speech to text duration: {speech_to_text_duration}")

    # Asynchronous chat completion and text-to-speech conversion
    await chat_completion(result["text"])


def do_sentiment_analysis(text):
    subprocess.Popen(["python", "sentiment-analysis-request.py", text])

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
    async for chunk in audio_stream:
        if chunk:
            mpv_process.stdin.write(chunk)
            mpv_process.stdin.flush()

    if mpv_process.stdin:
        mpv_process.stdin.close()
    mpv_process.wait()


async def text_to_speech_input_streaming(voice_id, text_iterator):
    """Send text to ElevenLabs API and stream the returned audio."""
    uri = f"wss://api.elevenlabs.io/v1/text-to-speech/{voice_id}/stream-input?model_id=eleven_multilingual_v1"

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
        do_sentiment_analysis(text)
        
        await websocket.send(json.dumps({"text": ""}))

        await listen_task


async def chat_completion(query):
    """Retrieve text from OpenAI and pass it to the text-to-speech function."""
    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": query}],
        temperature=1,
        stream=True,
    )

    async def text_iterator():
        async for chunk in response:
            delta = chunk.choices[0].delta
            yield delta.content

    await text_to_speech_input_streaming(VOICE_ID, text_iterator())


# Main execution
if __name__ == "__main__":
    asyncio.run(main())
