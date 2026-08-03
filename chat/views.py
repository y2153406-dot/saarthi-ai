from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth import logout

from .models import Conversation, Message
from .services.services import get_gemini_response

def home_view(request):
    return render(request, "home.html")
def signup_view(request):
    if request.method == "GET":
        return render(request, "signup.html")

    username = request.POST.get("username", "").strip()
    email = request.POST.get("email", "").strip()
    password = request.POST.get("password", "").strip()
    confirm_password = request.POST.get("confirm_password", "").strip()

    context = {
        "username": username,
        "email": email,
    }

    if not username or not email or not password or not confirm_password:
        messages.error(request, "All fields are required.")
        return render(request, "signup.html", context)

    if password != confirm_password:
        messages.error(request, "Password mismatch. Try again.")
        return render(request, "signup.html", context)

    if User.objects.filter(username=username).exists():
        messages.error(request, "Username already exists.")
        return render(request, "signup.html", context)

    User.objects.create_user(
        username=username,
        email=email,
        password=password,
    )

    return redirect("login")

def login_view(request):
    if request.method=="GET":
        return render(request, "login.html")
    if request.method=="POST":
        username=request.POST.get("username", "").strip()
        password=request.POST.get("password", "").strip()
        #Basic validation:
        if not username or not password:
            messages.error(request, "All fields are required.")
            return render(request, "login.html")
        #Authentication
        user=authenticate(request, username=username, password=password)
        #Authentication check
        if user is not None: 
            #login session
            login(request, user)
            return redirect("chat")
        else:
            messages.error(request, "Invalid username or password.")
            return render(request, "login.html")


@login_required
def chat_view(request):
    # Sidebar conversations
    conversations = (
        Conversation.objects
        .filter(user=request.user)
        .order_by("-updated_at")
    )

    selected_conversation = None
    chat_messages = Message.objects.none()

    # ---------------- GET ---------------- #
    if request.method == "GET":

        conversation_id = request.GET.get("conversation_id")

        if conversation_id:
            selected_conversation = get_object_or_404(
                Conversation,
                id=conversation_id,
                user=request.user
            )

            chat_messages = (
                Message.objects
                .filter(conversation=selected_conversation)
                .order_by("created_at")
            )

        context = {
            "conversations": conversations,
            "selected_conversation": selected_conversation,
            "messages": chat_messages,
        }

        return render(request, "chat.html", context)

    # ---------------- POST ---------------- #
    if request.method == "POST":

        message = request.POST.get("message", "").strip()
        conversation_id = request.POST.get("conversation_id")

        # Validation
        if not message:
            messages.error(request, "Message should not be empty.")
            return redirect("chat")

        # Existing Conversation
        if conversation_id:

            conversation = get_object_or_404(
                Conversation,
                id=conversation_id,
                user=request.user
            )

        # New Conversation
        else:

            conversation = Conversation.objects.create(
                user=request.user,
                title=message[:30]
            )

        # Save User Message
        Message.objects.create(
            conversation=conversation,
            role=Message.Role.USER,
            content=message
        )

        # Gemini API
        ai_response = get_gemini_response(message)

        # Save AI Message
        Message.objects.create(
            conversation=conversation,
            role=Message.Role.AI,
            content=ai_response
        )

        # Update conversation timestamp
        conversation.save()

        return redirect(
            f"/chat/?conversation_id={conversation.id}"
        )
@login_required
def logout_view(request):
    if request.method == "POST":
        logout(request)
        messages.success(request, "You have been logged out successfully.")
        return redirect("login")

    return redirect("chat")