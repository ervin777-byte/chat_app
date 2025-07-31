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

def login(page: Page, event):
    email = email_tf.value
    password = password_tf.value

    try:
        user = supabase.auth.sign_in_with_password(email=email, password=password)
        page.snack_bar = SnackBar(Text(f"Logged in as {user.user.email}"))
        page.snack_bar.open = True
        page.update()
        #page.navigation_stack = ["/chat"]
        page.go("/chat")
    except Exception as e:
        page.snack_bar = SnackBar(Text(str(e)))
        page.snack_bar.open = True
        page.update()

def signup(page: Page, event):
    email = email_tf.value
    password = password_tf.value

    try:
        user = supabase.auth.sign_up(email=email, password=password)
        page.snack_bar = SnackBar(Text(f"Signed up as {user.user.email}"))
        page.snack_bar.open = True
        page.update()
    except Exception as e:
        page.snack_bar = SnackBar(Text(str(e)))
        page.snack_bar.open = True
        page.update()

def main(page: Page):
    page.title = "Authentication zone"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    # --- Fix Starts Here ---

    # 1. Define UI elements and layout first
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
        # Center the column on the page
        horizontal_alignment=flet.CrossAxisAlignment.CENTER,
    )

    # 2. Define routing functions that USE the layout
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(
                flet.View(
                    "/",
                    [
                        flet.AppBar(title=flet.Text("Authentication Zone"), bgcolor=flet.Colors.ON_SURFACE_VARIANT),
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
                        flet.AppBar(title=flet.Text("Chat"), bgcolor=flet.Colors.ON_SURFACE_VARIANT),
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
        top_view = page.views[-1]
        page.go(top_view.route)

    # 3. Assign the routing functions to the page
    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # 4. Remove the page.add(column) call
    # The routing system now handles displaying the column.

    # 5. Go to the initial route to build the first view
    page.go(page.route)

flet.app(target=main)
