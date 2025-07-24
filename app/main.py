from app.gui.main_window import MainWindow
from app.gui.context import AppContext


def main() -> None:
    window = MainWindow()
    AppContext.main_window = window
    window.mainloop()


if __name__ == '__main__':
    main()

