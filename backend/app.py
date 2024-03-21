from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.vectorstores import Chroma
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain.chains import RetrievalQA

from fastapi.responses import StreamingResponse
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

import dotenv
import openai
import json
import time
import sys
import os

from . import prompt_constants
from . import datamodel


dotenv.load_dotenv()
app = FastAPI()
websocket_clients = set()


@app.post("/chat")
def main(message: datamodel.ChatMessage):
    def stream():
        prompt = PromptTemplate(
            template=prompt_constants.PROMPT_TEMPLATE_DE,
            input_variables=["context", "question"]
        )
        vectordb = Chroma(
            embedding_function=OpenAIEmbeddings(model='text-embedding-3-small'),
            persist_directory='./vectordb', )
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(
                streaming=True,
                callbacks=[StreamingStdOutCallbackHandler()],
                temperature=0,
                openai_api_key=os.environ["OPENAI_API_KEY"]
            ),
            retriever=vectordb.as_retriever(search_kwargs={'k': 10}),
            chain_type_kwargs={'prompt': prompt}
        )
        response_stream = qa_chain.invoke({'query': message.content})

        # client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
        # response_stream = client.chat.completions.create(
        #     model=os.environ["OPENAI_MODEL_NAME"],
        #     messages=[message.model_dump()],
        #     stream=True,
        # )

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
                    buffered_text = buffered_text[last_period + 1 :]
                    yield sentence + "\n"

        # Yield any remaining text after the loop finishes
        if buffered_text:
            yield buffered_text

    return StreamingResponse(stream())


@app.post("/test-stream")
def test_stream(message: datamodel.ChatMessage):
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
async def main(message: datamodel.ChatMessage):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    message.content = (
        f"Classify the sentiment into positive, negative or neutral:\n{message.content}"
    )
    response = openai.chat.completions.create(
        model=os.environ["OPENAI_MODEL_NAME"],
        messages=[message.model_dump()],
    )

    prediction = {
        "value": response.choices[0].message.content,
    }
    print(prediction, file=sys.stderr)
    for client in websocket_clients:
        await client.send_text(json.dumps(prediction))
        break  # TODO: Prevent sending it twice to the frontend

    return prediction
