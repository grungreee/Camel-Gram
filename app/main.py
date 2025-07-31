from app.gui.main_window import MainWindow
from app.gui.context import AppContext
from app.services.auth_controller import check_validation
import threading


def main() -> None:
    window = MainWindow()
    AppContext.main_window = window

    window.after(0, lambda: threading.Thread(target=check_validation, daemon=True).start())

    window.mainloop()


if __name__ == '__main__':
    main()
