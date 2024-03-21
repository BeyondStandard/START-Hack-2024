import json
import os
import sys
import time

import openai
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from openai import OpenAI

from datamodel import ChatMessage

load_dotenv()
app = FastAPI()
websocket_clients = set()


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
                if "." in buffered_text or "?" in buffered_text or "!" in buffered_text:
                    last_period = max(
                        buffered_text.rfind("."),
                        buffered_text.rfind("?"),
                        buffered_text.rfind("!"),
                    )
                    sentence = buffered_text[: last_period + 1]
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


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    websocket_clients.add(websocket)
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        websocket_clients.remove(websocket)


@app.post("/sentiment-analysis")
async def main(message: ChatMessage):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    message.content = (
        f"Classify the sentiment into positive, negative or neutral:\n{message.content}"
    )
    response = openai.chat.completions.create(
        model=os.environ["OPENAI_MODEL_NAME"],
        messages=[message.model_dump()],
    )

    prediction = {"value": response.choices[0].message.content, }
    print(prediction, file=sys.stderr)
    for client in websocket_clients:
        await client.send_text(json.dumps(prediction))
        break  # TODO: Prevent sending it twice to the frontend

    return prediction
