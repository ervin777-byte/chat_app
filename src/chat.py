import flet as ft
import hashlib
import qrcode
import io
import base64

# --- Helper Functions (Unchanged, they were correct) ---

def create_user_id(email: str) -> str:
    """Creates a unique, deterministic user ID from an email address."""
    return hashlib.sha256(email.encode()).hexdigest()

def generate_qr_code(data: str) -> str:
    """Generates a base64-encoded QR code image from text data."""
    qr = qrcode.QRCode(version=1, box_size=4, border=2)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color='black', back_color='white')

    buffered = io.BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return f"data:image/png;base64,{img_str}"


# --- Main Chat View ---

def chat_view(page: ft.Page, supabase, user_email: str):
    """
    Constructs the chat view, handling message display, sending, and real-time updates.
    
    NOTE: Ensure your Supabase table 'messages' has Row-Level Security (RLS) enabled
    and a default value of 'now()' for the 'created_at' column.
    """
    user_id = create_user_id(user_email)
    
    # This will hold the Supabase Realtime subscription object
    subscription = None
    chat_messages = []

    # --- Flet UI Controls ---

    # CORRECTED: Added auto_scroll=True to automatically scroll down on new messages.
    message_list = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
    
    input_message = ft.TextField(hint_text="Type a message...", expand=True, on_submit=lambda e: send_message(e))
    target_id_input = ft.TextField(label="Enter Target User ID", expand=True)
    qr_img = ft.Image(src=generate_qr_code(user_id), width=150, height=150)

    # --- Core Functions ---

    def update_message_list():
        """Clears and rebuilds the message list from the chat_messages list."""
        message_list.controls.clear()
        for msg in chat_messages:
            sender_name = "You" if msg['sender_id'] == user_id else "Them"
            message_list.controls.append(
                ft.Text(f"{sender_name}: {msg['content']}")
            )
        page.update()

    def on_new_message(payload):
        """Callback for Supabase Realtime subscription. Appends new messages."""
        nonlocal chat_messages
        new_msg = payload['new']
        target_user_id = target_id_input.value.strip()

        # Check if the new message belongs to the current active chat
        is_relevant = (
            (new_msg['sender_id'] == user_id and new_msg['receiver_id'] == target_user_id) or
            (new_msg['sender_id'] == target_user_id and new_msg['receiver_id'] == user_id)
        )

        if is_relevant:
            chat_messages.append(new_msg)
            update_message_list()

    def load_messages():
        """Loads the initial message history for a chat."""
        nonlocal chat_messages
        target_user_id = target_id_input.value.strip()
        if not target_user_id:
            return

        # CORRECTED: Fixed the Supabase .or_() filter syntax and added .execute().
        filter1 = f"and(sender_id.eq.{user_id},receiver_id.eq.{target_user_id})"
        filter2 = f"and(sender_id.eq.{target_user_id},receiver_id.eq.{user_id})"
        
        response = supabase.table("messages").select("*").or_(filter1, filter2).order("created_at").execute()

        if hasattr(response, 'error') and response.error:
            print(f"Error loading messages: {response.error}")
            chat_messages = []
        else:
            chat_messages = response.data or []
        
        update_message_list()

    def send_message(e):
        """Inserts a new message into the Supabase table."""
        target_user_id = target_id_input.value.strip()
        if not target_user_id:
            page.snack_bar = ft.SnackBar(ft.Text("Please connect to a user first."))
            page.snack_bar.open = True
            page.update()
            return
            
        content = input_message.value.strip()
        if not content:
            return

        # CORRECTED: Removed `created_at`. Let the database handle the timestamp.
        data_to_insert = {
            "sender_id": user_id,
            "receiver_id": target_user_id,
            "content": content,
        }
        
        # CORRECTED: Added .execute() to run the query.
        response = supabase.table("messages").insert(data_to_insert).execute()
        
        if hasattr(response, 'error') and response.error:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error sending message: {response.error.message}"))
            page.snack_bar.open = True
        else:
            # The Realtime listener will add the message to the UI, so no manual refresh is needed.
            input_message.value = ""
        
        page.update()

    def connect_to_chat(e):
        """Connects to a chat, loads history, and subscribes to real-time updates."""
        nonlocal subscription
        target_user_id = target_id_input.value.strip()
        if not target_user_id:
            page.snack_bar = ft.SnackBar(ft.Text("Please enter a Target User ID."))
            page.snack_bar.open = True
            page.update()
            return
        
        # Unsubscribe from any previous chat channel to prevent multiple listeners
        if subscription:
            supabase.remove_subscription(subscription)

        # Load initial message history for the new chat
        load_messages()

        # Set up a new Realtime subscription for the current chat
        subscription = supabase.realtime.channel("public:messages").on(
            "postgres_changes",
            {"event": "INSERT", "schema": "public", "table": "messages"},
            on_new_message
        ).subscribe()

        page.snack_bar = ft.SnackBar(ft.Text(f"✅ Chatting with user {target_user_id[:8]}..."))
        page.snack_bar.open = True
        page.update()

    # --- Cleanup ---
    
    def cleanup_on_exit(e):
        """Unsubscribe from Realtime events when the view is closed."""
        nonlocal subscription
        if subscription:
            supabase.remove_subscription(subscription)
    
    page.on_view_pop = cleanup_on_exit
    page.on_disconnect = cleanup_on_exit

    # --- Button and Input Event Handlers ---
    send_btn = ft.ElevatedButton("Send", on_click=send_message)
    connect_btn = ft.ElevatedButton("Chat", on_click=connect_to_chat)

    # --- View Layout ---
    return ft.View(
        "/chat",
        controls=[
            ft.Column(
                controls=[
                    ft.Card(
                        content=ft.Container(
                            padding=15,
                            content=ft.Column([
                                ft.Text("Your User ID", weight=ft.FontWeight.BOLD),
                                ft.Row([qr_img, ft.Text(user_id, selectable=True, expand=True)], alignment=ft.MainAxisAlignment.START, vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                ft.Text("Share this ID or QR code with a friend.", size=12, italic=True, color=ft.Colors.ON_SURFACE_VARIANT),
                            ]),
                        )
                    ),
                    ft.Row([target_id_input, connect_btn]),
                    ft.Divider(height=10),
                    message_list,
                    ft.Row([input_message, send_btn]),
                ],
                expand=True,
            )
        ],
        appbar=ft.AppBar(title=ft.Text("Flet & Supabase Chat 💬"), bgcolor=ft.Colors.ON_SURFACE_VARIANT),
        padding=20,
    )