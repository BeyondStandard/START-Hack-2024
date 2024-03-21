## GPT3.5 Chatter

Built for Canton Of St. Gallen challenge, START Hack 2024.

### Built With

The backend is written in Python **3.10.0** and utilizes the `FastAPI` framework along with `pydantic` data
models. `Uvicorn` serves as
the ASGI server to run the application.

The application is accessible at `http:localhost:8000`, and POST requests should be directed
to `/chat`.

The core application logic resides in `app.py`.

### Run locally

To get a local copy up and running follow these simple steps.

#### 1. Clone the repository
```shell
go install github.com/desertbit/grml@latest
```

```python
# Python
import json
import requests

request = json.dumps(
    {
        "content": "Hi, how are you?",
    }
)
response = requests.post(
    "http://localhost:8000/chat",
    data=request
)
print(json.dumps(response.json(), indent=2))
```

## Alternate Installation
If Anaconda is installed, use the following commands to run the pipeline:

`conda env create -f environment.yml`
`python runner.py`