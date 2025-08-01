from enum import Enum


class WindowState(Enum):
    AUTH_LOGIN = "auth_login"
    AUTH_REGISTER = "auth_register"
    VERIFY = "verify"
    MAIN_CHAT = "main_chat"


class NavigationController:
    def __init__(self, main_window):
        self.main_window = main_window
        self.current_state = None

    def navigate_to(self, state: WindowState, *args):
        if state == WindowState.AUTH_LOGIN:
            self.main_window.show_auth_window("log", *args)
        elif state == WindowState.AUTH_REGISTER:
            self.main_window.show_auth_window("reg", *args)
        elif state == WindowState.VERIFY:
            self.main_window.show_verify_window()
        elif state == WindowState.MAIN_CHAT:
            self.main_window.show_chat_window()

        self.current_state = state
