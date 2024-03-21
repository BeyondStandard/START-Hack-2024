import os
import sys

import openai
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

openai.api_key = os.environ["OPENAI_API_KEY"]


def get_sentiment(text):
    response = openai.chat.completions.create(
        model=os.environ["OPENAI_MODEL_NAME"],
        messages=[
            {
                "content": "Claasify the sentiment into positive, negative or neutral:"
                + str(text),
                "role": "user",
            }
        ],
    )

    sentiment = response.choices[0].message.content
    return sentiment


if __name__ == "__main__":
    # text = input("Enter the text to analyze: ")
    text = sys.argv[1]
    sentiment = get_sentiment(text)
    print(f"The sentiment of the text is {sentiment}")
