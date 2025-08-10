from app.gui.main_root import MainRoot
from app.gui.context import AppContext
from app.services.auth_controller import check_validation
import threading


def main() -> None:
    window = MainRoot()
    AppContext.main_window = window

    threading.Thread(target=check_validation, daemon=True).start()

    window.mainloop()


if __name__ == '__main__':
    main()
