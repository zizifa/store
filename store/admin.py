from django.contrib import admin
from .models import Product , Variation


@admin.register(Product)
class Productadmin(admin.ModelAdmin):
    list_display = ("product_name","category","stock","price","modified_date","is_available")
    prepopulated_fields = {"slug":("product_name",)}


"""@admin.register(Variation)
class Variationadmin(admin.ModelAdmin):
    list_display = ("product","variation_category","variation_value","is_active")
    list_editable = ("is_active",)
    list_filter = ("product","variation_category","variation_value","is_active")"""

