import threading
import app.settings
import json
from app.gui.context import AppContext
from app.schemas import MessageStatus, AccountData
from app.services.utils import get_validation_key
from tkinter.messagebox import showerror
from websocket import WebSocketApp, WebSocketConnectionClosedException


class WebSocketClient:
    def __init__(self) -> None:

        self.ws = WebSocketApp(
            url=f"ws://{app.settings.url}/ws?token={get_validation_key()}",
            on_message=self.on_message,
            on_error=lambda _, *args: print(*args)
        )

    @staticmethod
    def on_message(_, message: str) -> None:
        body: dict = json.loads(message)

        match body["type"]:
            case "new_message":
                user = AccountData(user_id=body["sender_id"], display_name=body["display_name"],
                                   username=body["username"])

                AppContext.main_window.chat_window.handle_new_message(
                    text=body["message"], message_id=body["message_id"], user=user, timestamp=body["timestamp"],
                    status=MessageStatus(body["status"]), user_id=body["sender_id"])
            case "message_ack":
                AppContext.main_window.chat_window.change_message_status(
                    user_id=body["receiver_id"], message_id=body["message_id"], status=MessageStatus.RECEIVED,
                    timestamp=body["timestamp"], temp_id=body["temp_id"])
            case "messages_read":
                for msg in AppContext.main_window.chat_window.messages_cache[body["reader_id"]].messages().values():
                    if msg.sender_id != body["reader_id"]:
                        AppContext.main_window.chat_window.change_message_status(
                            message_id=msg.message_id, status=MessageStatus.READ, user_id=body["reader_id"])
                    if msg.message_id == body["message_id"]:
                        break
            case _:
                print(body)

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
            AppContext.main_window.destroy()

    def close(self) -> None:
        self.ws.close()
