import time
import uuid
import customtkinter as ctk
import app.settings
import threading
from PIL import Image
from typing import TYPE_CHECKING
from datetime import datetime
from app.gui.context import AppContext
from app.schemas import (AccountData, ChatListItemData, ChatListItem, MessageData, CurrentChat, CurrentSideMenuState,
                         MessageStatus, MessagesCache)
from app.services.auth_controller import handle_logout
from app.services.handle_requests import handle_search, handle_change_display_name, handle_get_messages
from app.services.utils import iso_to_hm, MessageList, format_last_message

if TYPE_CHECKING:
    from app.gui.main_root import MainRoot  # noqa: F401


class ChatWindow(ctk.CTkFrame):
    def __init__(self, parent: "MainRoot"):
        super().__init__(parent)

        self.parent: "MainRoot" = parent

        self.left_upper_frame: ctk.CTkFrame | None = None
        self.left_bottom_frame: ctk.CTkFrame | None = None
        self.right_upper_frame: ctk.CTkFrame | None = None
        self.right_bottom_frame: ctk.CTkFrame | None = None

        self.side_menu_state: CurrentSideMenuState = CurrentSideMenuState.CHATS
        self.debounce_timer: str | None = None
        self.user_chats: dict[int, ChatListItem] = {}
        self.current_chat: CurrentChat | None = None
        self.messages_cache: dict[int, MessagesCache] = {}

    def setup_chat_ui(self, _=None) -> None:
        self.parent.title(self.parent.title_text)

        left_side = ctk.CTkFrame(self, width=250, corner_radius=0)
        left_side.pack_propagate(False)
        left_side.pack(side=ctk.LEFT, fill=ctk.Y)

        self.left_upper_frame = ctk.CTkFrame(left_side, corner_radius=0, height=50, fg_color="#292929", border_width=1)
        self.left_upper_frame.pack_propagate(False)
        self.left_upper_frame.pack(fill=ctk.X)

        self.left_bottom_frame = ctk.CTkFrame(left_side, corner_radius=0, fg_color="transparent")
        self.left_bottom_frame.pack_propagate(False)
        self.left_bottom_frame.pack(fill=ctk.BOTH, expand=True)

        self.init_chats_list_side()

        right_side = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        right_side.pack_propagate(False)
        right_side.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

        self.right_upper_frame = ctk.CTkFrame(right_side, corner_radius=0, height=50, fg_color="#292929")
        self.right_upper_frame.pack_propagate(False)
        self.right_upper_frame.pack(fill=ctk.X)
        self.right_upper_frame.bind("<Button-1>", self.init_chats_list_side)

        self.right_bottom_frame = ctk.CTkFrame(right_side, corner_radius=0, fg_color="transparent")
        self.right_bottom_frame.pack_propagate(False)
        self.right_bottom_frame.pack(fill=ctk.BOTH, expand=True)
        self.right_bottom_frame.bind("<Button-1>", self.init_chats_list_side)

        self.parent.bind("<Escape>", lambda _: self.init_chat(is_close=True))
        self.init_chat(is_close=True)

    def init_side_menu(self) -> None:
        self.clear_frame(self.left_upper_frame)
        self.clear_frame(self.left_bottom_frame)

        back_arrow_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/arrow_left.png"),
                                        size=(18, 13))
        back_button = self.parent.styled_button(self.left_upper_frame, text="", height=30, width=40,
                                                corner_radius=5, image=back_arrow_image,
                                                command=self.init_chats_list_side)
        back_button.pack(padx=(10, 0), side=ctk.LEFT)

        ctk.CTkLabel(self.left_bottom_frame, text="Account", font=("Arial", 17, "bold")
                     ).pack(pady=(10, 0), padx=15, anchor=ctk.W)

        account_info_frame = ctk.CTkFrame(self.left_bottom_frame, height=125)
        account_info_frame.pack(pady=(5, 0), padx=10, fill=ctk.X)

        pencil_icon = ctk.CTkImage(light_image=Image.open("app/assets/icons/pencil.png"), size=(17, 17))

        display_name_frame = ctk.CTkFrame(account_info_frame, fg_color="transparent", height=24)
        display_name_frame.pack(pady=(10, 0), padx=10, anchor=ctk.W, fill=ctk.X)

        display_name = app.settings.account_data.display_name
        display_name_label = ctk.CTkLabel(display_name_frame, text=display_name, font=("Arial", 15, "bold"),
                                          wraplength=160, justify=ctk.LEFT)
        display_name_label.pack(side=ctk.LEFT)

        change_display_name_button = ctk.CTkButton(display_name_frame, text="", width=20, image=pencil_icon,
                                                   fg_color="transparent", hover_color="#343434",
                                                   command=lambda: handle_change_display_name(display_name_label))
        change_display_name_button.pack(side=ctk.LEFT, padx=10)

        username_frame = ctk.CTkFrame(account_info_frame, fg_color="transparent", height=28)
        username_frame.pack_propagate(False)
        username_frame.pack(pady=(10, 0), padx=10, anchor=ctk.W, fill=ctk.X)

        username = app.settings.account_data.username
        username_label = ctk.CTkLabel(username_frame, text=f"@{username}", font=("Arial", 12))
        username_label.pack(side=ctk.LEFT)

        self.parent.styled_button(account_info_frame, text="Logout", command=handle_logout
                                  ).pack(pady=10, padx=10, fill=ctk.X)

    def init_chats_list_side(self, _=None) -> None:
        self.side_menu_state = CurrentSideMenuState.CHATS

        self.clear_frame(self.left_upper_frame)
        self.clear_frame(self.left_bottom_frame)

        burger_menu_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/burger_menu.png"), size=(18, 13))
        open_side_menu_button = self.parent.styled_button(self.left_upper_frame, text="", image=burger_menu_image,
                                                          width=40, height=30, corner_radius=5,
                                                          command=self.init_side_menu)
        open_side_menu_button.pack(side=ctk.LEFT, padx=(10, 0))

        search_entry = ctk.CTkEntry(self.left_upper_frame, placeholder_text="Search", height=30)
        search_entry.pack(side=ctk.RIGHT, padx=10, fill=ctk.X, expand=True)
        search_entry.bind("<FocusIn>", self.init_search_side)

        self.init_user_chats_list()

    def init_search_side(self, _=None) -> None:
        def cancel_search() -> None:
            if self.debounce_timer:
                self.after_cancel(self.debounce_timer)
                self.debounce_timer = None

        def back() -> None:
            cancel_search()
            self.init_chats_list_side()

        def on_text_change(*_) -> None:
            cancel_search()

            # noinspection PyTypeChecker
            self.debounce_timer = self.after(350, lambda: handle_search(text_var.get()))

        self.side_menu_state = CurrentSideMenuState.SEARCHING

        self.clear_frame(self.left_upper_frame)
        self.clear_frame(self.left_bottom_frame)

        back_arrow_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/arrow_left.png"),
                                        size=(18, 13))
        back_button = self.parent.styled_button(self.left_upper_frame, text="", height=30, width=40,
                                                corner_radius=5, image=back_arrow_image, command=back)
        back_button.pack(padx=(10, 0), side=ctk.LEFT)

        text_var = ctk.StringVar()
        text_var.trace_add("write", on_text_change)

        search_entry = ctk.CTkEntry(self.left_upper_frame, height=30, textvariable=text_var)
        search_entry.pack(side=ctk.RIGHT, padx=10, fill=ctk.X, expand=True)
        search_entry.focus()

        ctk.CTkLabel(self.left_bottom_frame, text="Start typing to search",
                     font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    def select_side_menu_frame(self, frame: ctk.CTkFrame, user: AccountData | None = None,
                               unselect: bool = False) -> None:
        def bind(widget) -> None:
            widget.bind("<Button-1>", lambda _: self.choose_chat(frame, user))
            widget.bind("<Enter>", lambda _: frame.configure(fg_color="#444444"))
            widget.bind("<Leave>", lambda _: frame.configure(fg_color="transparent"))

        def unbind(widget) -> None:
            widget.unbind("<Button-1>")
            widget.unbind("<Enter>")
            widget.unbind("<Leave>")

        frame.configure(fg_color="transparent" if unselect else "#555555")
        bind(frame) if unselect else unbind(frame)

        for widget in frame.winfo_children():
            bind(widget) if unselect else unbind(widget)

    def init_chats_list(self, count: int) -> list[ctk.CTkFrame]:
        self.clear_frame(self.left_bottom_frame)

        frame = ctk.CTkScrollableFrame(self.left_bottom_frame,
                                       fg_color="transparent", corner_radius=0,
                                       border_width=0, scrollbar_button_color="#444444",
                                       scrollbar_button_hover_color="#545454")
        # noinspection PyProtectedMember
        frame._scrollbar.configure(width=13)
        frame.pack(fill=ctk.BOTH, expand=True)

        frames: list[ctk.CTkFrame] = []

        for user in range(count):
            user_frame = ctk.CTkFrame(frame, fg_color="transparent", corner_radius=0, border_width=0, height=60,
                                      cursor="hand2")
            user_frame.pack(fill=ctk.X)
            frames.append(user_frame)

        return frames

    def init_user_chats_list(self) -> None:
        if not self.user_chats:
            ctk.CTkLabel(self.left_bottom_frame, text="You dont have chats.",
                         font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        else:
            frames: list[ctk.CTkFrame] = self.init_chats_list(len(self.user_chats))
            sorted_user_chats = sorted(self.user_chats.items(),
                                       key=lambda x: datetime.fromisoformat(x[1].data.timestamp), reverse=True)

            i: int = 0

            for key, value in sorted_user_chats:
                data: ChatListItemData = value.data
                frame: ctk.CTkFrame = frames[i]

                top_frame = ctk.CTkFrame(frame, fg_color="transparent", corner_radius=0, border_width=0)
                top_frame.pack(fill=ctk.X, side=ctk.TOP, padx=10, pady=(5, 0))

                ctk.CTkLabel(top_frame, text=data.display_name, font=("Arial", 14, "bold"),
                             wraplength=160, justify=ctk.LEFT,
                             cursor="hand2").pack(side=ctk.LEFT)

                timestamp_label = ctk.CTkLabel(top_frame, text=iso_to_hm(data.timestamp), font=("Arial", 12))
                timestamp_label.pack(side=ctk.RIGHT, padx=(10, 0))

                last_message_label = ctk.CTkLabel(frame, text=format_last_message(data.last_message),
                                                  font=("Arial", 12), cursor="hand2")
                last_message_label.pack(side=ctk.BOTTOM, anchor=ctk.W, padx=10, pady=(0, 5))

                self.user_chats[key].frame = frame  # type: ignore
                self.user_chats[key].timestamp_label = timestamp_label  # type: ignore
                self.user_chats[key].last_message_label = last_message_label  # type: ignore

                unselect: bool = False if self.current_chat and data.user_id == self.current_chat.user.user_id \
                    else True

                user = AccountData(user_id=data.user_id, display_name=data.display_name, username=data.username)
                self.select_side_menu_frame(frame, user=user, unselect=unselect)

                if not unselect:
                    self.current_chat.chat_list_frame = frame

                i += 1

    def init_search_results(self, results: list[AccountData] | None, text: str) -> None:
        self.clear_frame(self.left_bottom_frame)

        if not text.strip():
            ctk.CTkLabel(self.left_bottom_frame, text="Start typing to search",
                         font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        elif results:
            frames: list[ctk.CTkFrame] = self.init_chats_list(len(results))

            for i, user in enumerate(results):
                frame = frames[i]

                if frame.winfo_exists():
                    ctk.CTkLabel(frame, text=user.display_name, font=("Arial", 14, "bold"),
                                 wraplength=160, justify=ctk.LEFT,
                                 cursor="hand2").pack(side=ctk.TOP, anchor=ctk.W, padx=10, pady=(5, 0))
                    ctk.CTkLabel(frame, text=f"@{user.username}", font=("Arial", 12),
                                 cursor="hand2").pack(side=ctk.BOTTOM, anchor=ctk.W, padx=10, pady=(0, 5))

                    self.select_side_menu_frame(frame, user=user, unselect=True)

        else:
            ctk.CTkLabel(self.left_bottom_frame, text="No results found",
                         font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    def choose_chat(self, frame: ctk.CTkFrame, user: AccountData) -> None:
        if self.current_chat and self.current_chat.chat_list_frame.winfo_exists():
            self.select_side_menu_frame(frame=self.current_chat.chat_list_frame, user=self.current_chat.user,
                                        unselect=True)

        if not self.current_chat:
            self.current_chat = CurrentChat(chat_list_frame=frame, user=user)
        else:
            self.current_chat.chat_list_frame = frame
            self.current_chat.user = user

        self.select_side_menu_frame(frame)
        self.init_chat()

    def init_chat(self, is_close: bool = False) -> None:
        def send_message() -> None:
            text: str = self.current_chat.textbox.get(1.0, ctk.END).strip()

            if text.strip():
                temp_id = str(uuid.uuid4())

                self.handle_new_message(text=text, message_id=temp_id, user_id=self.current_chat.user.user_id,
                                        timestamp=datetime.now().isoformat(),
                                        display_name=app.settings.account_data.display_name,
                                        username=app.settings.account_data.username, status=MessageStatus.SENT)

                self.current_chat.textbox.delete(1.0, ctk.END)

                time.sleep(0.1)

                data: dict = {
                    "type": "send_message",
                    "temp_id": temp_id,
                    "receiver_id": self.current_chat.user.user_id,
                    "message": text
                }

                self.parent.ws_client.send(data)

        def on_enter(event):
            if event.state & 0x0001:
                return None
            else:
                send_message()
                return "break"

        if is_close:
            self.clear_frame(self.right_upper_frame)
            self.clear_frame(self.right_bottom_frame)

            if self.current_chat:
                if self.current_chat.chat_list_frame.winfo_exists():
                    self.select_side_menu_frame(frame=self.current_chat.chat_list_frame, user=self.current_chat.user,
                                                unselect=True)
                self.current_chat = None

            frame = ctk.CTkFrame(self.right_bottom_frame, fg_color="#343434", corner_radius=20)
            frame.place(rely=0.5, relx=0.5, anchor=ctk.CENTER)

            ctk.CTkLabel(frame, text="Select a chat to start messaging").pack(padx=18)
            self.parent.unbind("<Return>")
        else:
            if self.current_chat.display_name_label and self.current_chat.display_name_label.winfo_exists():
                self.current_chat.display_name_label.configure(text=self.current_chat.user.display_name)
                self.current_chat.username_label.configure(text=f"@{self.current_chat.user.username}")
                self.current_chat.textbox.delete(1.0, ctk.END)
                # noinspection PyProtectedMember
                self.current_chat.messages_frame._parent_canvas.yview_moveto(0.0)
            else:
                self.clear_frame(self.right_upper_frame)
                self.clear_frame(self.right_bottom_frame)

                display_name_label = ctk.CTkLabel(self.right_upper_frame, text=self.current_chat.user.display_name,
                                                  font=("Arial", 14, "bold"))
                display_name_label.pack(padx=15, anchor=ctk.W, side=ctk.TOP)
                self.current_chat.display_name_label = display_name_label

                username_label = ctk.CTkLabel(self.right_upper_frame, text=f"@{self.current_chat.user.username}",
                                              font=("Arial", 12))
                username_label.pack(padx=15, anchor=ctk.W, side=ctk.BOTTOM)
                self.current_chat.username_label = username_label

                messages_frame = ctk.CTkScrollableFrame(self.right_bottom_frame, fg_color="transparent",
                                                        corner_radius=0, border_width=0,
                                                        scrollbar_button_color="#444444",
                                                        scrollbar_button_hover_color="#545454")
                messages_frame.pack(fill=ctk.BOTH, expand=True)

                # noinspection PyProtectedMember
                messages_frame._scrollbar.configure(width=13)

                self.current_chat.messages_frame = messages_frame

                entry_frame = ctk.CTkFrame(self.right_bottom_frame, fg_color="#343434", height=50, border_width=1,
                                           corner_radius=0, border_color="#292929")
                entry_frame.pack_propagate(False)
                entry_frame.pack(fill=ctk.X, side=ctk.BOTTOM)

                textbox = ctk.CTkTextbox(entry_frame, height=30, border_width=0, corner_radius=0,
                                         font=("Arial", 13), fg_color="transparent", pady=10, padx=10)
                textbox.pack(expand=True, fill=ctk.X, padx=1, anchor=ctk.CENTER, pady=1, side=ctk.LEFT)

                self.current_chat.textbox = textbox

                send_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/send.png"), size=(24, 24))
                send_button = ctk.CTkButton(entry_frame, text="", image=send_image, width=24, height=24,
                                            fg_color="transparent", hover_color="#444444",
                                            command=send_message)
                send_button.pack(side=ctk.LEFT, padx=10)

                self.parent.bind("<Return>", on_enter)

            if self.current_chat.user.user_id not in self.messages_cache:
                handle_get_messages()
            else:
                self.init_messages(self.messages_cache[self.current_chat.user.user_id].messages(),
                                   self.current_chat.user.user_id,
                                   clear_messages_frame=True)

    def handle_new_message(self, text: str, message_id: str | int, user_id: int, timestamp: str, display_name: str,
                           username: str, status: MessageStatus) -> None:
        if user_id in self.user_chats:
            chat_list_item = self.user_chats[user_id]

            self.user_chats[user_id].data.last_message = text
            self.user_chats[user_id].data.timestamp = timestamp

            if (self.left_bottom_frame.winfo_children()[0].winfo_children()[0].
                    winfo_children()[0].winfo_children()[0] == chat_list_item.frame):  # Кастыль)
                if chat_list_item.last_message_label and chat_list_item.last_message_label.winfo_exists():
                    chat_list_item.last_message_label.configure(text=format_last_message(text))
                    chat_list_item.timestamp_label.configure(text=iso_to_hm(timestamp))
            else:
                self.init_user_chats_list()
        else:
            new_chat_list_data = ChatListItemData(user_id=user_id, display_name=display_name, username=username,
                                                  timestamp=timestamp, last_message=text)

            chat_list_item = ChatListItem(data=new_chat_list_data)
            self.user_chats[user_id] = chat_list_item

            if self.side_menu_state == CurrentSideMenuState.CHATS:
                self.init_user_chats_list()

        message = MessageData(message_id=message_id, display_name=display_name, timestamp=timestamp,
                              message=text, status=status)

        if user_id not in self.messages_cache:
            message_list = MessageList()
            message_list.add_new(message_id, message)
            self.messages_cache[user_id] = MessagesCache(messages=message_list, has_more=False)
        else:
            self.messages_cache[user_id].messages.add_new(message_id, message)

        if self.current_chat:
            self.init_messages({message_id: message}, user_id, new_message=True)

    def init_messages(self, messages: dict, user_id: int, new_message: bool = False,
                      clear_messages_frame: bool = False) -> None:
        if not new_message:
            AppContext.loading_window.start_loading()

        if clear_messages_frame:
            self.clear_frame(self.current_chat.messages_frame)

        messages_frames: dict[ctk.CTkFrame, MessageData] = {}

        for message_id, message in messages.items():
            color: str = "#444444" if message.display_name == app.settings.account_data.display_name else "#343434"

            message_frame = ctk.CTkFrame(self.current_chat.messages_frame, fg_color=color, corner_radius=17,
                                         border_width=0, height=70, width=90)

            if (self.current_chat.first_message_frame and self.current_chat.first_message_frame.winfo_exists() and
                    not new_message):
                message_frame.pack(padx=10, pady=10, anchor=ctk.SW, before=self.current_chat.first_message_frame)
                self.current_chat.first_message_frame = message_frame
            else:
                message_frame.pack(padx=10, pady=10, anchor=ctk.SW)
                self.current_chat.last_message_frame = message_frame

            messages_frames[message_frame] = message

        for frame, message in messages_frames.items():
            def load_message(data: MessageData) -> None:
                content_frame = ctk.CTkFrame(frame, fg_color="transparent", corner_radius=0, border_width=0)
                content_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

                ctk.CTkLabel(content_frame, text=data.display_name,
                             font=("Arial", 14, "bold"), justify=ctk.LEFT,
                             wraplength=300).pack(side=ctk.TOP, anchor=ctk.W, padx=(0, 30))

                bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent", corner_radius=0, border_width=0)
                bottom_frame.pack(side=ctk.BOTTOM, fill=ctk.X)

                ctk.CTkLabel(bottom_frame, text=data.message, justify=ctk.LEFT,
                             wraplength=300).pack(side=ctk.LEFT, anchor=ctk.W)

                right_frame = ctk.CTkFrame(bottom_frame, fg_color="transparent", corner_radius=0, border_width=0)
                right_frame.pack(side=ctk.RIGHT, padx=(10, 0), anchor=ctk.SE)

                timestamp_label = ctk.CTkLabel(right_frame, text=iso_to_hm(data.timestamp))
                timestamp_label.pack(side=ctk.LEFT, anchor=ctk.SW)
                self.messages_cache[user_id].messages[data.message_id].timestamp_label = timestamp_label

                image = ctk.CTkImage(light_image=Image.open(f"app/assets/icons/{data.status.value}.png"),
                                     size=(12, 12))
                status_label = ctk.CTkLabel(right_frame, text="", image=image)
                status_label.pack(side=ctk.RIGHT, padx=(10, 0))
                self.messages_cache[user_id].messages[data.message_id].status_label = status_label

                # noinspection PyProtectedMember
                # noinspection PyTypeChecker
                self.parent.after(100, lambda: self.current_chat.messages_frame._parent_canvas.yview_moveto(1.0))

            threading.Thread(target=load_message, args=(message,)).start()

        if not new_message:
            AppContext.loading_window.finish_loading()

    def change_message_status(self, message_id: int, status: MessageStatus, timestamp: str | None = None,
                              temp_id: str | None = None, user_id: int | None = None) -> None:
        if status == MessageStatus.RECEIVED:
            self.messages_cache[user_id].messages[temp_id].status = status
            self.messages_cache[user_id].messages[temp_id].timestamp = timestamp

            self.messages_cache[user_id].messages.add_new(message_id, self.messages_cache[user_id].messages[temp_id])
            self.messages_cache[user_id].messages.pop_by_id(temp_id)
        elif status == MessageStatus.READ:
            self.messages_cache[user_id].messages[message_id].status = status

        if self.messages_cache[user_id].messages[message_id].status_label.winfo_exists():
            image = ctk.CTkImage(light_image=Image.open(f"app/assets/icons/{status.value}.png"), size=(12, 12))
            self.messages_cache[user_id].messages[message_id].status_label.configure(image=image)

            if status == MessageStatus.RECEIVED:
                self.messages_cache[user_id].messages[message_id].timestamp_label.configure(text=iso_to_hm(timestamp))

    @staticmethod
    def clear_frame(frame: ctk.CTkFrame | ctk.CTkScrollableFrame | None) -> None:
        if frame is not None:
            for widget in frame.winfo_children():
                if widget.winfo_exists() and frame.winfo_exists():
                    widget.destroy()
