from django.contrib import admin
from .models import Accounts ,Profile
from django.contrib.auth.admin import UserAdmin
# Register your models here.


class Accountsadmin(UserAdmin):
    list_display = ["email","first_name","last_name","username","date_joined","last_login","is_active"]
    list_display_links = ["email","first_name","last_name"]
    readonly_fields = ["date_joined","last_login"]
    ordering = ("date_joined",)
    list_filter = ()
    filter_horizontal = ()
    fieldsets = ()

class Profileadmin(admin.ModelAdmin):
    list_display = ["user","city","state"]

admin.site.register(Accounts,Accountsadmin)
admin.site.register(Profile,Profileadmin)