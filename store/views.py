from django.shortcuts import render,get_object_or_404
from .models import Product
from core.models import Category

def store(request,category_slug=None):
    categories=None
    products=None
    #category_all = Category.objects.all()

    if category_slug != None:
        categories=get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=categories,is_available=True)
        products_count = products.count()
    else:
        products = Product.objects.all().filter(is_available=True)
        products_count=products.count()

    context = {
        "products": products ,
        "products_count":products_count,
        #"category_all":category_all
        }
    return render(request,"store.html", context)


def product_detail(request,category_slug,product_slug):
    try:
        product=Product.objects.get(category__slug=category_slug,slug=product_slug)
    except Exception as e:
        raise e

    context={
        "product":product
    }
    return render(request , "product-detail.html",context)