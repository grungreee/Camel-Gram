import threading
import app.settings
import customtkinter as ctk
from tkinter.messagebox import showerror, showinfo
from customtkinter.windows import CTkInputDialog
from app.services.requests import make_request
from app.gui.context import AppContext


def handle_search(text: str) -> None:
    def search() -> None:
        response_status, response = make_request("get", "search_user", {"text": text},
                                                 with_loading_window=False, with_token=True)

        if response_status == 0:
            return

        AppContext.main_window.chat_window.init_search_results_left_side(response if response_status == 200 else None,
                                                                         True if text == "" else False)

    threading.Thread(target=search).start()


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
                app.settings.account_data["display_name"] = display_name
                showinfo("Info", "Display name changed successfully")
            elif response_status == 400:
                showerror("Error", response["detail"])

        except Exception as e:
            showerror(type(e).__name__, f"Error: {str(e)}")

    threading.Thread(target=change_display_name).start()


def handle_get_messages() -> None:
    def get_messages() -> None:
        data: dict = {
            "receiver_id": AppContext.main_window.chat_window.current_chat[1]["user_id"],
            "page": 0,
        }

        response_status, response = make_request("get", "messages", data=data, with_token=True)

        if response_status == 200:
            AppContext.main_window.chat_window.init_messages(response)

    threading.Thread(target=get_messages).start()
