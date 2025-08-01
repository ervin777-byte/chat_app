import os
from dotenv import load_dotenv
import flet
from flet import (Page, Text, TextField, ElevatedButton, Column, Container, Row, SnackBar,)
from supabase import create_client, Client

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

email_tf = TextField(label="Email", width=300)
password_tf = TextField(label="Password", password=True, width=300)

def main(page: Page):
    page.title = "Authentication zone"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    login_btn = ElevatedButton("Login", on_click=lambda e: login(page, e))
    signup_btn = ElevatedButton("Sign Up", on_click=lambda e: signup(page, e))

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
        horizontal_alignment=flet.CrossAxisAlignment.CENTER,
    )

    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(
                flet.View(
                    "/",
                    [
                        flet.AppBar(title=flet.Text("Authentication Zone"), bgcolor=flet.Colors.RED),
                        column # Now 'column' is defined and can be used here
                    ],
                    vertical_alignment=flet.CrossAxisAlignment.CENTER,
                    horizontal_alignment=flet.CrossAxisAlignment.CENTER,
                )
            )
        elif page.route == "/chat":
            page.views.append(
                flet.View(
                    "/chat",
                    [
                        flet.AppBar(title=flet.Text("Chat"), bgcolor=flet.Colors.PURPLE),
                        flet.Text("Welcome to the chat page!"),
                        flet.ElevatedButton("Go back to Home", on_click=lambda e: page.go("/"))
                    ],
                    vertical_alignment=flet.CrossAxisAlignment.CENTER,
                    horizontal_alignment=flet.CrossAxisAlignment.CENTER,
                )
            )
        page.update()

    def view_pop(view):
        page.views.pop()
        top_view = page.views[0]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go(page.route)

def login(page: Page, event):
    email = email_tf.value
    password = password_tf.value

    try:
        user_session = supabase.auth.sign_in_with_password({"email": email, "password": password})
        page.open = SnackBar(Text(f"Logged in as {user_session.user.email}"))
        page.update()
        page.go("/chat")
    except Exception as e:
        page.open = SnackBar(Text(str(e)))
        page.update()

def signup(page: Page, event):
    email = email_tf.value
    password = password_tf.value

    try:
        user = supabase.auth.sign_up({"email": email,"password": password,})
        if user.user:
            message = f"Signed up as {user.user.email}"
        else:
            message = "Sign up failed. No user returned."

        page.open = SnackBar(Text(message))
        page.update()
    except Exception as e:
        page.open = SnackBar(f"Error: {str(e)}")
        page.update()

flet.app(target=main)
