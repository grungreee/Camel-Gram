import threading
import app.settings
from app.services.requests import make_request
from app.gui.context import AppContext
from tkinter.messagebox import showerror, showinfo
from app.services.utils import check_all, hash_password
from app.gui.navigation_controller import WindowState
from app.services.utils import set_validation_key, delete_validation_key


def handle_auth(username: str, password: str, email: str | None = None) -> None:
    def auth() -> None:
        if not all([username, password]) and (email is None or email):
            showerror("Error", "All fields must be filled!")
            return

        check_status: bool | str = check_all(username, password, email)

        if check_status is not True:
            showerror("Error", check_status)
            return

        user: dict = {
            "username": username,
            "password": hash_password(password),
        }

        if email is not None:
            user["email"] = email

        endpoint: str = "register" if email is not None else "login"

        response_status, response = make_request(method="post", endpoint=endpoint, data=user)

        try:
            if response_status == 200:
                if email is not None:
                    AppContext.main_window.verify_window.verify_id = response["temp_id"]
                    AppContext.main_window.navigation.navigate_to(WindowState.VERIFY)
                else:
                    set_validation_key(response["token"])
                    check_validation()
                    AppContext.main_window.navigation.navigate_to(WindowState.MAIN_CHAT)
                showinfo("Success", response["message"])
            elif response_status != 0:
                showerror("Error", response["detail"])
        except Exception as e:
            showerror(type(e).__name__, f"Error: {str(e)}")

    threading.Thread(target=auth).start()


def handle_verify(code: str) -> None:
    def verify() -> None:
        if len(code) != 6:
            showerror("Error", "Invalid verification code")
            return

        data: dict = {
            "temp_id": AppContext.main_window.verify_window.verify_id,
            "code": code
        }

        response_status, response = make_request(method="post", endpoint="verify_email", data=data)

        try:
            if response_status == 200:
                AppContext.main_window.navigation.navigate_to(WindowState.AUTH_LOGIN)
                showinfo("Success", response["message"])
            else:
                showerror("Error", response["detail"])
        except Exception as e:
            showerror(type(e).__name__, f"Error: {str(e)}")

    threading.Thread(target=verify).start()


def check_validation() -> None:
    response_status, response = make_request(method="get", endpoint="me", with_token=True)

    if response_status == 200:
        app.settings.account_data = response
        AppContext.main_window.ws_client.connect()
        AppContext.main_window.navigation.navigate_to(WindowState.MAIN_CHAT)
    elif response_status == 401:
        AppContext.main_window.navigation.navigate_to(WindowState.AUTH_LOGIN)
        showinfo("Info", "You are not authorized. Please log in.")
        delete_validation_key()
    elif response_status == 1:
        AppContext.main_window.navigation.navigate_to(WindowState.AUTH_REGISTER)
    else:
        AppContext.main_window.destroy()
