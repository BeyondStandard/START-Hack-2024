from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.vectorstores import Chroma
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

import logging
import base64
import dotenv
import openai
import typing
import json
import time
import sys
import os

# noinspection PyPackages
from . import prompt_constants, datamodel

# Load environment variables
dotenv.load_dotenv()

# Logger constants
LOGGER_DATE_FORMAT: typing.Final[str] = '%H:%M:%S'
LOGGER_FORMAT: typing.Final[str] = \
    '%(asctime)s | [%(lineno)3s] %(levelname)-9s| %(message)s'
FILE_LOGGER_FORMATTER = logging.Formatter(LOGGER_FORMAT, LOGGER_DATE_FORMAT)
FILE_LOGGER_NAME: typing.Final[str] = 'log_file.log'
FILE_LOGGER_LEVEL: typing.Final[int] = logging.DEBUG

# Set up file logging
file_handler = logging.FileHandler(FILE_LOGGER_NAME, mode='w')
file_handler.setFormatter(FILE_LOGGER_FORMATTER)
file_handler.setLevel(FILE_LOGGER_LEVEL)

# Set up logging
logger = logging.getLogger('uvicorn')
logger.addHandler(file_handler)

# Set up FastAPI
app = FastAPI()
websocket_clients = set()


@app.post('/chat')
def main(message: datamodel.ChatMessage):
    async def stream():
        prompt = PromptTemplate(
            template=prompt_constants.PROMPT_TEMPLATE_DE,
            input_variables=['context', 'question'],
        )
        vectordb = Chroma(
            embedding_function=OpenAIEmbeddings(
                model=os.environ['embeddingModel']),
            persist_directory='./vectordb',
        )
        qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(
                streaming=True,
                callbacks=[StreamingStdOutCallbackHandler()],
                temperature=0,
                openai_api_key=os.environ['OPENAI_API_KEY'],
            ),
            retriever=vectordb.as_retriever(search_kwargs={'k': 10}),
            chain_type_kwargs={'prompt': prompt},
        )
        response_stream = qa_chain.invoke({'query': message.content})
        yield response_stream['result'] + '\n'

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
        f"Classify the sentiment into positive, negative or neutral and give a probability of different emotions:\n{message.content}"
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
        if message['event'] == 'connected':
            logger.info("Connected Message received: {}".format(data))
        if message['event'] == 'start':
            logger.info("Start Message received: {}".format(data))
        if message['event'] == 'media':
            if not has_seen_media:
                logger.info("Media message: {}".format(data))
                payload = message['media']['payload']
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
