from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.gui.main_window import MainWindow


class AppContext:
    main_window: "MainWindow" = None
