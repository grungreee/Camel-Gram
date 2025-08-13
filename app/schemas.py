from dataclasses import dataclass
from customtkinter import CTkFrame, CTkLabel, CTkScrollableFrame, CTkTextbox


@dataclass
class AccountData:  # Data for displaying account info
    user_id: int
    username: str
    display_name: str


@dataclass
class MessageData:  # Data for displaying a message in chat
    user_id: int
    display_name: str
    message: str
    timestamp: str


@dataclass
class ChatData:  # Data for displaying chat in left chats list
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
    data: ChatData


@dataclass
class CurrentChat:  # Right frames chat data
    display_name_label: CTkLabel | None
    username_label: CTkLabel | None
    chats_list_frame: CTkFrame | None
    messages_frame: CTkScrollableFrame | None
    textbox: CTkTextbox | None
    user: AccountData
