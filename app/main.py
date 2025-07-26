import threading
from app.gui.main_window import MainWindow
from app.gui.context import AppContext
from app.services.auth_controller import check_validation


def main() -> None:
    window = MainWindow()
    AppContext.main_window = window

    threading.Thread(target=check_validation, daemon=True).start()

    window.mainloop()


if __name__ == '__main__':
    main()

