import flet
from flet import Column, Row, TextField, ElevatedButton, View, AppBar, Text, SnackBar

def home_view(page, supabase, login_fn, signup_fn):
    email_tf = TextField(label="Email", width=300)
    password_tf = TextField(label="Password", password=True, width=300)

    login_btn = ElevatedButton("Login", on_click=lambda e: login_fn(page, e, email_tf, password_tf, supabase))
    signup_btn = ElevatedButton("Sign Up", on_click=lambda e: signup_fn(page, e, email_tf, password_tf, supabase))

    column = Column(
        controls=[
            email_tf,
            password_tf,
            Row([login_btn, signup_btn], alignment="spaceBetween"),
        ],
        spacing=20,
        horizontal_alignment=flet.CrossAxisAlignment.CENTER,
    )

    return View(
        "/",
        [
            AppBar(title=Text("Authentication Zone"), bgcolor=flet.Colors.RED),
            column
        ],
        vertical_alignment=flet.CrossAxisAlignment.CENTER,
        horizontal_alignment=flet.CrossAxisAlignment.CENTER,
    )