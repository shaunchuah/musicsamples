from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path
from rest_framework.authtoken.views import obtain_auth_token

from authentication.views import (
    login_view,
    generate_token,
    delete_token,
    refresh_token,
)  # , register_user

urlpatterns = [
    path("login/", login_view, name="login"),
    # path('register/', register_user, name="register"),
    # Accounts are provisioned by the superuser through the django admin interface
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(
            template_name="accounts/password_reset_confirm.html"
        ),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            subject_template_name="accounts/password_reset_subject.txt",
            email_template_name="accounts/password_reset_email.html",
        ),
        name="password_reset",
    ),
    path(
        "password_change/",
        auth_views.PasswordChangeView.as_view(
            template_name="accounts/password_change.html"
        ),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(
            template_name="accounts/password_change_done.html"
        ),
        name="password_change_done",
    ),
    path("get_api_token/", obtain_auth_token, name="obtain_auth_token"),
    path("generate_token/", generate_token, name="generate_token"),
    path("delete_token/", delete_token, name="delete_token"),
    path("refresh_token/", refresh_token, name="refresh_token")
]
