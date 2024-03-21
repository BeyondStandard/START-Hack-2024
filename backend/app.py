import base64
import json
import logging
import os
import sys
import time

import dotenv
import openai
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain.chains import RetrievalQA
from langchain.prompts.prompt import PromptTemplate
from langchain_community.vectorstores import Chroma
from langchain_openai import OpenAI, OpenAIEmbeddings

from . import datamodel, prompt_constants

dotenv.load_dotenv()
app = FastAPI()
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)
file_handler = logging.FileHandler("log_file.log")
file_handler.setLevel(logging.DEBUG)
websocket_clients = set()


@app.post("/chat")
def main(message: datamodel.ChatMessage):
    async def stream():
        prompt = PromptTemplate(
            template=prompt_constants.PROMPT_TEMPLATE_DE,
            input_variables=["context", "question"],
        )
        vectordb = Chroma(
            embedding_function=OpenAIEmbeddings(model="text-embedding-3-small"),
            persist_directory="./vectordb",
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(
                streaming=True,
                callbacks=[StreamingStdOutCallbackHandler()],
                temperature=0,
                openai_api_key=os.environ["OPENAI_API_KEY"],
            ),
            retriever=vectordb.as_retriever(search_kwargs={"k": 10}),
            chain_type_kwargs={"prompt": prompt},
        )
        response_stream = qa_chain.invoke({"query": message.content})
        yield response_stream["result"]

        """
        buffered_text = ""
        for chunk in response_stream["result"]:
            # content = chunk.choices[0].delta.content
            content = chunk
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
        """

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
    print(f"sentiment prediction: {prediction}", file=sys.stderr)
    for client in websocket_clients:
        await client.send_text(json.dumps(prediction))
        break  # TODO: Prevent sending it twice to the frontend

    return prediction


@app.websocket("/media")
async def websocket_endpoint(websocket: WebSocket):
    logger.info("Connection accepted")
    # A lot of messages will be sent rapidly. We'll stop showing after the first one.
    has_seen_media = False
    message_count = 0
    await websocket.accept()
    while True:
        data = await websocket.receive_text()
        message = json.loads(data)
        if message is None:
            logger.info("No message received...")
            continue

        # Using the event type you can determine what type of message you are receiving
        if message["event"] == "connected":
            logger.info("Connected Message received: {}".format(data))
        if message["event"] == "start":
            logger.info("Start Message received: {}".format(data))
        if message["event"] == "media":
            if not has_seen_media:
                logger.info("Media message: {}".format(data))
                payload = message["media"]["payload"]
                logger.info("Payload is: {}".format(payload))
                chunk = base64.b64decode(payload)
                logger.info("That's {} bytes".format(len(chunk)))
                logger.info(
                    "Additional media messages from WebSocket are being suppressed...."
                )
                has_seen_media = True
        if message["event"] == "closed":
            logger.info("Closed Message received: {}".format(data))
            break
        message_count += 1

    logger.info(
        "Connection closed. Received a total of {} messages".format(message_count)
    )
