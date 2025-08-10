from dataclasses import dataclass
from customtkinter import CTkFrame, CTkLabel, CTkScrollableFrame, CTkTextbox


@dataclass
class AccountData:
    user_id: int
    username: str
    display_name: str


@dataclass
class MessageData:
    user_id: int
    display_name: str
    message: str
    timestamp: str


@dataclass
class ChatData:
    user_id: int
    username: str
    display_name: str
    last_message: str
    timestamp: str


@dataclass
class CurrentChat:
    display_name_label: CTkLabel | None
    username_label: CTkLabel | None
    chats_list_frame: CTkFrame | None
    messages_frame: CTkScrollableFrame | None
    textbox: CTkTextbox | None
    user: AccountData


@dataclass
class ChatItem:
    frame: CTkFrame | None
    last_message_label: CTkLabel | None
    timestamp_label: CTkLabel | None
    data: ChatData
