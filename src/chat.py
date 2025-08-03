
import flet
from flet import View, AppBar, Text, ElevatedButton
import flet as ft
import hashlib
import qrcode
import io
import base64
import threading
import time

def create_user_id(email: str) -> str:
    return hashlib.sha256(email.encode()).hexdigest()

def generate_qr_code(data: str) -> str:
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill='black', back_color='white')

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"

def chat_view(page: ft.Page, supabase, user_email: str):
    user_id = create_user_id(user_email)

    message_list = ft.ListView(expand=True, spacing=5, padding=10)
    input_message = ft.TextField(hint_text="Type a message", expand=True)
    send_btn = ft.ElevatedButton(text="Send")
    target_id_input = ft.TextField(label="Enter Target User ID to Chat", expand=True)
    connect_btn = ft.ElevatedButton(text="Connect")
    qr_img = ft.Image(src=generate_qr_code(user_id), width=150, height=150)

    chat_messages = []
    polling = True

    def update_message_list():
        message_list.controls.clear()
        for msg in chat_messages:
            sender = "You" if msg["sender_id"] == user_id else "Them"
            msg_text = f"{sender}: {msg['content']}"
            message_list.controls.append(ft.Text(msg_text))
        message_list.scroll_to_bottom()
        page.update()

    def load_messages():
        nonlocal chat_messages
        if not target_id_input.value:
            return
        target_user_id = target_id_input.value.strip()
        response = supabase.table("messages").select("*").or_(
            f"(sender_id.eq.{user_id},receiver_id.eq.{target_user_id}),"
            f"(sender_id.eq.{target_user_id},receiver_id.eq.{user_id})"
        ).order("created_at").execute()

        if response.error:
            print("Error loading messages:", response.error)
            return

        chat_messages = response.data or []
        update_message_list()

    def send_message(e):
        if not target_id_input.value:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter a target user ID"))
            page.snack_bar.open = True
            page.update()
            return
        content = input_message.value.strip()
        if not content:
            return
        target_user_id = target_id_input.value.strip()
        data = {
            "sender_id": user_id,
            "receiver_id": target_user_id,
            "content": content,
            "created_at": "now()"
        }
        response = supabase.table("messages").insert(data).execute()
        if response.error:
            print("Error sending message:", response.error)
            return
        input_message.value = ""
        chat_messages.append(data)
        update_message_list()

    def poll_messages():
        while polling:
            load_messages()
            time.sleep(2)

    def connect(e):
        if not target_id_input.value.strip():
            page.snack_bar = ft.SnackBar(ft.Text("Please enter a target user ID"))
            page.snack_bar.open = True
            page.update()
            return
        load_messages()
        threading.Thread(target=poll_messages, daemon=True).start()

    connect_btn.on_click = connect
    send_btn.on_click = send_message

    page.on_close = lambda e: nonlocal_poll_stop()

    def nonlocal_poll_stop():
        nonlocal polling
        polling = False

    return ft.View(
        "/chat",
        [
            ft.Column(
                [
                    ft.Text("Your unique ID (share this):"),
                    qr_img,
                    ft.Text(user_id, selectable=True),
                    ft.Row([target_id_input, connect_btn]),
                    message_list,
                    ft.Row([input_message, send_btn]),
                ],
                expand=True,
            )
        ],
    )
