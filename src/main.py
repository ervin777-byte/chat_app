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

    page.on_route_change = lambda e: route_change(e.route) # Simplified the async part

    def view_pop(e):
        page.go(page.views[-1].route)   

    page.on_view_pop = view_pop
    
    # This call triggers the initial page load 🚀
    page.go(page.route)

flet.app(target=main)
