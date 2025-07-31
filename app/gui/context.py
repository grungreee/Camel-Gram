from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.gui.main_window import MainWindow
    from app.gui.loading_window import LoadingWindow


class ClassProperty:
    def __init__(self, func):
        self.func = func

    def __get__(self, instance, owner):
        return self.func(owner)


class AppContext:
    main_window: "MainWindow" = None
    _loading_window: "LoadingWindow" = None

    @ClassProperty
    def loading_window(self) -> "LoadingWindow":
        if self._loading_window is None or not self._loading_window.winfo_exists():
            from app.gui.loading_window import init_loading_window
            init_loading_window()
        return self._loading_window
