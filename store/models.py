from django.db import models
from core.models import Category
from django.urls import reverse

class Product(models.Model):
    product_name=models.CharField(max_length=200)
    slug=models.SlugField(max_length=200)
    descriptions=models.TextField(max_length=500 ,blank=True)
    product_image=models.ImageField(upload_to="mediafiles/product_image")
    price=models.IntegerField()
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    #size

    def get_url(self):
        return reverse("product_detail",args=[self.category.slug , self.slug])

    def __str__(self):
        return str(self.product_name)