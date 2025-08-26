import threading
import app.settings
import customtkinter as ctk
from tkinter.messagebox import showerror, showinfo
from customtkinter.windows import CTkInputDialog
from app.services.requests import make_request
from app.gui.context import AppContext
from app.schemas import ChatListItemData, AccountData, ChatListItem, MessageData, MessageStatus, MessagesCache
from app.services.utils import MessageList


def handle_search(text: str) -> None:
    def search() -> None:
        response_status, response = make_request("get", "search_user", {"text": text},
                                                 with_loading_window=False, with_token=True)

        if response_status == 0:
            return

        AppContext.main_window.chat_window.init_search_results([AccountData(**data) for data in response]
                                                               if response_status == 200 else None, text)

    threading.Thread(target=search, daemon=True).start()


def handle_change_display_name(display_name_label: ctk.CTkLabel) -> None:
    def change_display_name() -> None:
        try:
            display_name: str | None = CTkInputDialog(title="Display name", text="Input new display name").get_input()

            if display_name is None:
                return

            response_status, response = make_request("post", "change_display_name",
                                                     {"display_name": display_name}, with_token=True)
            if response_status == 200:
                display_name_label.configure(text=display_name)
                app.settings.account_data.display_name = display_name
                showinfo("Info", "Display name changed successfully")
            elif response_status == 400:
                showerror("Error", response["detail"])

        except Exception as e:
            showerror(type(e).__name__, f"Error: {str(e)}")

    threading.Thread(target=change_display_name, daemon=True).start()


def handle_get_messages() -> None:
    def get_messages() -> None:
        receiver_id: int = AppContext.main_window.chat_window.current_chat.user.user_id

        message_id: int | None = None

        if receiver_id in AppContext.main_window.chat_window.messages_cache:
            message_id = (AppContext.main_window.chat_window.messages_cache[receiver_id].
                          messages.get_by_index(0).message_id)

        data: dict = {
            "receiver_id": receiver_id,
            "message_id": message_id,
        }

        response_status, response = make_request("get", "messages", data=data, with_token=True)

        if response_status == 200:
            messages: dict[int, MessageData] = {}

            for body in response:
                message: MessageData = MessageData(
                    message_id=body["message_id"],
                    display_name=body["display_name"],
                    timestamp=body["timestamp"],
                    message=body["message"],
                    status=MessageStatus(body["status"])
                )

                messages[body["message_id"]] = message

                if receiver_id not in AppContext.main_window.chat_window.messages_cache:
                    message_list = MessageList()
                    message_list.add_old(body["message_id"], message)
                    AppContext.main_window.chat_window.messages_cache[receiver_id] = (
                        MessagesCache(messages=message_list, has_more=False))
                else:
                    AppContext.main_window.chat_window.messages_cache[receiver_id].messages.add_old(body["message_id"],
                                                                                                    message)
            (AppContext.main_window.
             chat_window.init_messages(AppContext.main_window.chat_window.messages_cache[receiver_id].messages(),
                                       receiver_id, clear_messages_frame=True))

    threading.Thread(target=get_messages, daemon=True).start()


def handle_get_chats() -> None:
    def get_chats() -> None:
        response_status, response = make_request("get", "chats", with_token=True,
                                                 with_loading_window=True)

        if response_status == 200:
            new_user_chats: dict[int, ChatListItem] = {
                data["user_id"]: ChatListItem(data=ChatListItemData(**data))
                for data in response
            }

            AppContext.main_window.chat_window.user_chats = new_user_chats

        AppContext.main_window.chat_window.init_user_chats_list()

    threading.Thread(target=get_chats, daemon=True).start()
