import app.settings
import requests as rq
from json import JSONDecodeError
from typing import Literal


def make_request(method: Literal["get", "post"], endpoint: str, data: dict) -> tuple[int, dict]:
    response: rq.Response = rq.post(f"{app.settings.url}/{endpoint}", json=data) if method == "post" else (
                            rq.get(f"{app.settings.url}/{endpoint}", headers=data))
    try:
        return response.status_code, response.json()
    except (JSONDecodeError, ValueError):
        return response.status_code, {}
