from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username", "email", "full_name", "upi_id",
        "is_staff", "is_active", "created_at",
    )
    list_filter = BaseUserAdmin.list_filter + ("created_at",)
    search_fields = ("username", "email", "full_name", "upi_id")
    readonly_fields = ("created_at",)

    fieldsets = BaseUserAdmin.fieldsets + (
        ("SplitEase profile", {"fields": ("full_name", "avatar", "upi_id", "created_at")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("SplitEase profile", {"fields": ("full_name", "avatar", "upi_id")}),
    )