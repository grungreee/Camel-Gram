import customtkinter as ctk
from PIL import Image
from typing import TYPE_CHECKING
from app.services.auth_controller import handle_verify
from app.gui.navigation_controller import WindowState

if TYPE_CHECKING:
    from app.gui.main_window import MainWindow


class VerifyWindow(ctk.CTkFrame):
    def __init__(self, parent: "MainWindow"):
        super().__init__(parent)

        self.parent: "MainWindow" = parent
        self.verify_id: int | None = None

    def setup_verify_ui(self):
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

        self.parent.title(f"{self.parent.title_text} - Verify code")

        back_arrow_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/arrow_left.png"), size=(18, 13))
        back_button = self.parent.styled_button(self, text="", width=50, image=back_arrow_image, command=lambda:
                                                self.parent.navigation.navigate_to(WindowState.AUTH_REGISTER))
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

        confirm_button = self.parent.styled_button(main_frame, text="Confirm", width=100,
                                                   command=lambda: handle_verify(get_code()))
        confirm_button.pack(pady=(10, 15), padx=10, anchor=ctk.CENTER)
