from django.contrib.auth import update_session_auth_hash
from django.contrib.auth.forms import SetPasswordForm
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenBlacklistView, TokenObtainPairView, TokenRefreshView


@extend_schema(tags=["v3"])
class V3TokenObtainPairView(TokenObtainPairView):
    pass


@extend_schema(tags=["v3"])
class V3TokenRefreshView(TokenRefreshView):
    pass


@extend_schema(tags=["v3"])
class V3TokenBlacklistView(TokenBlacklistView):
    pass


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
