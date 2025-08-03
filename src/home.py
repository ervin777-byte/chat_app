import flet as ft

from auth import login, signup

def home_view(page: ft.Page, supabase, login_func, signup_func):
    email = ft.TextField(label="Email", width=300)
    password = ft.TextField(label="Password", width=300, password=True, can_reveal_password=True)
    login_btn = ft.ElevatedButton(text="Login")
    signup_btn = ft.ElevatedButton(text="Sign Up")
    message = ft.Text("")

    def on_login_click(e):
        if not email.value or not password.value:
            message.value = "Please fill in both fields"
            page.update()
            return
        login_func(page, e, email, password, supabase)


    def on_signup_click(e):
        if not email.value or not password.value:
            message.value = "Please fill in both fields"
            page.update()
            return
        signup_func(page, e, email, password)


    login_btn.on_click = on_login_click
    signup_btn.on_click = on_signup_click

    return ft.View(
        "/",
        [
            ft.Column(
                [
                    ft.Text("Welcome! Please log in or sign up", size=20),
                    email,
                    password,
                    ft.Row([login_btn, signup_btn], spacing=20),
                    message,
                ],
                alignment=ft.MainAxisAlignment.CENTER,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                expand=True,
            )
        ],
    )
