import app.settings
import requests as rq
from json import JSONDecodeError
from typing import Literal
from tkinter.messagebox import showerror
from app.gui.context import AppContext


def make_request(method: Literal["get", "post"], endpoint: str, data: dict) -> tuple[int, dict]:
    AppContext.loading_window.start_loading()
    try:
        response: rq.Response = rq.post(f"{app.settings.url}/{endpoint}", json=data) if method == "post" else (
                                rq.get(f"{app.settings.url}/{endpoint}", headers=data))

        try:
            return response.status_code, response.json()
        except (JSONDecodeError, ValueError):
            return response.status_code, {}
    except rq.exceptions.ConnectionError:
        AppContext.main_window.after(0, lambda: showerror("Error",
                                                          "Server is not available. Please try again later."))
        return 0, {}
    finally:
        AppContext.loading_window.finish_loading()
