from django.contrib import admin
from . models import Category
# Register your models here.

class Categoryadmin(admin.ModelAdmin):
    prepopulated_fields = {"slug":("category_name",)}
admin.site.register(Category,Categoryadmin)