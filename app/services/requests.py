import app.settings
import requests as rq
import time
import random
from json import JSONDecodeError
from typing import Literal
from tkinter.messagebox import showerror
from app.services.utils import get_validation_key
from app.gui.context import AppContext


def make_request(method: Literal["get", "post"], endpoint: str, data: dict | None = None,
                 with_loading_window: bool = True, with_token: bool = False) -> tuple[int, dict]:
    if with_token:
        token: str | None = get_validation_key()

        if not token:
            return 1, {}

        headers = {"Authorization": f"Bearer {token}"}
    else:
        headers: dict | None = None

    if with_loading_window:
        AppContext.loading_window.start_loading()

    time_ = time.time()

    try:
        url: str = f"http://{app.settings.url}/{endpoint}"
        response: rq.Response = rq.post(url, json=data) if method == "post" else rq.get(url, headers=headers,
                                                                                        params=data)

        if with_loading_window:
            while time.time() - time_ < random.uniform(0.5, 1.0):
                time.sleep(0.03)

            AppContext.loading_window.finish_loading()

        try:
            return response.status_code, response.json()
        except (JSONDecodeError, ValueError):
            return response.status_code, {}
    except rq.exceptions.ConnectionError:
        if with_loading_window:
            while time.time() - time_ < random.uniform(0.5, 1.0):
                time.sleep(0.03)

            AppContext.loading_window.finish_loading()

        showerror("Error", "Server is not available. Please try again later.")
        return 0, {}

