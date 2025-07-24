import app.settings
import requests as rq
from json import JSONDecodeError


def make_request(endpoint: str, data: dict) -> tuple[int, dict]:
    response: rq.Response = rq.post(f"{app.settings.url}/{endpoint}", json=data)
    try:
        return response.status_code, response.json()
    except (JSONDecodeError, ValueError):
        return response.status_code, {}
