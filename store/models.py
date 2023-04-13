from django.db import models
from core.models import Category
from django.urls import reverse
from accounts.models import Accounts
from django.db.models import Avg ,Count

class Product(models.Model):
    product_name=models.CharField(max_length=200, unique=True)
    slug=models.SlugField(max_length=200, unique=True)
    descriptions=models.TextField(max_length=500 ,blank=True)
    product_image=models.ImageField(upload_to="mediafiles/product_image")
    brand=models.CharField(max_length=100, blank=True)
    price=models.IntegerField()
    stock=models.IntegerField()
    is_available=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)
    modified_date=models.DateTimeField(auto_now=True)
    category=models.ForeignKey(Category,on_delete=models.CASCADE)
    #size

    def get_url(self):
        return reverse("product_detail",args=[self.category.slug , self.slug])

    def average(self):
        reviews=ReviewRating.objects.filter(product=self,status=True).aggregate(average=Avg('rating'))
        avg=0
        if reviews['average'] is not None:
            avg=float(reviews['average'])
        return avg

    def countReview(self):
        reviews=ReviewRating.objects.filter(product=self,status=True).aggregate(count=Count('id'))
        count=0
        if reviews['count'] is not None:
            count=int(reviews['count'])
        return count

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
    product=models.ForeignKey(Product,on_delete=models.CASCADE )
    variation_category=models.CharField(max_length=50,choices=VARIATION_CATEGORY_CHOICES)
    variation_value=models.CharField(max_length=100)
    is_active=models.BooleanField(default=True)
    created_at=models.DateTimeField(auto_now_add=True)

    objects=VariationManager()

    def __unicode__(self):
        return self.product


class ReviewRating(models.Model):
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    user=models.ForeignKey(Accounts,on_delete=models.CASCADE)
    subject=models.CharField(max_length=100,blank=True)
    review=models.TextField(max_length=500,blank=True)
    rating=models.FloatField()
    ip=models.CharField(max_length=20,blank=True)
    status=models.BooleanField(default=True)
    crated_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.subject

