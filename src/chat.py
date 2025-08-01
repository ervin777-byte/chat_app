
import flet
from flet import View, AppBar, Text, ElevatedButton

def chat_view(page):
    return View(
        "/chat",
        [
            AppBar(title=Text("Chat"), bgcolor=flet.Colors.PURPLE),
            Text("Welcome to the chat page!"),
            ElevatedButton("Go back to Home", on_click=lambda e: page.go("/"))
        ],
        vertical_alignment=flet.CrossAxisAlignment.CENTER,
        horizontal_alignment=flet.CrossAxisAlignment.CENTER,
    )