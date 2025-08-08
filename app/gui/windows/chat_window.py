import customtkinter as ctk
import app.settings
from PIL import Image
from typing import TYPE_CHECKING
from app.services.auth_controller import handle_logout
from app.gui.context import AppContext
from app.services.handle_requests import handle_search, handle_change_display_name, handle_get_messages
from app.services.utils import iso_to_hm

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

        self.username_label: ctk.CTkLabel | None = None
        self.display_name_label: ctk.CTkLabel | None = None
        self.textbox: ctk.CTkTextbox | None = None
        self.messages_frame: ctk.CTkScrollableFrame | None = None

        self.debounce_timer: str | None = None
        self.current_chat: tuple[ctk.CTkFrame, dict] | None = None
        self.last_message_frame: ctk.CTkFrame | None = None

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

        self.init_main_left_side()

        right_side = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        right_side.pack_propagate(False)
        right_side.pack(side=ctk.RIGHT, fill=ctk.BOTH, expand=True)

        self.right_upper_frame = ctk.CTkFrame(right_side, corner_radius=0, height=50, fg_color="#292929")
        self.right_upper_frame.pack_propagate(False)
        self.right_upper_frame.pack(fill=ctk.X)
        self.right_upper_frame.bind("<Button-1>", self.init_main_left_side)

        self.right_bottom_frame = ctk.CTkFrame(right_side, corner_radius=0, fg_color="transparent")
        self.right_bottom_frame.pack_propagate(False)
        self.right_bottom_frame.pack(fill=ctk.BOTH, expand=True)
        self.right_bottom_frame.bind("<Button-1>", self.init_main_left_side)

        self.parent.bind("<Escape>", lambda _: self.init_chat(is_close=True))
        self.init_chat(is_close=True)

    def init_side_menu(self) -> None:
        self.clear_frame(self.left_upper_frame)
        self.clear_frame(self.left_bottom_frame)

        back_arrow_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/arrow_left.png"),
                                        size=(18, 13))
        back_button = self.parent.styled_button(self.left_upper_frame, text="", height=30, width=40,
                                                corner_radius=5, image=back_arrow_image,
                                                command=self.init_main_left_side)
        back_button.pack(padx=(10, 0), side=ctk.LEFT)

        ctk.CTkLabel(self.left_bottom_frame, text="Account", font=("Arial", 17, "bold")
                     ).pack(pady=(10, 0), padx=15, anchor=ctk.W)

        account_info_frame = ctk.CTkFrame(self.left_bottom_frame, height=125)
        account_info_frame.pack(pady=(5, 0), padx=10, fill=ctk.X)

        pencil_icon = ctk.CTkImage(light_image=Image.open("app/assets/icons/pencil.png"), size=(17, 17))

        display_name_frame = ctk.CTkFrame(account_info_frame, fg_color="transparent", height=24)
        display_name_frame.pack(pady=(10, 0), padx=10, anchor=ctk.W, fill=ctk.X)

        display_name = app.settings.account_data["display_name"]
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

        username = app.settings.account_data["username"]
        username_label = ctk.CTkLabel(username_frame, text=f"@{username}", font=("Arial", 12))
        username_label.pack(side=ctk.LEFT)

        self.parent.styled_button(account_info_frame, text="Logout", command=handle_logout
                                  ).pack(pady=10, padx=10, fill=ctk.X)

    def init_main_left_side(self, _=None) -> None:
        self.clear_frame(self.left_upper_frame)
        self.clear_frame(self.left_bottom_frame)

        burger_menu_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/burger_menu.png"), size=(18, 13))
        open_side_menu_button = self.parent.styled_button(self.left_upper_frame, text="", image=burger_menu_image,
                                                          width=40, height=30, corner_radius=5,
                                                          command=self.init_side_menu)
        open_side_menu_button.pack(side=ctk.LEFT, padx=(10, 0))

        search_entry = ctk.CTkEntry(self.left_upper_frame, placeholder_text="Search", height=30)
        search_entry.pack(side=ctk.RIGHT, padx=10, fill=ctk.X, expand=True)
        search_entry.bind("<FocusIn>", self.init_search_left_side)

        ctk.CTkLabel(self.left_bottom_frame, text="You dont have chats.",
                     font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    def init_search_left_side(self, _=None) -> None:
        def cancel_search() -> None:
            if self.debounce_timer:
                self.after_cancel(self.debounce_timer)
                self.debounce_timer = None

        def back() -> None:
            cancel_search()
            self.init_main_left_side()

        def on_text_change(*_) -> None:
            cancel_search()

            # noinspection PyTypeChecker
            self.debounce_timer = self.after(350, lambda: handle_search(text_var.get()))

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

    def bind_chat_frame(self, frame: ctk.CTkFrame, user: dict | None = None, is_unbind: bool = False) -> None:
        def bind(widget) -> None:
            widget.bind("<Button-1>", lambda _: self.choose_chat(frame, user))
            widget.bind("<Enter>", lambda _: frame.configure(fg_color="#444444"))
            widget.bind("<Leave>", lambda _: frame.configure(fg_color="transparent"))

        def unbind(widget) -> None:
            widget.unbind("<Button-1>")
            widget.unbind("<Enter>")
            widget.unbind("<Leave>")

        frame.configure(fg_color="#555555" if is_unbind else "transparent")
        unbind(frame) if is_unbind else bind(frame)

        for widget in frame.winfo_children():
            unbind(widget) if is_unbind else bind(widget)

    def init_chats_list(self, chats: dict) -> None:
        frame = ctk.CTkScrollableFrame(self.left_bottom_frame,
                                       fg_color="transparent", corner_radius=0,
                                       border_width=0, scrollbar_button_color="#444444",
                                       scrollbar_button_hover_color="#545454")
        # noinspection PyProtectedMember
        frame._scrollbar.configure(width=13)
        frame.pack(fill=ctk.BOTH, expand=True)

        for user in chats["users"]:
            user_frame = ctk.CTkFrame(frame, fg_color="transparent", corner_radius=0, border_width=0, height=60,
                                      cursor="hand2")
            user_frame.pack(fill=ctk.X)

            ctk.CTkLabel(user_frame, text=user["display_name"], font=("Arial", 14, "bold"),
                         wraplength=160, justify=ctk.LEFT,
                         cursor="hand2").pack(side=ctk.TOP, anchor=ctk.W, padx=10, pady=(5, 0))
            ctk.CTkLabel(user_frame, text=f"@{user["username"]}", font=("Arial", 12),
                         cursor="hand2").pack(side=ctk.BOTTOM, anchor=ctk.W, padx=10, pady=(0, 5))

            self.bind_chat_frame(user_frame, user=user)

    def init_search_results_left_side(self, results: dict | None, no_text: bool) -> None:
        self.clear_frame(self.left_bottom_frame)

        if no_text:
            ctk.CTkLabel(self.left_bottom_frame, text="Start typing to search",
                         font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)
        elif results is not None:
            self.init_chats_list(results)
        else:
            ctk.CTkLabel(self.left_bottom_frame, text="No results found",
                         font=("Arial", 15, "bold")).place(relx=0.5, rely=0.5, anchor=ctk.CENTER)

    def choose_chat(self, frame: ctk.CTkFrame, user: dict) -> None:
        if self.current_chat is not None and self.current_chat[0].winfo_exists():
            self.bind_chat_frame(*self.current_chat)

        self.current_chat = [frame, user]
        self.bind_chat_frame(frame, is_unbind=True)

        self.init_chat()

    def init_chat(self, is_close: bool = False) -> None:
        def send_message() -> None:
            text: str = self.textbox.get(1.0, ctk.END).strip()

            if text:
                data: dict = {
                    "type": "send_message",
                    "receiver_id": self.current_chat[1]["user_id"],
                    "message": text
                }

                self.parent.ws_client.send(data)
                self.textbox.delete(1.0, ctk.END)

        def on_enter(event):
            if event.state & 0x0001:
                self.textbox.insert("insert", "\n")
                return None
            else:
                send_message()
                return "break"

        if is_close:
            self.clear_frame(self.right_upper_frame)
            self.clear_frame(self.right_bottom_frame)

            if self.current_chat is not None:
                if self.current_chat[0].winfo_exists():
                    self.bind_chat_frame(*self.current_chat)
                self.current_chat = None

            frame = ctk.CTkFrame(self.right_bottom_frame, fg_color="#343434", corner_radius=20)
            frame.place(rely=0.5, relx=0.5, anchor=ctk.CENTER)

            ctk.CTkLabel(frame, text="Select a chat to start messaging").pack(padx=18)
            self.parent.unbind("<Return>")
        else:
            if self.display_name_label and self.display_name_label.winfo_exists():
                self.display_name_label.configure(text=self.current_chat[1]["display_name"])
                self.username_label.configure(text=f"@{self.current_chat[1]['username']}")
                self.textbox.delete(1.0, ctk.END)
                return

            self.clear_frame(self.right_upper_frame)
            self.clear_frame(self.right_bottom_frame)

            self.display_name_label = ctk.CTkLabel(self.right_upper_frame, text=self.current_chat[1]["display_name"],
                                                   font=("Arial", 14, "bold"))
            self.display_name_label.pack(padx=15, anchor=ctk.W, side=ctk.TOP)

            self.username_label = ctk.CTkLabel(self.right_upper_frame, text=f"@{self.current_chat[1]["username"]}",
                                               font=("Arial", 12))
            self.username_label.pack(padx=15, anchor=ctk.W, side=ctk.BOTTOM)

            self.messages_frame = ctk.CTkScrollableFrame(self.right_bottom_frame, fg_color="transparent",
                                                         corner_radius=0, border_width=0,
                                                         scrollbar_button_color="#444444",
                                                         scrollbar_button_hover_color="#545454")
            self.messages_frame.pack(fill=ctk.BOTH, expand=True)

            # noinspection PyProtectedMember
            self.messages_frame._scrollbar.configure(width=13)

            entry_frame = ctk.CTkFrame(self.right_bottom_frame, fg_color="#343434", height=50, border_width=1,
                                       corner_radius=0, border_color="#292929")
            entry_frame.pack_propagate(False)
            entry_frame.pack(fill=ctk.X, side=ctk.BOTTOM)

            self.textbox = ctk.CTkTextbox(entry_frame, height=30, border_width=0, corner_radius=0,
                                          font=("Arial", 13), fg_color="transparent", pady=10, padx=10)
            self.textbox.pack(expand=True, fill=ctk.X, padx=1, anchor=ctk.CENTER, pady=1, side=ctk.LEFT)

            send_image = ctk.CTkImage(light_image=Image.open("app/assets/icons/send.png"), size=(24, 24))
            send_button = ctk.CTkButton(entry_frame, text="", image=send_image, width=24, height=24,
                                        fg_color="transparent", hover_color="#444444",
                                        command=send_message)
            send_button.pack(side=ctk.LEFT, padx=10)

            self.parent.bind("<Return>", on_enter)
            handle_get_messages()

    def init_messages(self, messages: list[dict], new_message: bool = False) -> None:
        AppContext.loading_window.start_loading()

        for message in messages:
            message_frame = ctk.CTkFrame(self.messages_frame, fg_color="#343434", corner_radius=17, border_width=0,
                                         height=70, width=90)

            if self.last_message_frame is not None and self.last_message_frame.winfo_exists() and not new_message:
                message_frame.pack(padx=10, pady=10, anchor=ctk.W, before=self.last_message_frame)
            else:
                message_frame.pack(padx=10, pady=10, anchor=ctk.W)

            self.last_message_frame = message_frame

            content_frame = ctk.CTkFrame(message_frame, fg_color="transparent", corner_radius=0, border_width=0)
            content_frame.pack(fill=ctk.BOTH, expand=True, padx=10, pady=10)

            ctk.CTkLabel(content_frame, text=message["sender_display_name"],
                         font=("Arial", 14, "bold"), justify=ctk.LEFT,
                         wraplength=300).pack(side=ctk.TOP, anchor=ctk.W, padx=(0, 30))

            bottom_frame = ctk.CTkFrame(content_frame, fg_color="transparent", corner_radius=0, border_width=0)
            bottom_frame.pack(side=ctk.BOTTOM, fill=ctk.X)

            ctk.CTkLabel(bottom_frame, text=message["message"], justify=ctk.LEFT,
                         wraplength=300).pack(side=ctk.LEFT, anchor=ctk.W)

            ctk.CTkLabel(bottom_frame, text=iso_to_hm(message["timestamp"])
                         ).pack(side=ctk.RIGHT, padx=(10, 0), anchor=ctk.SE)

        # noinspection PyProtectedMember
        # noinspection PyTypeChecker
        self.after(100, lambda: self.messages_frame._parent_canvas.yview_moveto(1.0))
        AppContext.loading_window.finish_loading()

    @staticmethod
    def clear_frame(frame: ctk.CTkFrame) -> None:
        for widget in frame.winfo_children():
            widget.destroy()
