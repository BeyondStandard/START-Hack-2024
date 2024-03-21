import sys

import requests


def sentiment_analysis(content):
    print(content)
    res = requests.post(
        "http://localhost:8000/sentiment-analysis",
        json={"content": content},
    )

    print(res.text)


if __name__ == "__main__":
    _content = sys.argv[1]
    sentiment_analysis(_content)
