from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Accounts, Profile


class AccountsAdmin(BaseUserAdmin):
    list_display = ["phone_number", "first_name", "last_name", "email", "date_joined", "last_login", "is_active", "is_staff", "is_superuser"]
    list_display_links = ["phone_number", "first_name", "last_name"]
    readonly_fields = ["date_joined", "last_login"]
    ordering = ("date_joined",)
    list_filter = ("is_active", "is_staff", "is_superuser")
    filter_horizontal = ()
    
    fieldsets = (
        (None, {'fields': ('phone_number', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'email', 'username')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone_number', 'password1', 'password2'),
        }),
    )

admin.site.register(Accounts, AccountsAdmin)
admin.site.register(Profile)