from django.contrib import admin

from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm
from django.utils.translation import gettext_lazy as _

from authentication.forms import CustomUserCreationForm
from authentication.models import Token


class CustomUserChangeForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = get_user_model()


class CustomUserAdmin(UserAdmin):
    fieldsets = (
        (None, {"fields": ("email", "phone_number", "password")}),
        (_("Personal info"), {"fields": ("first_name", "last_name")}),
        (
            _("Contact Verification"),
            {"fields": ("phone_number_verified_on", "email_verified_on")},
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (_("Important dates"), {"fields": ("last_login",)}),
    )
    filter_horizontal = ("groups", "user_permissions")

    list_display = (
        "name",
        "email",
        "phone_number__prettified",
        "email_verified",
        "phone_number_verified",
        "auth0_user_id",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    ordering = ("date_joined", "is_staff", "is_superuser")
    search_fields = ("phone_number", "first_name", "last_name", "email")

    form = CustomUserChangeForm

    add_form = CustomUserCreationForm
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "phone_number", "password1", "password2"),
            },
        ),
    )


class TokenAdmin(admin.ModelAdmin):
    list_display = ("token", "user", "user_agent", "created_on", "updated_on")
    readonly_fields = ("token", "ip_address_hash", "user_agent")
    exclude = ("key",)
    ordering = ("-created_on", "-updated_on")


admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(Token, TokenAdmin)
