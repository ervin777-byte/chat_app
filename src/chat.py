import flet as ft
import hashlib
import qrcode
import io
import base64

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

def chat_view(page: ft.Page, supabase, user_id: str):
    """
    Constructs the chat view, handling message display, sending, and real-time updates.
    
    NOTE: Ensure your Supabase table 'messages' has Row-Level Security (RLS) enabled
    and a default value of 'now()' for the 'created_at' column.
    """
    
    # This will hold the Supabase Realtime subscription object
    subscription = None
    chat_messages = []

    # --- Flet UI Controls ---

    # CORRECTED: Added auto_scroll=True to automatically scroll down on new messages.
    # message_list = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
    
    # input_message = ft.TextField(hint_text="Type a message...", expand=True, on_submit=lambda e: send_message(e))
    # target_id_input = ft.TextField(label="Enter Target User ID", expand=True)
    # qr_img = ft.Image(src=generate_qr_code(user_id), width=150, height=150)

    message_list = ft.ListView(expand=True, spacing=10, padding=20, auto_scroll=True)
    input_message = ft.TextField(hint_text="Type a message...", expand=True, on_submit=lambda e: send_message(e))
    target_id_input = ft.TextField(label="Enter or select a contact's User ID", expand=True)
    
    ## NEW: Controls for the drawer (user info & contacts)
    qr_img = ft.Image(src=generate_qr_code(user_id), width=150, height=150)
    new_contact_id_input = ft.TextField(label="Enter Contact's UUID")
    contacts_list_view = ft.ListView(expand=True, spacing=5)

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

        try:
            # Query 1: Messages sent by you to the target
            response1 = supabase.table("messages").select("*").match({
                "sender_id": user_id,
                "receiver_id": target_user_id
            }).execute()

            # Query 2: Messages sent by the target to you
            response2 = supabase.table("messages").select("*").match({
                "sender_id": target_user_id,
                "receiver_id": user_id
            }).execute()
            
            # Combine the data from both responses
            all_data = (response1.data or []) + (response2.data or [])

            # Sort the combined list by the 'created_at' timestamp
            # This ensures the chat is in the correct chronological order
            chat_messages = sorted(all_data, key=lambda msg: msg['created_at'])
            
        except Exception as e:
            print(f"An error occurred loading messages: {e}")
            chat_messages = []
        
        update_message_list()

    def send_message(e):
        """Inserts a new message into the Supabase table."""
        target_user_id = target_id_input.value.strip()
        if not target_user_id:
            page.open(ft.SnackBar(ft.Text("Please connect to a user first.")))
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
            page.open(ft.SnackBar(ft.Text(f"Error sending message: {response.error.message}")))
            page.update()
        else:
            # The Realtime listener will add the message to the UI, so no manual refresh is needed.
            input_message.value = ""
        
        page.update()

    def connect_to_chat(e):
        """Connects to a chat, loads history, and subscribes to real-time updates."""
        nonlocal subscription
        target_user_id = target_id_input.value.strip()
        if not target_user_id:
            page.open(ft.SnackBar(ft.Text("Please enter a Target User ID.")))
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

        page.open(ft.SnackBar(ft.Text(f"✅ Chatting with user {target_user_id[:8]}...")))
        page.update()

    ## NEW: Contact Management Functions
    def add_contact(e):
        """Saves a new contact's UUID to the Supabase 'contacts' table."""
        contact_id = new_contact_id_input.value.strip()
        if not contact_id:
            # You can add a snackbar here for feedback
            return

        try:
            # Check if contact already exists to avoid duplicates
            existing = supabase.table("contacts").select("id").match({"user_id": user_id, "contact_uuid": contact_id}).execute()
            if not existing.data:
                supabase.table("contacts").insert({
                    "user_id": user_id,
                    "contact_uuid": contact_id
                }).execute()
                page.open(ft.SnackBar(ft.Text("✅ Contact saved!")))
                load_contacts() # Refresh the list
                new_contact_id_input.value = ""
            else:
                page.open(ft.SnackBar(ft.Text("ℹ️ Contact already exists.")))

        except Exception as e:
            page.snack_bar = ft.SnackBar(ft.Text(f"Error saving contact: {e}"))

        page.update()

    def load_contacts():
        """Loads the user's saved contacts from Supabase into the drawer."""
        contacts_list_view.controls.clear()
        try:
            response = supabase.table("contacts").select("contact_uuid").eq("user_id", user_id).execute()
            if response.data:
                for contact in response.data:
                    contact_uuid = contact['contact_uuid']
                    contacts_list_view.controls.append(
                        ft.ListTile(
                            leading=ft.Icon(ft.icons.PERSON_OUTLINE),
                            title=ft.Text(f"User: {contact_uuid[:8]}..."),
                            # Use a lambda to capture the correct uuid for the on_click event
                            on_click=lambda _, c=contact_uuid: start_chat_with_contact(c)
                        )
                    )
        except Exception as e:
            print(f"Error loading contacts: {e}") # Print error to console
        page.update()

    def start_chat_with_contact(contact_uuid: str):
        """Fills the target ID input and connects to the selected contact."""
        target_id_input.value = contact_uuid
        page.end_drawer.open = False # Close the drawer
        connect_to_chat(None) # Call the existing connect function
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
    connect_btn = ft.ElevatedButton("connect/refresh", on_click=connect_to_chat)

    ## NEW: Function to open the right-side drawer
    def open_drawer(e):
        page.end_drawer.open = True
        page.update()

    ## MODIFIED: Initial data loading
    load_contacts()

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
        appbar=ft.AppBar(title=ft.Text("Flet & Supabase Chat 💬"), bgcolor=ft.Colors.BLUE),
        padding=20,
    )