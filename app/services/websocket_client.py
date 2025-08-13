import threading
import app.settings
import json
from app.gui.context import AppContext
from app.schemas import MessageData, CurrentChat, ChatListItem
from app.services.utils import get_validation_key, iso_to_hm
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
            current_chat: CurrentChat | None = AppContext.main_window.chat_window.current_chat
            chats_list_items: list[ChatListItem] | None = AppContext.main_window.chat_window.user_chats

            if current_chat and current_chat.messages_frame is not None and \
                    current_chat.messages_frame.winfo_exists() and current_chat.user.user_id == body["sender_id"]:
                message_data = MessageData(display_name=current_chat.user.display_name, message=body["message"],
                                           timestamp=body["timestamp"], user_id=body["sender_id"])

                AppContext.main_window.chat_window.init_messages([message_data], new_message=True)

            if chats_list_items:
                for i, chat_list_item in enumerate(chats_list_items):
                    if chat_list_item.data.user_id == body["sender_id"]:
                        if chat_list_item.last_message_label and chat_list_item.last_message_label.winfo_exists():
                            chat_list_item.last_message_label.configure(text=body["message"])
                            chat_list_item.timestamp_label.configure(text=iso_to_hm(body["timestamp"]))
                        chats_list_items[i].data.last_message = body["message"]
                        chats_list_items[i].data.timestamp = body["timestamp"]
                        break

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
