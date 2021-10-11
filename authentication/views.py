from django.contrib.auth import authenticate, login
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse
from rest_framework.authtoken.models import Token

# from django.contrib.auth.models import User
# from django.forms.utils import ErrorList
# from django.http import HttpResponse
from .forms import LoginForm  # , SignUpForm


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


def generate_token(request):
    Token.objects.get_or_create(user=request.user)
    return redirect(reverse("data_export"))


def delete_token(request):
    token = get_object_or_404(Token, user=request.user)
    token.delete()
    return redirect(reverse("data_export"))


def refresh_token(request):
    token = get_object_or_404(Token, user=request.user)
    token.delete()
    Token.objects.get_or_create(user=request.user)
    return redirect(reverse("data_export"))


# Public access to registration is disabled. Uncomment to re-enable -
# you will need to activate the registration url in authentication/urls.py
#
# def register_user(request):

#     msg     = None
#     success = False

#     if request.method == "POST":
#         form = SignUpForm(request.POST)
#         if form.is_valid():
#             form.save()
#             username = form.cleaned_data.get("username")
#             raw_password = form.cleaned_data.get("password1")
#             user = authenticate(username=username, password=raw_password)

#             msg     = 'User created.'
#             success = True

#             return redirect("/login/")

#         else:
#             msg = 'Form is not valid'
#     else:
#         form = SignUpForm()

#     return render(request,
#       "accounts/register.html",
#       {"form": form, "msg" : msg, "success" : success }
#     )
