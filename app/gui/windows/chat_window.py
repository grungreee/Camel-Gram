import customtkinter as ctk
import app.settings
from PIL import Image
from typing import TYPE_CHECKING
from app.services.handle_requests import handle_search
from app.services.websocket_client import WebSocketClient

if TYPE_CHECKING:
    from app.gui.main_root import MainRoot


class ChatWindow(ctk.CTkFrame):
    def __init__(self, parent: "MainRoot"):
        super().__init__(parent)

        self.parent: "MainRoot" = parent

        self.ws_client: WebSocketClient = parent.ws_client
        self.left_side: ctk.CTkFrame | None = None
        self.upper_left_frame: ctk.CTkFrame | None = None
        self.bottom_left_frame: ctk.CTkFrame | None = None

        self.debounce_timer: str | None = None

    def setup_chat_ui(self, _=None) -> None:
        self.parent.title(self.parent.title_text)

        self.left_side = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.left_side.pack_propagate(False)
        self.left_side.pack(side=ctk.LEFT, fill=ctk.Y)

        self.upper_left_frame = ctk.CTkFrame(self.left_side, corner_radius=0, height=50, fg_color="#292929")
        self.upper_left_frame.pack_propagate(False)
        self.upper_left_frame.pack(fill=ctk.X)

        self.bottom_left_frame = ctk.CTkFrame(self.left_side, corner_radius=0, fg_color="transparent")
        self.bottom_left_frame.pack_propagate(False)
        self.bottom_left_frame.pack(fill=ctk.BOTH, expand=True)

        self.init_main_left_side()

        right_side = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        right_side.pack_propagate(False)
        right_side.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)
        right_side.bind("<Button-1>", self.init_main_left_side)

        def foo():
            self.ws_client.send({"type": "ping"})

        send_button = ctk.CTkButton(right_side, text="Ping websocket", command=foo)
        send_button.place(rely=0.5, relx=0.5, anchor=ctk.CENTER)

    def init_side_menu(self) -> None:
        self.clear_left_side()

        back_arrow_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/arrow_left.png"),
                                        size=(18, 13))
        back_button = self.parent.styled_button(self.upper_left_frame, text="", height=30, width=40,
                                                corner_radius=5, image=back_arrow_image,
                                                command=self.init_main_left_side)
        back_button.pack(padx=(10, 0), side=ctk.LEFT)

        ctk.CTkLabel(self.bottom_left_frame, text="Account", font=("Arial", 17, "bold")
                     ).pack(pady=(10, 0), padx=15, anchor=ctk.W)

        account_info_frame = ctk.CTkFrame(self.bottom_left_frame, height=125)
        account_info_frame.pack_propagate(False)
        account_info_frame.pack(pady=(5, 0), padx=10, fill=ctk.X)

        pencil_icon = ctk.CTkImage(light_image=Image.open("app/assets/icons/pencil.png"), size=(17, 17))

        display_name_frame = ctk.CTkFrame(account_info_frame, fg_color="transparent", height=28)
        display_name_frame.pack_propagate(False)
        display_name_frame.pack(pady=(10, 0), padx=10, anchor=ctk.W, fill=ctk.X)

        display_name = app.settings.account_data["display_name"]
        display_name_label = ctk.CTkLabel(display_name_frame, text=f"{display_name}", font=("Arial", 15, "bold"))
        display_name_label.pack(side=ctk.LEFT)

        change_display_name_button = ctk.CTkButton(display_name_frame, text="", width=20, image=pencil_icon,
                                                   fg_color="transparent", hover_color="#343434")
        change_display_name_button.pack(side=ctk.LEFT, padx=10)

        username_frame = ctk.CTkFrame(account_info_frame, fg_color="transparent", height=28)
        username_frame.pack_propagate(False)
        username_frame.pack(pady=(10, 0), padx=10, anchor=ctk.W, fill=ctk.X)

        username = app.settings.account_data["username"]
        username_label = ctk.CTkLabel(username_frame, text=f"@{username}", font=("Arial", 12))
        username_label.pack(side=ctk.LEFT)

        change_username_button = ctk.CTkButton(username_frame, text="", width=20, image=pencil_icon,
                                               fg_color="transparent", hover_color="#343434")
        change_username_button.pack(side=ctk.LEFT, padx=10)

        self.parent.styled_button(account_info_frame, text="Logout").pack(pady=(10, 0), padx=10, fill=ctk.X)

    def init_main_left_side(self, _=None) -> None:
        self.clear_left_side()

        burger_menu_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/burger_menu.png"), size=(18, 13))
        open_side_menu_button = self.parent.styled_button(self.upper_left_frame, text="", image=burger_menu_image,
                                                          width=40, height=30, corner_radius=5,
                                                          command=self.init_side_menu)
        open_side_menu_button.pack(side=ctk.LEFT, padx=(10, 0))

        search_entry = ctk.CTkEntry(self.upper_left_frame, placeholder_text="Search", height=30)
        search_entry.pack(side=ctk.RIGHT, padx=10, fill=ctk.X, expand=True)
        search_entry.bind("<FocusIn>", self.init_search_left_side)

        ctk.CTkLabel(self.bottom_left_frame, text="You dont have chats.",
                     font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    def init_search_left_side(self, _=None) -> None:
        def cancel_search() -> None:
            if self.debounce_timer:
                self.after_cancel(self.debounce_timer)
                self.debounce_timer = None

        def back() -> None:
            cancel_search()
            self.init_main_left_side()

        def on_text_change(*_) -> None:
            cancel_search()

            self.debounce_timer = self.after(350, lambda: handle_search(text_var.get()))

        self.clear_left_side()

        back_arrow_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/arrow_left.png"),
                                        size=(18, 13))
        back_button = self.parent.styled_button(self.upper_left_frame, text="", height=30, width=40,
                                                corner_radius=5, image=back_arrow_image, command=back)
        back_button.pack(padx=(10, 0), side=ctk.LEFT)

        text_var = ctk.StringVar()
        text_var.trace_add("write", on_text_change)

        search_entry = ctk.CTkEntry(self.upper_left_frame, height=30, textvariable=text_var)
        search_entry.pack(side=ctk.RIGHT, padx=10, fill=ctk.X, expand=True)
        search_entry.focus()

        self.init_search_bottom_left_side()

    def init_search_bottom_left_side(self) -> None:
        self.clear_left_bottom_frame()

        ctk.CTkLabel(self.bottom_left_frame, text="Start typing to search",
                     font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    def clear_left_upper_frame(self) -> None:
        for widget in self.upper_left_frame.winfo_children():
            widget.destroy()

    def clear_left_bottom_frame(self) -> None:
        for widget in self.bottom_left_frame.winfo_children():
            widget.destroy()

    def clear_left_side(self) -> None:
        self.clear_left_upper_frame()
        self.clear_left_bottom_frame()
