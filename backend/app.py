from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.vectorstores import Chroma
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_core.callbacks.base import BaseCallbackHandler

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse

import asyncio
import logging
import base64
import dotenv
import openai
import typing
import json
import time
import sys
import os

from pydantic import BaseModel
import traceback

# noinspection PyPackages
from . import prompt_constants, datamodel
from .datamodel import ChatMessage

# Load environment variables
dotenv.load_dotenv()

# Logger constants
LOGGER_DATE_FORMAT: typing.Final[str] = '%H:%M:%S'
LOGGER_FORMAT: typing.Final[str] = \
    '%(asctime)s.%(msecs)03d | [%(lineno)3s] %(levelname)-9s| %(message)s'
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

#aclient = AsyncOpenAI(api_key=os.environ['OPENAI_API_KEY'])
VOICE_ID = "iP95p4xoKVk53GoZ742B"


class TokenCallbackHandler(BaseCallbackHandler):
    def __init__(self):
        super().__init__()
        self.tokens = []

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.tokens.append(token)

    def request_token(self):
        if self.tokens:
            return self.tokens.pop(0)


class GPTChatter:
    def __init__(self):
        self.complete = None
        self.callback = TokenCallbackHandler()

        prompt = PromptTemplate(
            template=prompt_constants.PROMPT_TEMPLATE_DE,
            input_variables=['context', 'question'],
        )
        vectordb = Chroma(
            embedding_function=OpenAIEmbeddings(
                model=os.environ['embeddingModel']),
            persist_directory='data/vectordb',
        )
        self.qa_chain: RetrievalQA = RetrievalQA.from_chain_type(
            llm=OpenAI(
                streaming=True,
                callbacks=[self.callback],
                temperature=0,
                openai_api_key=os.environ['OPENAI_API_KEY'],
            ),
            retriever=vectordb.as_retriever(search_kwargs={'k': 10}),
            chain_type_kwargs={'prompt': prompt},
        )

    def _ask(self, message: str) -> dict[str, typing.Any]:
        return self.qa_chain.invoke({'query': message})

    async def ask(self, message: str) -> dict[str, typing.Any]:
        self.complete = False
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(
            None, self._ask, message)

        self.complete = True
        return result

    async def get_response(self):
        while not self.complete:
            if token := self.callback.request_token():
                yield token

            else:
                await asyncio.sleep(0.1)


chatter = GPTChatter()


@app.post('/chat')
async def main(message: datamodel.ChatMessage):
    _ = asyncio.create_task(chatter.ask(message.content))
    resposne_stream = asyncio.create_task(chatter.get_response())

    return StreamingResponse(resposne_stream, media_type='text/plain')


"""
async def chat_completion(query):
    response = await aclient.chat.completions.create(
        model="gpt-3.5-turbo-0125",
        messages=[{"role": "user", "content": query}],
        temperature=1,
        stream=True,
    )

    text_responses = []

    async for chunk in response:
        delta = chunk.choices[0].delta
        text_responses.append(delta.content)

    return text_responses


@app.post("/basicchat/")
async def chat_endpoint(chat_query: ChatQuery):
    try:
        responses = await chat_completion(chat_query.query)
        return {"responses": responses}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
"""


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
        f"Classify the sentiment into positive, negative or neutral and identify the most fitting emotion. Return the result in a JSON format with 'emotion' and 'sentiment' as keys:\n{message.content}."
    )
    response = openai.chat.completions.create(
        model=os.environ["OPENAI_MODEL_NAME"],
        messages=[message.model_dump()],
    )

    prediction = [response.choices[0].message.content.lower()]
    logger.info(f"sentiment prediction: {prediction}", file=sys.stderr)
    for client in websocket_clients:
        await client.send_text(prediction)
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
