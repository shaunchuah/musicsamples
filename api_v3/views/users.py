# api_v3/views/users.py
# Provides v3 user/account API endpoints for profile, passwords, staff management, tokens, and activity feeds.
# Exists to mirror legacy template-based user flows in an API form for the Next.js frontend.

from django.conf import settings
from django.contrib.auth import get_user_model, update_session_auth_hash
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.db import IntegrityError
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.authtoken.models import Token
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import AllowAny, IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
from rest_framework.views import APIView

from api_v3.serializers import SampleV3Serializer
from app.models import Sample
from users.utils import generate_random_password, send_welcome_email

User = get_user_model()


class CurrentUserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "is_staff", "is_superuser", "groups")

    def get_groups(self, obj) -> list[str]:
        return list(obj.groups.values_list("name", flat=True))


class CurrentUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "job_title", "primary_organisation")
        extra_kwargs = {"email": {"required": False}}


@extend_schema(tags=["v3"])
class CurrentUserView(APIView):
    """
    Return or update the authenticated user's profile details.
    """

    serializer_class = CurrentUserSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(request=CurrentUserUpdateSerializer, responses=CurrentUserSerializer)
    def patch(self, request):
        serializer = CurrentUserUpdateSerializer(request.user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(CurrentUserSerializer(serializer.instance).data)


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetRequestView(APIView):
    """
    Begin the password reset flow by sending a reset email.
    """

    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    @extend_schema(tags=["v3"], description="Send password reset email for the supplied address.")
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        if not serializer.is_valid():
            email_errors = serializer.errors.get("email")
            if email_errors:
                return Response({"error": email_errors[0]}, status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        form = PasswordResetForm({"email": serializer.validated_data["email"]})
        if not form.is_valid():
            return Response({"error": "Enter a valid email address."}, status=status.HTTP_400_BAD_REQUEST)

        frontend_base_url = getattr(settings, "FRONTEND_BASE_URL", "").rstrip("/")
        extra_email_context = {"frontend_base_url": frontend_base_url} if frontend_base_url else None

        form.save(
            request=request,
            use_https=request.is_secure(),
            subject_template_name="accounts/password_reset_subject.txt",
            email_template_name="emails/password_reset_email.txt",
            html_email_template_name="emails/password_reset_email.html",
            extra_email_context=extra_email_context,
        )

        return Response({"success": True})


class PasswordResetConfirmSerializer(serializers.Serializer):
    uid = serializers.CharField()
    token = serializers.CharField()
    new_password = serializers.CharField()


class PasswordResetConfirmView(APIView):
    """
    Complete the password reset flow using uid/token and a new password.
    """

    permission_classes = [AllowAny]
    throttle_classes = [UserRateThrottle, AnonRateThrottle]

    @extend_schema(tags=["v3"], description="Confirm password reset with uid/token and set a new password.")
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        uidb64 = serializer.validated_data["uid"]
        token = serializer.validated_data["token"]
        new_password = serializer.validated_data["new_password"]

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User._default_manager.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({"error": "Reset link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)

        if not default_token_generator.check_token(user, token):
            return Response({"error": "Reset link is invalid or has expired."}, status=status.HTTP_400_BAD_REQUEST)

        form = SetPasswordForm(user, data={"new_password1": new_password, "new_password2": new_password})
        if form.is_valid():
            form.save()
            return Response({"success": True})

        errors = []
        for field_errors in form.errors.values():
            errors.extend(field_errors)
        return Response(
            {"error": errors[0] if errors else "Unable to reset password."},
            status=status.HTTP_400_BAD_REQUEST,
        )


class PasswordChangeSerializer(serializers.Serializer):
    new_password = serializers.CharField()


class PasswordChangeView(APIView):
    """
    Change password for the authenticated user and preserve session.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(tags=["v3"])
    def post(self, request):
        serializer = PasswordChangeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        form = SetPasswordForm(
            request.user,
            data={
                "new_password1": serializer.validated_data["new_password"],
                "new_password2": serializer.validated_data["new_password"],
            },
        )
        if form.is_valid():
            form.save()
            update_session_auth_hash(request, form.user)
            return Response({"success": True})

        errors = []
        for field_errors in form.errors.values():
            errors.extend(field_errors)
        return Response(
            {"error": errors[0] if errors else "Unable to change password."}, status=status.HTTP_400_BAD_REQUEST
        )


class StaffUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "id",
            "email",
            "first_name",
            "last_name",
            "job_title",
            "primary_organisation",
            "is_staff",
            "is_active",
        )
        read_only_fields = ("id", "is_staff", "is_active")


class StaffUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "job_title", "primary_organisation")
        extra_kwargs = {"email": {"required": False}}


@extend_schema(tags=["v3"])
class StaffUserViewSet(
    mixins.ListModelMixin, mixins.CreateModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    """
    Staff-only management for non-superusers: list, create, edit, and toggle staff/active flags.
    """

    queryset = User.objects.filter(is_superuser=False).order_by("-is_active", "-last_login")
    permission_classes = [IsAuthenticated, IsAdminUser]

    def get_serializer_class(self):
        if self.action in ("partial_update", "update"):
            return StaffUserUpdateSerializer
        if self.action == "create":
            return StaffUserUpdateSerializer
        return StaffUserSerializer

    def perform_create(self, serializer):
        random_password = generate_random_password()
        try:
            user = User.objects.create_user(password=random_password, **serializer.validated_data)  # type: ignore
        except IntegrityError:
            raise serializers.ValidationError({"email": "This email has already been registered."})

        send_welcome_email(user, self.request)

    def partial_update(self, request, *args, **kwargs):
        user = self.get_object()
        if user.is_superuser:
            return Response({"error": "You cannot edit a superuser."}, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(StaffUserSerializer(user).data)

    @extend_schema(
        description="Grant staff status to a user (superusers cannot be edited).",
        request=None,
        responses=StaffUserSerializer,
    )
    @action(detail=True, methods=["post"])
    def make_staff(self, request, pk=None):
        user = self.get_object()
        if user.is_superuser:
            return Response({"error": "You cannot edit a superuser."}, status=status.HTTP_403_FORBIDDEN)
        user.is_staff = True
        user.save()
        return Response({"success": True, "message": f"{user.email} has been granted staff status."})

    @extend_schema(
        description="Remove staff status; blocked for self and superusers.",
        request=None,
        responses=StaffUserSerializer,
    )
    @action(detail=True, methods=["post"])
    def remove_staff(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            return Response({"error": "You cannot remove your own staff status."}, status=status.HTTP_400_BAD_REQUEST)
        if user.is_superuser:
            return Response({"error": "You cannot edit a superuser."}, status=status.HTTP_403_FORBIDDEN)
        user.is_staff = False
        user.save()
        return Response({"success": True, "message": f"{user.email} has been removed from staff status."})

    @extend_schema(
        description="Activate a user; superusers are not editable here.", request=None, responses=StaffUserSerializer
    )
    @action(detail=True, methods=["post"])
    def activate(self, request, pk=None):
        user = self.get_object()
        if user.is_superuser:
            return Response({"error": "You cannot edit a superuser."}, status=status.HTTP_403_FORBIDDEN)
        user.is_active = True
        user.save()
        return Response({"success": True, "message": f"{user.email} has been activated."})

    @extend_schema(
        description="Deactivate a user; blocked for self and superusers.", request=None, responses=StaffUserSerializer
    )
    @action(detail=True, methods=["post"])
    def deactivate(self, request, pk=None):
        user = self.get_object()
        if user == request.user:
            return Response({"error": "You cannot deactivate your own account."}, status=status.HTTP_400_BAD_REQUEST)
        if user.is_superuser:
            return Response({"error": "You cannot edit a superuser."}, status=status.HTTP_403_FORBIDDEN)
        user.is_active = False
        user.save()
        return Response({"success": True, "message": f"{user.email} has been deactivated."})


class TokenResponseSerializer(serializers.Serializer):
    token = serializers.CharField()


class SuccessResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()


class CurrentUserTokenViewSet(viewsets.ViewSet):
    """
    Manage DRF auth tokens for the current user (create, delete, refresh).
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["v3"],
        description="Create a DRF token for the current user (idempotent).",
        request=None,
        responses=TokenResponseSerializer,
    )
    def create(self, request):
        token, _ = Token.objects.get_or_create(user=request.user)
        return Response({"token": token.key})

    @extend_schema(
        tags=["v3"],
        description="Delete the current user's DRF token, if it exists.",
        request=None,
        responses=SuccessResponseSerializer,
    )
    def destroy(self, request, pk=None):  # pk unused; required by ViewSet signature
        token = Token.objects.filter(user=request.user).first()
        if token:
            token.delete()
        return Response({"success": True})

    @extend_schema(
        tags=["v3"],
        description="Refresh (delete and recreate) the current user's DRF token.",
        request=None,
        responses=TokenResponseSerializer,
    )
    @action(detail=False, methods=["post"])
    def refresh(self, request):
        token = Token.objects.filter(user=request.user).first()
        if token:
            token.delete()
        new_token, _ = Token.objects.get_or_create(user=request.user)
        return Response({"token": new_token.key})


class CurrentUserRecentSamplesView(APIView):
    """
    Return the current user's recently modified samples with limit/offset pagination (default 20).
    """

    permission_classes = [IsAuthenticated]
    pagination_class = LimitOffsetPagination

    @extend_schema(tags=["v3"], description="List recent samples modified by the current user (paginated).")
    def get(self, request):
        paginator = self.pagination_class()
        paginator.default_limit = 20
        queryset = (
            Sample.objects.filter(last_modified_by=request.user.email)
            .select_related("study_id")
            .order_by("-last_modified")
        )
        page = paginator.paginate_queryset(queryset, request, view=self)
        data = SampleV3Serializer(page, many=True).data
        return paginator.get_paginated_response(data)


class ManagementUserEmailsView(APIView):
    """
    Staff-only utility endpoint returning all user emails.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(tags=["v3"], description="Staff-only listing of all user emails (list and semicolon string).")
    def get(self, request):
        emails = list(User.objects.values_list("email", flat=True))
        return Response({"emails": emails, "emails_joined": ";".join(emails)})
