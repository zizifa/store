from django.shortcuts import render
from store.models import Product
from store.models import Category
from django.http import HttpResponse
# Create your views here.

def index(request):
    products = Product.objects.all().filter(is_available=True)
    products_count = products.count()
    context={
        "products": products,
        "products_count":products_count,
    }
    return render(request,'index.html',context)