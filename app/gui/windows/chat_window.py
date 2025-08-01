import customtkinter as ctk
import app.settings
from PIL import Image
from typing import TYPE_CHECKING
from app.services.websocket_client import WebSocketClient

if TYPE_CHECKING:
    from app.gui.main_window import MainWindow


class ChatWindow(ctk.CTkFrame):
    def __init__(self, parent: "MainWindow"):
        super().__init__(parent)

        self.parent: "MainWindow" = parent

        self.ws_client: WebSocketClient = parent.ws_client
        self.left_side: ctk.CTkFrame | None = None
        self.upper_left_frame: ctk.CTkFrame | None = None
        self.bottom_left_frame: ctk.CTkFrame | None = None

    def setup_chat_ui(self, _=None) -> None:
        def init_main_left_side(_=None) -> None:
            def init_search_left_side(_=None) -> None:
                self.clear_left_side()

                back_arrow_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/arrow_left.png"),
                                                size=(18, 13))
                back_button = self.parent.styled_button(self.upper_left_frame, text="", height=30, width=40,
                                                        corner_radius=5, image=back_arrow_image,
                                                        command=init_main_left_side)
                back_button.pack(padx=(10, 0), side=ctk.LEFT)

                search_entry = ctk.CTkEntry(self.upper_left_frame, placeholder_text="Search", height=30)
                search_entry.pack(side=ctk.RIGHT, padx=10, fill=ctk.X, expand=True)
                search_entry.bind("<FocusOut>", init_main_left_side)
                search_entry.focus()

                ctk.CTkLabel(self.bottom_left_frame, text="Start typing to search",
                             font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

            def init_side_menu() -> None:
                self.clear_left_side()

                back_arrow_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/arrow_left.png"),
                                                size=(18, 13))
                back_button = self.parent.styled_button(self.upper_left_frame, text="", height=30, width=40,
                                                        corner_radius=5, image=back_arrow_image,
                                                        command=init_main_left_side)
                back_button.pack(padx=(10, 0), side=ctk.LEFT)

                account = app.settings.account_data["username"]
                account_label = ctk.CTkLabel(self.bottom_left_frame, text=f"Account: {account}",
                                             font=("Arial", 15, "bold"))
                account_label.pack(pady=(10, 0), padx=10)

            self.clear_left_side()

            burger_menu_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/burger_menu.png"), size=(18, 13))
            open_side_menu_button = self.parent.styled_button(self.upper_left_frame, text="", image=burger_menu_image,
                                                              width=40, height=30, corner_radius=5,
                                                              command=init_side_menu)
            open_side_menu_button.pack(side=ctk.LEFT, padx=(10, 0))

            search_entry = ctk.CTkEntry(self.upper_left_frame, placeholder_text="Search", height=30)
            search_entry.pack(side=ctk.RIGHT, padx=10, fill=ctk.X, expand=True)
            search_entry.bind("<FocusIn>", init_search_left_side)

            ctk.CTkLabel(self.bottom_left_frame, text="You dont have chats.",
                         font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        self.parent.title(self.parent.title_text)

        self.left_side = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.left_side.pack_propagate(False)
        self.left_side.pack(side=ctk.LEFT, fill=ctk.Y)

        self.upper_left_frame = ctk.CTkFrame(self.left_side, corner_radius=0, height=50)
        self.upper_left_frame.pack_propagate(False)
        self.upper_left_frame.pack(fill=ctk.X)

        self.bottom_left_frame = ctk.CTkFrame(self.left_side, corner_radius=0, fg_color="transparent")
        self.bottom_left_frame.pack_propagate(False)
        self.bottom_left_frame.pack(fill=ctk.BOTH, expand=True)

        init_main_left_side()

        right_side = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        right_side.pack_propagate(False)
        right_side.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)
        right_side.bind("<Button-1>", init_main_left_side)

        def foo():
            self.ws_client.send({"type": "ping"})

        send_button = ctk.CTkButton(right_side, text="Ping websocket", command=foo)
        send_button.place(rely=0.5, relx=0.5, anchor=ctk.CENTER)

    def clear_left_side(self) -> None:
        for widget in self.bottom_left_frame.winfo_children() + self.upper_left_frame.winfo_children():
            widget.destroy()
