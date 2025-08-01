import os
from dotenv import load_dotenv
import flet
from flet import Page
from supabase import create_client, Client

import auth
from home import home_view
from chat import chat_view

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

url: str = os.getenv("SUPABASE_URL")
key: str = os.getenv("SUPABASE_KEY")
supabase: Client = create_client(url, key)

def main(page: Page):
    page.title = "Authentication zone"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    # Route change handler
    def route_change(route):
        page.views.clear()
        if page.route == "/":
            page.views.append(home_view(page, supabase, auth.login, auth.signup))
        elif page.route == "/chat":
            page.views.append(chat_view(page))
        page.update()

    # View pop handler
    def view_pop(view):
        page.views.pop()
        top_view = page.views[-1]
        page.go(top_view.route)

    page.on_route_change = route_change
    page.on_view_pop = view_pop

    page.go(page.route)

flet.app(target=main, view=flet.WEB_BROWSER)
