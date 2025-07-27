from app.gui.main_window import MainWindow
from app.gui.context import AppContext
from app.services.auth_controller import check_validation


def main() -> None:
    window = MainWindow()
    AppContext.main_window = window

    window.after(0, check_validation)

    window.mainloop()


if __name__ == '__main__':
    main()

