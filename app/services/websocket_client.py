import threading
import app.settings
import json
from app.services.utils import get_validation_key
from tkinter.messagebox import showerror
from websocket import WebSocketApp


class WebSocketClient:
    def __init__(self) -> None:

        self.ws = WebSocketApp(
            url=f"ws://{app.settings.url}/ws",
            on_message=self.on_message
        )

        self.thread = threading.Thread(target=self.ws.run_forever, daemon=True)

    @staticmethod
    def on_message(ws, message: str) -> None:
        print(message)

    def connect(self) -> None:
        self.thread.start()

    def send(self, data: dict) -> None:
        token: str | None = get_validation_key()

        if not token:
            self.close()
            return

        data_with_auth: dict = data.copy()
        data_with_auth["token"] = token

        if self.ws.sock and self.ws.sock.connected:
            self.ws.send(json.dumps(data_with_auth))
        else:
            showerror("Error", "Connection is not established. Please try again later.")

    def close(self) -> None:
        self.ws.close()
