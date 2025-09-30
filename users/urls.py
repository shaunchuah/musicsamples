from django.contrib.auth import views as auth_views
from django.contrib.auth.views import LogoutView
from django.urls import path
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView

from users.views import (
    PasswordChangeView,
    account,
    activate_account_view,
    deactivate_account_view,
    delete_token,
    edit_profile_view,
    edit_user_view,
    generate_token,
    login_view,
    make_staff_view,
    management,
    new_user_view,
    refresh_token,
    remove_staff_view,
    user_list_view,
)

urlpatterns = [
    path("login/", login_view, name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path(
        "password_reset/done/",
        auth_views.PasswordResetDoneView.as_view(template_name="accounts/password_reset_done.html"),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        auth_views.PasswordResetConfirmView.as_view(template_name="accounts/password_reset_confirm.html"),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(template_name="accounts/password_reset_complete.html"),
        name="password_reset_complete",
    ),
    path(
        "password_reset/",
        auth_views.PasswordResetView.as_view(
            template_name="accounts/password_reset.html",
            subject_template_name="accounts/password_reset_subject.txt",
            email_template_name="emails/password_reset_email.txt",
            html_email_template_name="emails/password_reset_email.html",
        ),
        name="password_reset",
    ),
    path(
        "password_change/",
        PasswordChangeView.as_view(template_name="accounts/password_change.html"),
        name="password_change",
    ),
    path(
        "password_change/done/",
        auth_views.PasswordChangeDoneView.as_view(template_name="accounts/password_change_done.html"),
        name="password_change_done",
    ),
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    path("generate_token/", generate_token, name="generate_token"),
    path("delete_token/", delete_token, name="delete_token"),
    path("refresh_token/", refresh_token, name="refresh_token"),
    path("new_user/", new_user_view, name="new_user"),
    path("users/", user_list_view, name="user_list"),
    path("make_staff/<int:user_id>/", make_staff_view, name="make_staff"),
    path("remove_staff/<int:user_id>/", remove_staff_view, name="remove_staff"),
    path("activate/<int:user_id>/", activate_account_view, name="activate_account"),
    path("deactivate/<int:user_id>/", deactivate_account_view, name="deactivate_account"),
    path("edit_user/<int:user_id>/", edit_user_view, name="edit_user"),
    path("edit_profile/", edit_profile_view, name="edit_profile"),
    path("account/", account, name="account"),
    path("management/", management, name="management"),
]
