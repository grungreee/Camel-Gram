import threading
import app.settings
import json
from app.gui.context import AppContext
from app.services.utils import get_validation_key
from tkinter.messagebox import showerror
from websocket import WebSocketApp


class WebSocketClient:
    def __init__(self) -> None:

        self.ws = WebSocketApp(
            url=f"ws://{app.settings.url}/ws?token={get_validation_key()}",
            on_message=self.on_message,
        )

    @staticmethod
    def on_message(_, message: dict) -> None:
        print(message)
        if message["type"] == "new_message":
            body: dict = message["body"]
            current_chat: tuple | None = AppContext.main_window.chat_window.current_chat

            if current_chat is not None and current_chat[0].winfo_exists() and \
                    current_chat[1]["user_id"] == body["sender_id"]:
                message: dict = {
                    "sender_display_name": current_chat[1]["display_name"],
                    "message": body["message"],
                    "timestamp": body["timestamp"]
                }

                AppContext.main_window.chat_window.init_messages([message], new_message=True)

    def connect(self) -> None:
        threading.Thread(target=self.ws.run_forever, daemon=True).start()

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
