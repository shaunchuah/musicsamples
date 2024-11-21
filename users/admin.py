from django.contrib import admin
from django.contrib.auth import get_user_model

User = get_user_model()


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    def group(self, user):
        groups = []
        for group in user.groups.all():
            groups.append(group.name)
        return " ".join(groups)

    group.short_description = "Groups"

    list_display = [
        "email",
        "first_name",
        "last_name",
        "group",
        "is_staff",
        "is_active",
        "is_superuser",
        "last_login",
        "date_joined",
    ]
