import os
from dotenv import load_dotenv
import flet
from flet import (Page, Text, TextField, ElevatedButton, Column, Container, Row, SnackBar,)
from supabase import create_client, Client

# Load environment variables from .env file
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

email_tf = TextField(label="Email", width=300)
password_tf = TextField(label="Password", password=True, width=300)

def login(event):
    email = email_tf.value
    password = password_tf.value

    try:
        user = supabase.auth.sign_in_with_password(email=email, password=password)
        Page.snack_bar = SnackBar(Text(f"Logged in as {user.user.email}"))
        Page.snack_bar.open = True
    except Exception as e:
        Page.snack_bar = SnackBar(Text(str(e)))
        Page.snack_bar.open = True

def signup(event):
    email = email_tf.value
    password = password_tf.value

    try:
        user = supabase.auth.sign_up(email=email, password=password)
        Page.snack_bar = SnackBar(Text(f"Signed up as {user.user.email}"))
        Page.snack_bar.open = True
    except Exception as e:
        Page.snack_bar = SnackBar(Text(str(e)))
        Page.snack_bar.open = True


def main(page: Page):

    page.title = "Authentication zone"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    login_btn = ElevatedButton("Login", on_click=login)
    signup_btn = ElevatedButton("Sign Up", on_click=signup)

    column = Column(
        controls=[
            email_tf,
            password_tf,
            Row(
                [login_btn, signup_btn],
                alignment="spaceBetween",
            ),
        ],
        spacing=20,
    )

    page.add(column)

flet.app(main)
