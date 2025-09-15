import tkinter
import customtkinter as ctk
import app.settings
from app.gui.windows.auth_window import AuthWindow
from app.gui.windows.verify_window import VerifyWindow
from app.gui.windows.chat_window import ChatWindow
from app.services.websocket_client import WebSocketClient
from app.gui.navigation_controller import NavigationController


class MainRoot(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title_text = f"CamelGram {app.settings.version}"
        self.title(self.title_text)
        self.geometry("1000x600")

        self.navigation = NavigationController(self)
        self.ws_client: WebSocketClient | None = None

        self.auth_window: AuthWindow | None = None
        self.verify_window: VerifyWindow | None = None
        self.chat_window: ChatWindow | None = None

    @staticmethod
    def styled_button(parent, **kwargs) -> ctk.CTkButton:
        return ctk.CTkButton(parent, border_width=2, border_color="#545454", fg_color="#353535",
                             hover_color="#444444", **kwargs)

    def show_auth_window(self, auth_type, **kwargs):
        self.clear_window()
        self.auth_window = AuthWindow(self, **kwargs)
        self.auth_window.pack(fill="both", expand=True)
        self.auth_window.setup_auth_ui(auth_type)

    def show_verify_window(self, **kwargs):
        self.clear_window()
        self.verify_window = VerifyWindow(self, **kwargs)
        self.verify_window.pack(fill="both", expand=True)
        self.verify_window.setup_verify_ui()

    def show_chat_window(self):
        self.clear_window()
        self.chat_window = ChatWindow(self)
        self.chat_window.pack(fill="both", expand=True)
        self.chat_window.setup_chat_ui()

    def clear_window(self):
        for widget in self.winfo_children():
            try:
                widget.destroy()
            except tkinter.TclError:
                pass
