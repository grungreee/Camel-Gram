import app.settings
import requests as rq
from json import JSONDecodeError
from typing import Literal
from tkinter.messagebox import showerror
from app.gui.context import AppContext


def make_request(method: Literal["get", "post"], endpoint: str, data: dict,
                 with_loading_window: bool = True) -> tuple[int, dict]:
    if with_loading_window:
        AppContext.loading_window.start_loading()

    try:
        response: rq.Response = rq.post(f"{app.settings.url}/{endpoint}", json=data) if method == "post" else (
                                rq.get(f"{app.settings.url}/{endpoint}", headers=data))

        if with_loading_window:
            AppContext.loading_window.finish_loading()

        try:
            return response.status_code, response.json()
        except (JSONDecodeError, ValueError):
            return response.status_code, {}
    except rq.exceptions.ConnectionError:
        if with_loading_window:
            AppContext.loading_window.finish_loading()

        showerror("Error", "Server is not available. Please try again later.")
        return 0, {}
