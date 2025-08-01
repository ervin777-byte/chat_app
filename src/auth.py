from flet import Text, SnackBar, Colors

def login(page, event, email_tf, password_tf, supabase):
    email = email_tf.value
    password = password_tf.value

    try:
        user_session = supabase.auth.sign_in_with_password({"email": email, "password": password})
        print(f"Logged in as {user_session.user.email}")
        page.open(SnackBar(Text(f"Logged in as {user_session.user.email}"), bgcolor=Colors.RED))
        page.update()
        page.go("/chat")
    except Exception as e:
        print(str(e))
        page.open(SnackBar(Text(str(e)), bgcolor=Colors.RED))
        page.update()

def signup(page, event, email_tf, password_tf, supabase):
    email = email_tf.value
    password = password_tf.value

    try:
        user = supabase.auth.sign_up({"email": email,"password": password,})
        if user.user:
            message = f"Signed up as {user.user.email}. Please confirm your email address."
        else:
            message = "Sign up failed. No user returned."

        print(message)
        page.open(SnackBar(Text(message), bgcolor=Colors.RED))
        page.update()
    except Exception as e:
        print(f"Error: {str(e)}")
        page.open(SnackBar(Text(f"Error: {str(e)}"), bgcolor=Colors.RED))
        page.update()