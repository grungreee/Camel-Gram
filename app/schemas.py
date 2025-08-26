import typing
from dataclasses import dataclass
from enum import Enum
from customtkinter import CTkFrame, CTkLabel, CTkScrollableFrame, CTkTextbox

if typing.TYPE_CHECKING:
    from app.services.utils import MessageList  # noqa: F401


class MessageStatus(Enum):
    SENT = "sent"
    RECEIVED = "received"
    READ = "read"


class CurrentSideMenuState(Enum):
    CHATS = "chats"
    SETTINGS = "settings"
    SEARCHING = "searching"


class WindowState(Enum):
    AUTH_LOGIN = "auth_login"
    AUTH_REGISTER = "auth_register"
    VERIFY = "verify"
    MAIN_CHAT = "main_chat"


@dataclass
class AccountData:  # Data for displaying account info
    user_id: int
    username: str
    display_name: str


@dataclass
class MessagesCache:
    messages: "MessageList"
    has_more: bool


@dataclass
class MessageData:  # Data for displaying a message in chat
    message_id: int
    display_name: str
    message: str
    timestamp: str
    status: MessageStatus
    timestamp_label: CTkLabel | None = None
    status_label: CTkLabel | None = None


@dataclass
class ChatListItemData:  # Data for displaying chat in left chats list
    user_id: int
    username: str
    display_name: str
    last_message: str
    timestamp: str


@dataclass
class ChatListItem:  # Left frame chats list data
    data: ChatListItemData
    frame: CTkFrame | None = None
    last_message_label: CTkLabel | None = None
    timestamp_label: CTkLabel | None = None


@dataclass
class CurrentChat:  # Right frames chat data
    user: AccountData
    display_name_label: CTkLabel | None = None
    username_label: CTkLabel | None = None
    chat_list_frame: CTkFrame | None = None
    messages_frame: CTkScrollableFrame | None = None
    last_message_frame: CTkFrame | None = None
    first_message_frame: CTkFrame | None = None
    textbox: CTkTextbox | None = None
