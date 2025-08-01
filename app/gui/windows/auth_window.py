import customtkinter as ctk
from PIL import Image
from typing import Literal, TYPE_CHECKING
from app.gui.navigation_controller import WindowState
from app.services.auth_controller import handle_auth
from app.services.utils import check_all

if TYPE_CHECKING:
    from app.gui.main_window import MainWindow


class AuthWindow(ctk.CTkFrame):
    def __init__(self, parent: "MainWindow"):
        super().__init__(parent)

        self.parent: "MainWindow" = parent

        self.username_text: str = ""
        self.password_text: str = ""
        self.email_text: str = ""

    def setup_auth_ui(self, auth_type: Literal["reg", "log"]):
        def change_password_visibility() -> None:
            if password_entry.cget("show") == "*":
                show_password_button.configure(image=open_eye_image)
                password_entry.configure(show="")
            else:
                show_password_button.configure(image=close_eye_image)
                password_entry.configure(show="*")

        def username_on_release(_) -> None:
            self.username_text = username_entry.get()

        def password_on_release(_) -> None:
            self.password_text = password_entry.get()

        def email_on_release(_) -> None:
            self.email_text = email_entry.get()

        def update_errors() -> None:
            result = check_all(self.username_text, self.password_text,
                               self.email_text if auth_type == "reg" else None)
            error_label.configure(text="" if result is True else result)

        self.parent.title(f"{self.parent.title_text} - {"Login" if auth_type == "log" else "Register"}")

        frame_height: int = 175 if auth_type == "reg" else 135

        error_label = ctk.CTkLabel(self, text="", font=("Arial", 10, "italic"), text_color="red")
        error_label.place(relx=0.5, rely=0.5, anchor=ctk.S, y=-(frame_height // 2 + 5))

        auth_frame = ctk.CTkFrame(self, width=300, height=frame_height)
        auth_frame.pack_propagate(False)
        auth_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        username_entry = ctk.CTkEntry(auth_frame, placeholder_text="Username")
        username_entry.pack(pady=(15, 0), padx=10, anchor=ctk.W, fill=ctk.X)
        username_entry.bind("<KeyRelease>", lambda e: (username_on_release(e), update_errors()))

        if self.username_text:
            username_entry.insert(0, self.username_text)

        password_frame = ctk.CTkFrame(auth_frame, fg_color="transparent", height=28)
        password_frame.pack_propagate(False)
        password_frame.pack(pady=(10, 0), padx=10, anchor=ctk.W, fill=ctk.X)

        password_entry = ctk.CTkEntry(password_frame, placeholder_text="Password", show="*")
        password_entry.pack(fill=ctk.BOTH, expand=True, side=ctk.LEFT)
        password_entry.bind("<KeyRelease>", lambda e: (password_on_release(e), update_errors()))

        if self.password_text:
            password_entry.insert(0, self.password_text)

        open_eye_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/eye_open.png"), size=(21, 21))
        close_eye_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/eye_close.png"), size=(21, 21))
        show_password_button = self.parent.styled_button(password_frame, text="", image=close_eye_image, width=12,
                                                         command=change_password_visibility)
        show_password_button.pack(side=ctk.RIGHT, padx=(10, 0))

        if auth_type == "reg":
            email_entry = ctk.CTkEntry(auth_frame, placeholder_text="Email")
            email_entry.pack(pady=(10, 0), padx=10, anchor=ctk.W, fill=ctk.X)
            email_entry.bind("<KeyRelease>", lambda e: (email_on_release(e), update_errors()))

            if self.email_text:
                email_entry.insert(0, self.email_text)

        auth_button = self.parent.styled_button(auth_frame, text="Login" if auth_type == "log" else "Register",
                                                width=100,
                                                command=lambda: handle_auth(self.username_text, self.password_text,
                                                                            self.email_text if auth_type == "reg"
                                                                            else None))
        auth_button.pack(pady=(10, 15), padx=10, anchor=ctk.CENTER)

        auth_text: str = "Don't have an account? Register here." if auth_type == "log" else \
                         "Already have an account? Login here."

        auth_label = ctk.CTkLabel(self, text=auth_text, font=("Arial", 11, "underline"), cursor="hand2")
        auth_label.place(relx=0.5, rely=0.5, anchor=ctk.N, y=(frame_height // 2 + 5))

        state: WindowState = WindowState.AUTH_REGISTER if auth_type == "log" else WindowState.AUTH_LOGIN
        auth_label.bind("<Button-1>", lambda _: self.parent.navigation.navigate_to(state))
