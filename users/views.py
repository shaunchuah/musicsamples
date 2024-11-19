from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth import authenticate, get_user_model, login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from rest_framework.authtoken.models import Token

from users.forms import LoginForm, NewUserForm
from users.utils import generate_random_password, send_welcome_email

User = get_user_model()


def login_view(request):
    form = LoginForm(request.POST or None)

    msg = None

    if request.method == "POST":
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/")
            else:
                msg = "Invalid credentials"
        else:
            msg = "Error validating the form"

    return render(request, "accounts/login.html", {"form": form, "msg": msg})


@login_required
def generate_token(request):
    Token.objects.get_or_create(user=request.user)
    return redirect(reverse("data_export"))


@login_required
def delete_token(request):
    token = get_object_or_404(Token, user=request.user)
    token.delete()
    return redirect(reverse("data_export"))


@login_required
def refresh_token(request):
    token = get_object_or_404(Token, user=request.user)
    token.delete()
    Token.objects.get_or_create(user=request.user)
    return redirect(reverse("data_export"))


@staff_member_required
def new_user_view(request):
    if request.method == "POST":
        form = NewUserForm(request.POST)
        if form.is_valid():
            try:
                form.save(commit=False)
                first_name = form.cleaned_data.get("first_name")
                last_name = form.cleaned_data.get("last_name")
                username = form.cleaned_data.get("username")
                email = form.cleaned_data.get("email")
                password = generate_random_password()
                user = User.objects.create_user(
                    username=username, email=email, password=password, first_name=first_name, last_name=last_name
                )
                user.save()

                send_welcome_email(user, request)

                messages.success(request, "User registered successfully. An email has been sent to the user.")

                return redirect(reverse("user_list"))
            except IntegrityError:
                messages.error(request, "This email has already been registered.")

        else:
            messages.error(request, "Form is not valid.")
    else:
        form = NewUserForm()

    context = {"form": form}

    return render(request, "accounts/new_user.html", context)


@staff_member_required
def edit_user_view(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if user.is_superuser:
        messages.error(request, "You cannot edit a superuser.")
        return redirect(reverse("user_list"))

    if request.method == "POST":
        form = NewUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, f"{user.email} has been updated successfully.")
            return redirect(reverse("user_list"))
        else:
            messages.error(request, "Form is not valid.")
    else:
        form = NewUserForm(instance=user)

    context = {"form": form, "user": user}
    return render(request, "accounts/edit_user.html", context)


@login_required
def edit_profile_view(request):
    user = request.user

    if request.method == "POST":
        form = NewUserForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect(reverse("account"))
        else:
            messages.error(request, "Form is not valid.")
    else:
        form = NewUserForm(instance=user)

    context = {"form": form, "user": user}
    return render(request, "accounts/edit_user.html", context)


@staff_member_required
def user_list_view(request):
    users = User.objects.filter(is_superuser=False).order_by("email")
    context = {"users": users}
    return render(request, "accounts/user_list.html", context)


@staff_member_required
def make_staff_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_staff = True
    user.save()
    messages.success(request, f"{user.email} has been granted staff status.")
    return redirect(reverse("user_list"))


@staff_member_required
def remove_staff_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "You cannot remove your own staff status.")
    elif user.is_superuser:
        messages.error(request, "You cannot remove staff status from a superuser.")
    else:
        user.is_staff = False
        user.save()
        messages.success(request, f"{user.email} has been removed from staff status.")
    return redirect(reverse("user_list"))


@staff_member_required
def activate_account_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    user.is_active = True
    user.save()
    messages.success(request, f"{user.email} has been activated.")
    return redirect(reverse("user_list"))


@staff_member_required
def deactivate_account_view(request, user_id):
    user = get_object_or_404(User, id=user_id)
    if user == request.user:
        messages.error(request, "You cannot deactivate your own account.")
    elif user.is_superuser:
        messages.error(request, "You cannot deactivate a superuser account.")
    else:
        user.is_active = False
        user.save()
        messages.success(request, f"{user.email} has been deactivated.")
    return redirect(reverse("user_list"))
