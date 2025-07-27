import customtkinter as ctk
import app.settings
from PIL import Image
from typing import Literal
from app.services.auth_controller import handle_auth, handle_verify
from app.services.utils import check_all


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.left_side: ctk.CTkFrame | None = None

        self.username_text: str = ""
        self.password_text: str = ""
        self.email_text: str = ""
        self.verify_id: str | None = None

        self.title_text = f"CamelGram {app.settings.version}"
        self.title(self.title_text)
        self.geometry("1000x600")

    def clear_window(self) -> None:
        for widget in self.winfo_children():
            widget.destroy()

    @staticmethod
    def styled_button(parent, **kwargs) -> ctk.CTkButton:
        return ctk.CTkButton(parent, border_width=2, border_color="#545454", fg_color="#353535",
                             hover_color="#444444", **kwargs)

    def init_auth_window(self, type_: Literal["reg", "log"]) -> None:
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
                               self.email_text if type_ == "reg" else None)
            error_label.configure(text="" if result is True else result)

        self.clear_window()

        self.title(f"{self.title_text} - {"Login" if type_ == "log" else "Register"}")

        frame_height: int = 175 if type_ == "reg" else 135

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
        show_password_button = self.styled_button(password_frame, text="", image=close_eye_image, width=12,
                                                  command=change_password_visibility)
        show_password_button.pack(side=ctk.RIGHT, padx=(10, 0))

        if type_ == "reg":
            email_entry = ctk.CTkEntry(auth_frame, placeholder_text="Email")
            email_entry.pack(pady=(10, 0), padx=10, anchor=ctk.W, fill=ctk.X)
            email_entry.bind("<KeyRelease>", lambda e: (email_on_release(e), update_errors()))

            if self.email_text:
                email_entry.insert(0, self.email_text)

        auth_button = self.styled_button(auth_frame, text="Login" if type_ == "log" else "Register", width=100,
                                         command=lambda: handle_auth(self.username_text, self.password_text,
                                                                     self.email_text if type_ == "reg" else None))
        auth_button.pack(pady=(10, 15), padx=10, anchor=ctk.CENTER)

        register_label = ctk.CTkLabel(self, text="Don't have an account? Register here." if type_ == "log" else
                                                 "Already have an account? Login here.",
                                      font=("Arial", 11, "underline"), cursor="hand2")
        register_label.bind("<Button-1>", lambda _: self.init_auth_window("reg" if type_ == "log" else "log"))
        register_label.place(relx=0.5, rely=0.5, anchor=ctk.N, y=(frame_height // 2 + 5))

    def init_verify_code_window(self) -> None:
        def validate_input(value: str) -> bool:
            return (value.isdigit() or value == "") and len(value) <= 1

        def handle_code_entry(code_entries, event, index: int) -> None:
            entry = code_entries[index]
            value = entry.get()

            if event.keysym == "BackSpace":
                if value == "" and index > 0:
                    code_entries[index - 1].focus()
            elif value != "":
                if index < len(code_entries) - 1:
                    code_entries[index + 1].focus()

        def get_code() -> str:
            return "".join([entry.get() for entry in code_entries])

        self.clear_window()

        self.title(f"{self.title_text} - Verify code")

        back_button = self.styled_button(self, text="<-- Back", width=50, command=lambda: self.init_auth_window("reg"))
        back_button.pack(pady=10, padx=10, anchor=ctk.W)

        main_frame = ctk.CTkFrame(self, width=300, height=155)
        main_frame.pack_propagate(False)
        main_frame.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

        code_label = ctk.CTkLabel(main_frame, text="Enter the code:", font=("Arial", 22))
        code_label.pack(pady=(15, 0), padx=10)

        entries_frame = ctk.CTkFrame(main_frame, height=40)
        entries_frame.pack_propagate(False)
        entries_frame.pack(pady=(10, 0), padx=10, fill=ctk.X)

        for i in range(6):
            entries_frame.grid_columnconfigure(i, weight=1, uniform="entry")

        code_entries: list[ctk.CTkEntry] = []
        vcmd = self.register(validate_input)

        for i in range(6):
            entry = ctk.CTkEntry(entries_frame, height=30, justify=ctk.CENTER, validate="key",
                                 validatecommand=(vcmd, "%P"))
            entry.grid(row=0, column=i, padx=7, sticky="nsew", pady=7)

            entry.bind("<KeyRelease>", lambda e, index=i: handle_code_entry(code_entries, e, index))

            code_entries.append(entry)

        confirm_button = self.styled_button(main_frame, text="Confirm", width=100,
                                            command=lambda: handle_verify(get_code()))
        confirm_button.pack(pady=(10, 15), padx=10, anchor=ctk.CENTER)

    def init_main_window(self) -> None:
        self.clear_window()

        self.title(self.title_text)

        self.left_side = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.left_side.pack_propagate(False)
        self.left_side.pack(side=ctk.LEFT, fill=ctk.Y)

        self.init_main_left_side()

        right_side = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        right_side.pack_propagate(False)
        right_side.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

    def clear_left_side(self) -> None:
        for widget in self.left_side.winfo_children():
            widget.destroy()

    def init_main_left_side(self) -> None:
        self.clear_left_side()

        upper_left_frame = ctk.CTkFrame(self.left_side, corner_radius=0, height=50)
        upper_left_frame.pack_propagate(False)
        upper_left_frame.pack(fill=ctk.X)

        burger_menu_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/burger_menu.png"), size=(18, 13))
        open_side_menu_button = self.styled_button(upper_left_frame, text="", image=burger_menu_image,
                                                   width=40, height=30, corner_radius=5, command=self.init_side_menu)
        open_side_menu_button.pack(side=ctk.LEFT, padx=(10, 0))

        search_entry = ctk.CTkEntry(upper_left_frame, placeholder_text="Search", height=30)
        search_entry.pack(side=ctk.RIGHT, padx=10, fill=ctk.X, expand=True)

        bottom_left_frame = ctk.CTkFrame(self.left_side, corner_radius=0, fg_color="transparent")
        bottom_left_frame.pack_propagate(False)
        bottom_left_frame.pack(fill=ctk.BOTH, expand=True)

        ctk.CTkLabel(bottom_left_frame, text="You dont have chats.",
                     font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    def init_side_menu(self) -> None:
        self.clear_left_side()

        upper_left_frame = ctk.CTkFrame(self.left_side, corner_radius=0, height=50)
        upper_left_frame.pack_propagate(False)
        upper_left_frame.pack(fill=ctk.X)

        back_button = self.styled_button(upper_left_frame, text="<-- Back", height=30, width=50,
                                         command=self.init_main_left_side)
        back_button.pack(padx=10, side=ctk.LEFT)

        account = app.settings.account_data["username"]
        account_label = ctk.CTkLabel(self.left_side, text=f"Account: {account}", font=("Arial", 15, "bold"))
        account_label.pack(pady=(10, 0), padx=10)
