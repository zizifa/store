from django.db import models

# Create your models here.

class Category(models.Model):
    category_name=models.CharField(max_length =100)
    slug = models.SlugField(max_length =50 , unique=True)
    descriptions=models.TextField(max_length=100 , blank=True)
    category_image=models.ImageField(upload_to="category_image")

    class Meta:
        verbose_name='category'
        verbose_name_plural="categories"

    def __str__(self):
        return self.category_name
