import os
import time

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from openai import OpenAI

from datamodel import ChatMessage

load_dotenv()
app = FastAPI()


@app.post("/chat")
def main(message: ChatMessage):
    def stream():
        client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        response_stream = client.chat.completions.create(
            model=os.environ["OPENAI_MODEL_NAME"],
            messages=[message.model_dump()],
            stream=True,
        )

        buffered_text = ""
        for chunk in response_stream:
            content = chunk.choices[0].delta.content
            if content:
                buffered_text += content
                if '.' in buffered_text or '?' in buffered_text or '!' in buffered_text:
                    last_period = max(buffered_text.rfind('.'), buffered_text.rfind('?'), buffered_text.rfind('!'))
                    sentence = buffered_text[:last_period + 1]
                    buffered_text = buffered_text[last_period + 1:]
                    yield sentence + "\n"

        # Yield any remaining text after the loop finishes
        if buffered_text:
            yield buffered_text

    return StreamingResponse(stream())


@app.post("/test-stream")
def test_stream(message: ChatMessage):
    def generate_numbers():
        for i in range(1, 11):
            yield f"{i}\n"
            time.sleep(1)  # Simulate delay

    return StreamingResponse(generate_numbers(), media_type="text/plain")
