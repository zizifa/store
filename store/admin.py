from django.contrib import admin
from .models import Product

class Productadmin(admin.ModelAdmin):
    list_display = ("product_name","category","stock","price","modified_date","is_available")
    prepopulated_fields = {"slug":("product_name",)}

admin.site.register(Product,Productadmin)