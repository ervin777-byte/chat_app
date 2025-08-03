import asyncio
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
if not url or not key:
    raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set in the .env file.")

supabase: Client = create_client(url, key)

def main(page: Page):
    page.title = "Authentication zone"
    page.vertical_alignment = "center"
    page.horizontal_alignment = "center"

    def route_change(route):
        user_email = page.session.get("user_email")

        page.views.clear()

        if page.route == "/":
            page.views.append(home_view(page, supabase, auth.login, auth.signup))
        elif page.route == "/chat":
            if not user_email:
                page.go("/")
                return
            page.views.append(chat_view(page, supabase, user_email))

        page.update()


    # Pass the 'route' attribute from the event object
    page.on_route_change = lambda e: asyncio.create_task(route_change(e.route))

    def view_pop(e): # The handler receives an event argument
        # The view has already been popped by Flet, so we just navigate
        page.go(page.views[-1].route)   

    page.on_view_pop = view_pop

    # Defer navigation to after frontend is ready
    async def on_connect(e):
        # This now correctly handles the very first page load.
        # Subsequent navigation is handled by on_route_change.
        route_change(page.route)

    # The handler for on_connect receives the event object `e`
    page.on_connect = on_connect

flet.app(target=main, view=flet.WEB_BROWSER)
