from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name", "email", "date_of_birth", "bio", "profile_picture")}),
        (_("Permissions"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        (_("Verification"), {"fields": ("is_email_verified",)}),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("username", "email", "password1", "password2"),
        }),
    )
    list_display = ("username", "email", "first_name", "last_name", "is_staff", "is_email_verified")
    list_filter = ("is_staff", "is_superuser", "is_active", "is_email_verified", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)
