from django.shortcuts import render,get_object_or_404
from .models import Product
from core.models import Category
from carts.models import CartItem
from carts.views import _cart_id
from django.core.paginator import PageNotAnInteger,Paginator,EmptyPage
from django.db.models import Q
from django.http import HttpResponse

def store(request,category_slug=None):
    categories=None
    products=None
    #category_all = Category.objects.all()

    if category_slug != None:
        categories=get_object_or_404(Category,slug=category_slug)
        products = Product.objects.filter(category=categories,is_available=True)
        products_count = products.count()
        paginator = Paginator(products, 6)
        page = request.GET.get("page")
        page_product = paginator.get_page(page)
    else:
        products = Product.objects.all().filter(is_available=True).order_by('id')
        products_count=products.count()
        paginator=Paginator(products ,9)
        page=request.GET.get("page")
        page_product=paginator.get_page(page)

    context = {
        "products": page_product ,
        "products_count":products_count,
        }
    return render(request,"store.html", context)


def product_detail(request,category_slug,product_slug):
    try:
        product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=product).exists()
    except Exception as e:
        raise e

    context={
        "product":product,
        "in_cart":in_cart,
    }
    return render(request , "product-detail.html",context)

def search(request):
    if 'keyword' in request.GET:
        keyword=request.GET["keyword"]
        if keyword:
            products=Product.objects.order_by("-created_at").filter(Q(descriptions__icontains=keyword)|Q( product_name__icontains=keyword ) |Q( brand__icontains=keyword ))
            products_count = products.count()
        context={
            "products":products,
            "products_count":products_count,
        }

    return render(request,"store.html",context)