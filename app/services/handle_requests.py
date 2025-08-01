import threading
import customtkinter as ctk
from app.services.requests import make_request
from app.gui.context import AppContext


def handle_search(text: str) -> None:
    def search() -> None:
        if text != "":
            response_status, response = make_request("get", "search_user", {"text": text},
                                                     with_loading_window=False)

            AppContext.main_window.chat_window.clear_left_bottom_frame()

            if response_status == 200:
                frame = ctk.CTkScrollableFrame(AppContext.main_window.chat_window.bottom_left_frame,
                                               fg_color="transparent", corner_radius=0,
                                               border_width=0)
                frame.pack(fill=ctk.BOTH, expand=True)

                for user in response["users"]:
                    ctk.CTkLabel(frame, text=f"{user["display_name"]} - {user["username"]}", font=("Arial", 12)).pack(
                        fill=ctk.BOTH, expand=True)
            elif response_status != 0:
                ctk.CTkLabel(AppContext.main_window.chat_window.bottom_left_frame, text="No results found",
                             font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
            else:
                pass
        else:
            AppContext.main_window.chat_window.init_search_bottom_left_side()

    threading.Thread(target=search).start()
