from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Kyc

admin.site.register(Kyc)


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ["username", "email", "get_full_name", "balance", "date_joined"]
    fieldsets = UserAdmin.fieldsets + (
        (
            "Profile",
            {
                "fields": (
                    "phone_number",
                    "country",
                    "date_of_birth",
                    "bio",
                    "profile_picture",
                )
            },
        ),
    )
