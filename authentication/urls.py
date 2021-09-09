from django.urls import path
from .views import login_view  # , register_user
from django.contrib.auth.views import LogoutView
from django.contrib.auth import views as auth_views

# sentry debug intentional error
# def trigger_error(request):
#    division_by_zero = 1/0

urlpatterns = [
    path("login/", login_view, name="login"),
    # path('register/', register_user, name="register"), Accounts are provisioned by the superuser through the django admin interface
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
    # path('sentry_debug/', trigger_error),
]
