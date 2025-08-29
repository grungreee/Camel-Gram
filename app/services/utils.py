import hashlib
import string
import re
import keyring
import app.settings
from datetime import datetime, timezone
from app.schemas import MessageData
from collections import deque


class MessageList:
    def __init__(self) -> None:
        self._order = deque()
        self._messages: dict[int | str, MessageData] = {}

    def add_old(self, message_id: int | str, message: MessageData) -> None:
        if message_id not in self._messages:
            self._order.appendleft(message_id)
            self._messages[message_id] = message

    def add_new(self, message_id: int | str, message: MessageData) -> None:
        if message_id not in self._messages:
            self._order.append(message_id)
            self._messages[message_id] = message

    def get_by_index(self, index: int) -> MessageData:
        return self._messages[self._order[index]]

    def pop_by_id(self, message_id: int | str) -> None:
        if message_id in self._messages:
            self._order.remove(message_id)

    def __len__(self) -> int:
        return len(self._messages)

    def __getitem__(self, item: str | int | slice) -> MessageData | dict[int | str, MessageData]:
        if isinstance(item, slice):
            return {message_id: self._messages[message_id] for message_id in list(self._order)[item]}
        return self._messages[item]

    def __setitem__(self, key, value) -> None:
        self._messages[key] = value

    def __call__(self) -> dict[int | str, MessageData]:
        return {msg_id: self._messages[msg_id] for msg_id in self._order}


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


def format_last_message(text: str) -> str:
    text = text.replace("\n", " ")

    if len(text) > 20:
        return text[:20] + "..."
    return text


def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def get_validation_key() -> str | None:
    return keyring.get_password(f"CamelGram{app.settings.session}", "access_key")


def set_validation_key(key: str) -> None:
    keyring.set_password(f"CamelGram{app.settings.session}", "access_key", key)


def delete_validation_key() -> None:
    keyring.delete_password(f"CamelGram{app.settings.session}", "access_key")
