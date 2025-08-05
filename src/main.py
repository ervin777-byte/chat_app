import os
from dotenv import load_dotenv
import flet as ft
from supabase import create_client, Client

import auth
from home import home_view
from chat import chat_view

# --- Initialization (no changes) ---
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY")
if not url or not key:
    raise EnvironmentError("SUPABASE_URL and SUPABASE_KEY must be set in the .env file.")

supabase: Client = create_client(url, key)


# --- Main Application Logic ---
def main(page: ft.Page):
    page.title = "Authentication Zone"
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER

    # IMPROVED: This function now directly uses the 'route' passed to it.
    def route_change(e: ft.RouteChangeEvent):
        # If the user is navigating to the home page, clear the history.
        if e.route == "/":
            page.views.clear()
            page.views.append(home_view(page, supabase, auth.login, auth.signup))
        
        # If the user is navigating to the chat page...
        elif e.route == "/chat":
            user_id = page.session.get("user_id")
            if not user_id:
                # If not logged in, just redirect, don't change the view stack.
                page.go("/")
                return
            
            # Add the chat view on top of the home view.
            page.views.append(chat_view(page, supabase, user_id))
        
        page.update()

    # IMPROVED: Correct logic for popping a view.
    def view_pop(e: ft.ViewPopEvent):
        page.views.pop() # Remove the top view
        top_view = page.views[-1] # Get the new top view
        page.go(top_view.route) # Navigate to the new top view's route

    page.on_route_change = route_change
    page.on_view_pop = view_pop
    
    # This call triggers the initial page load 🚀
    page.go(page.route)

# It's good practice to run the app within a name==main block.
if __name__ == "__main__":
    ft.app(target=main)