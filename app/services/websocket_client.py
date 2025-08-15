import threading
import app.settings
import json
from app.gui.context import AppContext
from app.services.utils import get_validation_key
from tkinter.messagebox import showerror
from websocket import WebSocketApp, WebSocketConnectionClosedException


class WebSocketClient:
    def __init__(self) -> None:

        self.ws = WebSocketApp(
            url=f"ws://{app.settings.url}/ws?token={get_validation_key()}",
            on_message=self.on_message,
        )

    @staticmethod
    def on_message(_, message: str) -> None:
        message: dict = json.loads(message)

        if message["type"] == "new_message":
            body: dict = message["body"]

            kwargs: dict = {
                "text": body["message"],
                "user_id": body["sender_id"],
                "chat_with_id": body["sender_id"],
                "timestamp": body["timestamp"],
                "display_name": body["display_name"],
                "username": body["username"]
            }

            AppContext.main_window.chat_window.handle_new_message(**kwargs)

    def connect(self) -> None:
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

    def send(self, data: dict) -> None:
        try:
            token: str | None = get_validation_key()

            if not token:
                self.close()
                return

            data_with_auth: dict = data.copy()
            data_with_auth["token"] = token

            self.ws.send(json.dumps(data_with_auth))
        except WebSocketConnectionClosedException:
            showerror("Error", "Connection is not established. Please try again later.")

    def close(self) -> None:
        self.ws.close()
