from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler
from langchain_community.vectorstores import Chroma
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import OpenAI, OpenAIEmbeddings
from langchain.chains import RetrievalQA

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import StreamingResponse, Response

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
from .speech_to_text import do_speech_to_text

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
        yield response_stream['result']

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


@app.post("/voice")
async def voice(request: Request):
    """Accept phone call and redirect to websocket endpoint (doesn't work) :(
    https://www.twilio.com/docs/voice/twiml/stream
    https://www.twilio.com/docs/voice/tutorials/consume-real-time-media-stream-using-websockets-python-and-flask
    Alternative: https://help.twilio.com/articles/230878368-How-to-use-templates-with-TwiML-Bins ?
    """
    logger.info(f"Received an incoming call")

    twiml = """
    <Response>
        <Say>Hello, we will start processing your call now.</Say>
        <Start>
            <Stream url="wss://sweeping-maggot-informed.ngrok-free.app/media"/>
        </Start>
    </Response>
    """

    resp = Response(content=twiml, media_type="text/xml")

    return resp


@app.websocket("/media")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()

    async for message in websocket.iter_text():
        data = json.loads(message)

        if data['event'] == "media":
            payload = data["media"]["payload"]
            audio = base64.b64decode(payload)
            response = do_speech_to_text(audio)

            # If your STT service response is a sequence of words,
            # you may want to join them into a complete sentence.
            text = ' '.join(response)

            # Now you have the transcribed text!
            print(text)

    print("Connection closed.")