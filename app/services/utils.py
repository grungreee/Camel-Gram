import hashlib
import string
import re
import keyring
import app.settings
from datetime import datetime, timezone


def iso_to_hm(iso_str: str, to_local: bool = True) -> str:
    if iso_str.endswith('Z'):
        dt = datetime.fromisoformat(iso_str.replace('Z', '+00:00'))
    else:
        dt = datetime.fromisoformat(iso_str)

    if to_local:
        dt = dt.astimezone()
    else:
        dt = dt.astimezone(timezone.utc)

    return f"{dt.hour}:{dt.minute:02d}"


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


def get_validation_key() -> str | None:
    return keyring.get_password("CamelGram" + app.settings.session, "access_key")


def set_validation_key(key: str) -> None:
    keyring.set_password("CamelGram" + app.settings.session, "access_key", key)


def delete_validation_key() -> None:
    keyring.delete_password("CamelGram" + app.settings.session, "access_key")
