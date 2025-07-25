import hashlib
import string
import re
import threading
from app.utils.requests import make_request
from app.gui.context import AppContext
from tkinter.messagebox import showerror, showinfo


def check_all(username: str, password: str, email: str | None = None) -> str | bool:
    for symbol in username:
        if symbol not in string.ascii_letters + string.digits + "_-":
            return "Unsupported characters in username"
    if len(username) < 4:
        return "The length of the username must be longer than 3 characters"
    elif len(username) > 20:
        return "Username length should not be longer than 20 characters"

    for symbol in password:
        if symbol not in string.ascii_letters + string.digits + "_-":
            return "Unsupported characters in password"
    if len(password) < 5:
        return "The length of the password must be longer than 4 characters"
    elif len(username) > 25:
        return "Password length should not be longer than 25 characters"

    if email is not None:
        if not re.match(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$", email):
            return "Incorrect email"

    return True


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def handle_register(username: str, password: str, email: str) -> None:
    def register() -> None:
        try:
            if not all([username, password, email]):
                showerror("Error", "All fields must be filled!")
                return

            check_status: bool | str = check_all(username, password, email)

            if check_status is not True:
                showerror("Error", check_status)
                return

            user: dict = {
                "username": username,
                "password": hash_password(password),
                "email": email,
            }

            response_status, response = make_request(endpoint="register", data=user)

            if response_status == 200:
                AppContext.main_window.verify_id = response["temp_id"]
                AppContext.main_window.init_verify_code_window()
                showinfo("Success", response["message"])
            else:
                showerror("Error", response["detail"])
        except Exception as e:
            showerror(type(e).__name__, f"Error: {str(e)}")

    threading.Thread(target=register).start()


def handle_verify(code: str) -> None:
    def verify() -> None:
        try:
            if len(code) != 6:
                showerror("Error", "Invalid verification code")
                return

            data: dict = {
                "temp_id": AppContext.main_window.verify_id,
                "code": code
            }

            response_status, response = make_request("verify_email", data)

            if response_status == 200:
                AppContext.main_window.init_auth_window("log")
                showinfo("Success", response["message"])
            else:
                showerror("Error", response["detail"])
        except Exception as e:
            showerror(type(e).__name__, f"Error: {str(e)}")

    threading.Thread(target=verify).start()

