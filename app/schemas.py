from dataclasses import dataclass
from enum import Enum
from customtkinter import CTkFrame, CTkLabel, CTkScrollableFrame, CTkTextbox


@dataclass
class AccountData:  # Data for displaying account info
    user_id: int
    username: str
    display_name: str


class MessageStatus(Enum):
    SENT = "sent"
    RECEIVED = "received"
    READ = "read"


@dataclass
class MessageData:  # Data for displaying a message in chat
    timestamp_label: CTkLabel | None
    status_label: CTkLabel | None
    message_id: int
    display_name: str
    message: str
    timestamp: str
    status: MessageStatus


@dataclass
class ChatListItemData:  # Data for displaying chat in left chats list
    user_id: int
    username: str
    display_name: str
    last_message: str
    timestamp: str


@dataclass
class ChatListItem:  # Left frame chats list data
    frame: CTkFrame | None
    last_message_label: CTkLabel | None
    timestamp_label: CTkLabel | None
    data: ChatListItemData


@dataclass
class CurrentChat:  # Right frames chat data
    display_name_label: CTkLabel | None
    username_label: CTkLabel | None
    chat_list_frame: CTkFrame | None
    messages_frame: CTkScrollableFrame | None
    last_message_frame: CTkFrame | None
    first_message_frame: CTkFrame | None
    textbox: CTkTextbox | None
    user: AccountData


class CurrentSideMenuState(Enum):
    CHATS = "chats"
    SETTINGS = "settings"
    SEARCHING = "searching"


class WindowState(Enum):
    AUTH_LOGIN = "auth_login"
    AUTH_REGISTER = "auth_register"
    VERIFY = "verify"
    MAIN_CHAT = "main_chat"
