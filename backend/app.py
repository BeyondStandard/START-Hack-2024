from langchain.chains.retrieval_qa.base import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain_core.callbacks.base import BaseCallbackHandler
from langchain.prompts.prompt import PromptTemplate
from langchain_openai import OpenAI, OpenAIEmbeddings

from fastapi.responses import StreamingResponse
from fastapi import FastAPI

import langsmith
import datetime
import asyncio
import logging
import dotenv
import openai
import typing
import json
import uuid
import os

from backend import prompt_constants, datamodel, stt

# Load environment variables
dotenv.load_dotenv()

# Langchain environment variables
os.environ["LANGCHAIN_PROJECT"] = f"Tracing - {uuid.uuid4().hex[:8]}"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"

# Logger constants
LOGGER_DATE_FORMAT: typing.Final[str] = "%H:%M:%S"
LOGGER_FORMAT: typing.Final[str] = (
    "%(asctime)s.%(msecs)03d | [%(lineno)3s] %(levelname)-9s| %(message)s"
)
FILE_LOGGER_FORMATTER = logging.Formatter(LOGGER_FORMAT, LOGGER_DATE_FORMAT)
FILE_LOGGER_NAME: typing.Final[str] = "log_file.log"
FILE_LOGGER_LEVEL: typing.Final[int] = logging.DEBUG

# Set up file logging
file_handler = logging.FileHandler(FILE_LOGGER_NAME, mode="w")
file_handler.setFormatter(FILE_LOGGER_FORMATTER)
file_handler.setLevel(FILE_LOGGER_LEVEL)

# Set up logging
logger = logging.getLogger("uvicorn")
logger.addHandler(file_handler)

# Set up everything
app = FastAPI()
client = langsmith.Client()
websocket_clients = set()


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
            input_variables=["context", "question"],
        )
        vectordb = Chroma(
            persist_directory="data/vectordb",
            embedding_function=OpenAIEmbeddings(model=os.environ["embeddingModel"]),
        )
        r = vectordb.as_retriever(search_kwargs={'k': 5})
        self.qa_chain = RetrievalQA.from_chain_type(
            llm=OpenAI(
                streaming=True,
                callbacks=[self.callback],
                temperature=0,
                openai_api_key=os.environ["OPENAI_API_KEY"],
            ),
            retriever=r,
            chain_type_kwargs={"prompt": prompt},
        )

    def _ask(self, message: str) -> dict[str, typing.Any]:
        return self.qa_chain.invoke({"query": message})

    async def _response(self):
        while not self.complete:
            if token := self.callback.request_token():
                yield token

            else:
                await asyncio.sleep(0)

    async def ask(self, message: str) -> dict[str, typing.Any]:
        self.complete = False
        loop = asyncio.get_running_loop()
        result = await loop.run_in_executor(None, self._ask, message)

        self.complete = True
        return result

    async def response(self):
        async for item in self._response():
            yield item


chatter = GPTChatter()


# Return the complete response from the GPT model
@app.post("/chat")
async def chat_endpoint(message: datamodel.ChatMessage):
    response = await asyncio.create_task(chatter.ask(message.content))
    for key, value in response.items():
        logger.info(f"{key}: {value}")

    return response["result"]


# Stream the response from the GPT model
@app.post("/stream")
def stream_endpoint(message: datamodel.ChatMessage):
    _ = asyncio.create_task(chatter.ask(message.content))
    return StreamingResponse(chatter.response(), media_type="text/plain")


@app.get("/stt")
async def stt_endpoint():
    asyncio.run(stt.main())


@app.post("/sentiment-analysis")
async def sentiment_analysis_endpoint(message: datamodel.ChatMessage):
    openai.api_key = os.environ["OPENAI_API_KEY"]
    message.content = (
        f"Classify the sentiment into positive, negative or neutral "
        f"and identify the most fitting emotion. Return the result in a "
        f"JSON format with 'emotion' and 'sentiment' as keys:\n{message.content}."
    )
    response = openai.chat.completions.create(
        model=os.environ["gptModel"],
        messages=[message.model_dump()],
    )

    prediction = json.loads(response.choices[0].message.content.lower())
    prediction["timestamp"] = datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%SZ")
    json_path = os.path.join("frontend", "ratings.json")
    with open(json_path, "r") as f:
        data = json.load(f)
        data.append(prediction)
    with open(json_path, "w") as f:
        json.dump(data, f, indent=4)

    logger.info(f"[sentiment / emotion analysis] {prediction}")
    for client in websocket_clients:
        await client.send_text(prediction)
        break  # TODO: Prevent sending it twice to the frontend

    return prediction
