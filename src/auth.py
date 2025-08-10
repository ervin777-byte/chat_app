import asyncio
from flet import Text, SnackBar, Colors

from flet import SnackBar, Text, Colors

def login(page, event, email_tf, password_tf, supabase):
    email = email_tf.value.strip()
    password = password_tf.value.strip()

    if not email or not password:
        page.open(SnackBar(Text("Email and password required", bgcolor=Colors.RED)))
        page.update()
        return

    try:
        response = supabase.auth.sign_in_with_password({"email": email, "password": password})
        user = response.user
        if response.user is not None:
            # ✅ Store email using page.session (synchronous)
            page.session.set("user_email", response.user.email)
            page.session.set("user_id", user.id)
            page.open(SnackBar(Text(f"Logged in as {response.user.email}", bgcolor=Colors.GREEN)))
            page.update()
            page.go("/chat")
        else:
            page.open(SnackBar(Text("Login failed: Invalid credentials", bgcolor=Colors.RED)))
            page.update()
    except Exception as e:
        page.open(SnackBar(Text(f"Error: {str(e)}", bgcolor=Colors.RED)))
        page.update()

def signup(page, event, email_tf, password_tf, supabase):
    email = email_tf.value.strip()
    password = password_tf.value.strip()

    if not email or not password:
        page.open(SnackBar(Text("Email and password required", bgcolor=Colors.RED)))
        page.update()
        return

    try:
        user = supabase.auth.sign_up({"email": email, "password": password})
        if user.user:
            message = f"Signed up as {user.user.email}. Please confirm your email address."

            # ✅ Use page.session for synchronous session storage
            page.session.set("user_email", user.user.email)

            page.open(SnackBar(Text(message, bgcolor=Colors.GREEN)))
            page.update()

            # ✅ Optionally redirect after signup
            page.go("/chat")
        else:
            message = "Sign up failed. No user returned."
            page.open(SnackBar(Text(message, bgcolor=Colors.RED)))
            page.update()
    except Exception as e:
        page.open(SnackBar(Text(f"Error: {str(e)}", bgcolor=Colors.RED)))
        page.update()
