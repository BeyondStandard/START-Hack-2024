import os

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

        for chunk in response_stream:
            if chunk.choices[0].delta.content is not None:
                yield chunk.choices[0].delta.content

    return StreamingResponse(stream())
