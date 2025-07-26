import customtkinter as ctk
from app.gui.context import AppContext


class LoadingWindow(ctk.CTkToplevel):
    def __init__(self, root: ctk.CTk) -> None:
        super().__init__()
        
        self.root: ctk.CTk = root
        self.stop_flag: bool = False

        self.withdraw()

        self.title("Loading...")
        self.geometry("300x150")
        self.protocol("WM_DELETE_WINDOW", self.on_delete_window)
        self.resizable(False, False)

        self.loading_label = ctk.CTkLabel(self, text="Loading...", font=("Arial", 20, "bold"))
        self.loading_label.place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    def on_delete_window(self) -> None:
        self.destroy()
        self.root.destroy()

    def set_geometry(self, _=None) -> None:
        x: int = self.root.winfo_x() + (self.root.winfo_width() - self.winfo_width()) // 2
        y: int = self.root.winfo_y() + (self.root.winfo_height() - self.winfo_height()) // 2

        self.geometry(f"+{x}+{y}")

    def start_loading(self) -> None:
        self.bind("<Configure>", self.set_geometry)
        self.attributes("-topmost", True)
        self.start_loading_animation()

        self.deiconify()

    def animate_loading(self) -> None:
        if not self.stop_flag:
            label_text = self.loading_label.cget("text")
            if label_text == "Loading...":
                self.loading_label.configure(text="Loading")
            else:
                self.loading_label.configure(text=label_text + ".")
            self.after(350, self.animate_loading)

    def start_loading_animation(self) -> None:
        self.stop_flag = False
        self.animate_loading()

    def finish_loading(self) -> None:
        self.stop_flag = True
        self.withdraw()


def init_loading_window() -> None:
    loading_window = LoadingWindow(root=AppContext.main_window)
    AppContext._loading_window = loading_window
