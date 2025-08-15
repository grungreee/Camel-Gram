import customtkinter as ctk
import app.settings
import threading
from PIL import Image
from typing import TYPE_CHECKING
from datetime import datetime
from app.gui.context import AppContext
from app.schemas import AccountData, ChatListItemData, ChatListItem, MessageData, CurrentChat, CurrentSideMenuState
from app.services.auth_controller import handle_logout
from app.services.handle_requests import handle_search, handle_change_display_name, handle_get_messages
from app.services.utils import iso_to_hm
from collections import defaultdict

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
        self.messages_cache: dict[int, list[MessageData]] = defaultdict(list)

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

            i: int = 0

            for key, value in self.user_chats.items():
                data: ChatListItemData = value.data
                frame: ctk.CTkFrame = frames[i]

                top_frame = ctk.CTkFrame(frame, fg_color="transparent", corner_radius=0, border_width=0)
                top_frame.pack(fill=ctk.X, side=ctk.TOP, padx=10, pady=(5, 0))

                ctk.CTkLabel(top_frame, text=data.display_name, font=("Arial", 14, "bold"),
                             wraplength=160, justify=ctk.LEFT,
                             cursor="hand2").pack(side=ctk.LEFT)

                timestamp_label = ctk.CTkLabel(top_frame, text=iso_to_hm(data.timestamp), font=("Arial", 12))
                timestamp_label.pack(side=ctk.RIGHT, padx=(10, 0))

                last_message_label = ctk.CTkLabel(frame, text=data.last_message, font=("Arial", 12), cursor="hand2")
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
            self.current_chat = CurrentChat(chat_list_frame=frame, user=user, messages_frame=None,
                                            display_name_label=None, username_label=None, textbox=None,
                                            first_message_frame=None)
        else:
            self.current_chat.chat_list_frame = frame
            self.current_chat.user = user

        self.select_side_menu_frame(frame)
        self.init_chat()

    def init_chat(self, is_close: bool = False) -> None:
        def send_message() -> None:
            text: str = self.current_chat.textbox.get(1.0, ctk.END).strip()

            if text:
                data: dict = {
                    "type": "send_message",
                    "receiver_id": self.current_chat.user.user_id,
                    "display_name": app.settings.account_data.display_name,
                    "username": app.settings.account_data.username,
                    "message": text
                }

                self.parent.ws_client.send(data)

                self.handle_new_message(text=text, user_id=app.settings.account_data.user_id,
                                        chat_with_id=self.current_chat.user.user_id,
                                        timestamp=datetime.now().isoformat(),
                                        display_name=self.current_chat.user.display_name,
                                        username=self.current_chat.user.username)
                self.current_chat.textbox.delete(1.0, ctk.END)

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
                self.init_messages(self.current_chat.user.user_id, clear_messages_frame=True)

    def handle_new_message(self, text: str, user_id: int, chat_with_id: int, timestamp: str, display_name: str,
                           username: str) -> None:
        if chat_with_id in self.user_chats:
            chat_list_item = self.user_chats[chat_with_id]

            if chat_list_item.last_message_label and chat_list_item.last_message_label.winfo_exists():
                chat_list_item.last_message_label.configure(text=text)
                chat_list_item.timestamp_label.configure(text=iso_to_hm(timestamp))
            self.user_chats[chat_with_id].data.last_message = text
            self.user_chats[chat_with_id].data.timestamp = timestamp
        else:
            new_chat_list_data = ChatListItemData(user_id=chat_with_id, display_name=display_name, username=username,
                                                  timestamp=timestamp, last_message=text)

            chat_list_item = ChatListItem(frame=None, last_message_label=None, timestamp_label=None,
                                          data=new_chat_list_data)
            self.user_chats[chat_with_id] = chat_list_item

            if self.side_menu_state == CurrentSideMenuState.CHATS:
                self.init_user_chats_list()

        message = MessageData(user_id=user_id,
                              display_name=app.settings.account_data.display_name
                              if user_id == app.settings.account_data.user_id else display_name,
                              timestamp=timestamp, message=text)

        self.messages_cache[chat_with_id].append(message)

        if self.current_chat:
            self.init_messages(chat_with_id, new_message=True)

    def init_messages(self, user_id: int, new_message: bool = False, clear_messages_frame: bool = False) -> None:
        def init_():
            if not new_message:
                AppContext.loading_window.start_loading()

            if clear_messages_frame:
                self.clear_frame(self.current_chat.messages_frame)

            messages_frames: dict[ctk.CTkFrame, MessageData] = {}
            messages: list[MessageData] = self.messages_cache[user_id]

            for message in reversed([messages[-1]] if new_message else messages):
                color: str = "#444444" if message.display_name == app.settings.account_data.display_name else "#343434"

                message_frame = ctk.CTkFrame(self.current_chat.messages_frame, fg_color=color, corner_radius=17,
                                             border_width=0, height=70, width=90)

                if (self.current_chat.first_message_frame and self.current_chat.first_message_frame.winfo_exists()
                        and not new_message):
                    message_frame.pack(padx=10, pady=10, anchor=ctk.W, before=self.current_chat.first_message_frame)
                    self.current_chat.first_message_frame = message_frame
                else:
                    message_frame.pack(padx=10, pady=10, anchor=ctk.W)

                messages_frames[message_frame] = message

            for frame, message in messages_frames.items():
                def load_message(message_: MessageData) -> None:
                    content_frame = ctk.CTkFrame(frame, fg_color="transparent", corner_radius=0, border_width=0)
                    content_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

                    ctk.CTkLabel(content_frame, text=message_.display_name,
                                 font=("Arial", 14, "bold"), justify=ctk.LEFT,
                                 wraplength=300).pack(side=ctk.TOP, anchor=ctk.W, padx=(0, 30))

                    bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent", corner_radius=0, border_width=0)
                    bottom_frame.pack(side=ctk.BOTTOM, fill=ctk.X)

                    ctk.CTkLabel(bottom_frame, text=message_.message, justify=ctk.LEFT,
                                 wraplength=300).pack(side=ctk.LEFT, anchor=ctk.W)

                    ctk.CTkLabel(bottom_frame, text=iso_to_hm(message_.timestamp)).pack(side=ctk.RIGHT,
                                                                                        padx=(10, 0), anchor=ctk.SE)

                    # noinspection PyProtectedMember
                    # noinspection PyTypeChecker
                    self.parent.after(100, lambda: self.current_chat.messages_frame._parent_canvas.yview_moveto(1.0))

                threading.Thread(target=load_message, args=(message,), daemon=True).start()

            if not new_message:
                AppContext.loading_window.finish_loading()

        threading.Thread(target=init_, daemon=True).start()

    @staticmethod
    def clear_frame(frame: ctk.CTkFrame | ctk.CTkScrollableFrame | None) -> None:
        if frame is not None:
            for widget in frame.winfo_children():
                if widget.winfo_exists() and frame.winfo_exists():
                    widget.destroy()
