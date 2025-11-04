# users/api_views.py
# Provides DRF endpoints for user-facing identity data consumed by the dashboard.
# Exists so the frontend can fetch current user profile and access metadata directly from Django.

from django.contrib.auth import get_user_model
from rest_framework import serializers
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView


User = get_user_model()


class CurrentUserSerializer(serializers.ModelSerializer):
    groups = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ("email", "first_name", "last_name", "is_staff", "is_superuser", "groups")

    def get_groups(self, obj):
        return list(obj.groups.values_list("name", flat=True))


class CurrentUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = CurrentUserSerializer(request.user)
        return Response(serializer.data)
