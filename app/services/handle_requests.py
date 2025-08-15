import threading
import app.settings
import customtkinter as ctk
from tkinter.messagebox import showerror, showinfo
from customtkinter.windows import CTkInputDialog
from app.services.requests import make_request
from app.gui.context import AppContext
from app.schemas import ChatListItemData, AccountData, ChatListItem, MessageData


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
        data: dict = {
            "receiver_id": receiver_id,
            "page": 0,
        }

        response_status, response = make_request("get", "messages", data=data, with_token=True)

        if response_status == 200:
            AppContext.main_window.chat_window.messages_cache[receiver_id] = [MessageData(**body) for body in response]
            AppContext.main_window.chat_window.init_messages(receiver_id, clear_messages_frame=True)

    threading.Thread(target=get_messages, daemon=True).start()


def handle_get_chats() -> None:
    def get_chats() -> None:
        response_status, response = make_request("get", "chats", with_token=True,
                                                 with_loading_window=True)

        if response_status == 200:
            new_user_chats: dict[int, ChatListItem] = {
                data["user_id"]: ChatListItem(frame=None, last_message_label=None, timestamp_label=None,
                                              data=ChatListItemData(**data))
                for data in response
            }

            AppContext.main_window.chat_window.user_chats = new_user_chats

        AppContext.main_window.chat_window.init_user_chats_list()

    threading.Thread(target=get_chats, daemon=True).start()
