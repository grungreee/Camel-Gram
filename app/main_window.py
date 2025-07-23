import customtkinter as ctk


class MainWindow(ctk.CTk):
    def __init__(self) -> None:
        super().__init__()

        self.title("CamelGram")
        self.geometry("1000x600")
