import customtkinter as ctk
import app.settings
from PIL import Image
from typing import Literal
from app.gui.auth_controller import handle_register
import asyncio


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title(f"CamelGram {app.settings.version}")
        self.geometry("1000x600")

        self.init_auth_window("reg")

    def clear_window(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    def init_auth_window(self, type_: Literal["reg", "log"]) -> None:
        def change_password_visibility() -> None:
            if password_entry.cget("show") == "*":
                show_password_button.configure(image=open_eye_image)
                password_entry.configure(show="")
            else:
                show_password_button.configure(image=close_eye_image)
                password_entry.configure(show="*")

        self.clear_window()

        self.title(f"CamelGram {app.settings.version} - {"Login" if type_ == "log" else "Register"}")

        frame_height: int = 195 if type_ == "reg" else 155

        main_frame = ctk.CTkFrame(self, width=300, height=frame_height, fg_color="transparent")
        main_frame.pack_propagate(False)
        main_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        auth_frame = ctk.CTkFrame(main_frame, height=frame_height-20)
        auth_frame.pack_propagate(False)
        auth_frame.pack(fill=ctk.X)

        username_entry = ctk.CTkEntry(auth_frame, placeholder_text="Username")
        username_entry.pack(pady=(15, 0), padx=10, anchor=ctk.W, fill=ctk.X)

        password_frame = ctk.CTkFrame(auth_frame, fg_color="transparent", height=28)
        password_frame.pack_propagate(False)
        password_frame.pack(pady=(10, 0), padx=10, anchor=ctk.W, fill=ctk.X)

        password_entry = ctk.CTkEntry(password_frame, placeholder_text="Password", show="*")
        password_entry.pack(fill=ctk.BOTH, expand=True, side=ctk.LEFT)

        open_eye_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/eye_open.png"), size=(21, 21))
        close_eye_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/eye_close.png"), size=(21, 21))
        show_password_button = ctk.CTkButton(password_frame, text="", image=close_eye_image, width=12, border_width=2,
                                             border_color="#545454", fg_color="#353535", hover_color="#444444",
                                             command=change_password_visibility)
        show_password_button.pack(side=ctk.RIGHT, padx=(10, 0))

        if type_ == "reg":
            email_entry = ctk.CTkEntry(auth_frame, placeholder_text="Email")
            email_entry.pack(pady=(10, 0), padx=10, anchor=ctk.W, fill=ctk.X)

        auth_button = ctk.CTkButton(auth_frame, text="Login" if type_ == "log" else "Register",
                                    width=100, border_width=2, border_color="#545454", fg_color="#353535",
                                    hover_color="#444444", command=lambda: asyncio.run(handle_register(
                                                                                       username_entry.get(),
                                                                                       password_entry.get(),
                                                                                       email_entry.get()))
                                    if type_ == "reg" else None)
        auth_button.pack(pady=(10, 15), padx=10, anchor=ctk.CENTER)

        register_label = ctk.CTkLabel(main_frame, text="Don't have an account? Register here." if type_ == "log" else
                                                       "Already have an account? Login here.",
                                      font=("Arial", 11, "underline"), cursor="hand2")
        register_label.bind("<Button-1>", lambda _: self.init_auth_window("reg" if type_ == "log" else "log"))
        register_label.pack(pady=(5, 0), padx=10, anchor=ctk.CENTER)

    def init_main_menu(self) -> None:
        self.clear_window()

        left_side = ctk.CTkFrame(self, width=250, corner_radius=0)
        left_side.pack_propagate(False)
        left_side.pack(side=ctk.LEFT, fill=ctk.Y)

        right_side = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        right_side.pack_propagate(False)
        right_side.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)
