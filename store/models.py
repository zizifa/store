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
        return self.product_name


class VariationManager(models.Manager):
    def colors(self):
        return super(VariationManager,self).filter(variation_category="color",is_active=True)
    def sizes(self):
        return super(VariationManager,self).filter(variation_category="size",is_active=True)


VARIATION_CATEGORY_CHOICES=(
        ("color",'color'),
        ("size",'size'),
    )

class Variation(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation_category=models.CharField(max_length=50,choices=VARIATION_CATEGORY_CHOICES)
    variation_value=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    objects=VariationManager()

    def __unicode__(self):
        return self.product