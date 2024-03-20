## GPT3.5 Chatter
Built for Canton Of St. Gallen challenge, START Hack 2024.

### Built With
The backend is written in Python **3.12.0** and utilizes the `FastAPI` framework along with `pydantic` data
models. `Uvicorn` serves as
the ASGI server to run the application.

The application is accessible at `http:localhost:8000`, and POST requests should be directed
to `/chat`.

The core application logic resides in `app.py`.

### Run locally

To get a local copy up and running follow these simple steps.

#### 1. Create a virtual environment

```shell
python3 -m venv .venv 
source .venv/bin/activate
```

#### 2. Install dependencies

```shell
pip install poetry
poetry install --no-root
```

#### 3. Run the app

```shell
uvicorn app.app:app --reload --port 8000
```

#### 4. Send requests

Examples:

```shell
# Shell
curl -X POST -H "Content-Type: application/json" -d '{
  "cart_value": "790",
  "delivery_distance": "2635",
  "number_of_items": "4",
  "time": "2024-01-18T17:30:00Z"
}' http://localhost:8000/calculate-delivery-fee
```

```python
# Python
import json
import requests

request = json.dumps(
    {
        "cart_value": "790",
        "delivery_distance": "2635",
        "number_of_items": "4",
        "time": "2024-01-18T17:30:00Z",
    }
)
response = requests.post(
    "http://localhost:8000/calculate-delivery-fee",
    data=request
)
print(json.dumps(response.json(), indent=2))
```

### Testing

`pytest` is used for tests. The project has a 100% pytest coverage which can be checked by running:

```shell
pytest --cov=. --cov-report=html
open htmlcov/index.html
```