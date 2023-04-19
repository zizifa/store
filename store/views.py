from django.shortcuts import render,get_object_or_404,redirect
from .models import Product,ReviewRating,ProductGallery,Variation
from core.models import Category
from carts.models import CartItem
from .forms import ReviewForm
from carts.views import _cart_id
from django.core.paginator import PageNotAnInteger,Paginator,EmptyPage
from django.db.models import Q
from django.contrib import messages
from order.models import OrderProduct
from django.db.models import Avg
from django.http import HttpResponse


def store(request,category_slug=None):
    categories=None
    products=None
    category_all = Category.objects.all()



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

    """size_list=[34,36,38,40,42,44]
    for i in size_list:
        filterr=Variation.objects.filter(variation_value = i)
        if filterr:
            print(filterr)

    for i in size_list:
        i = Variation.objects.filter(variation_value = i)"""



    context = {
        "products": page_product ,
        "products_count":products_count,
        'category_all':category_all,
        }
    return render(request,"store.html", context)


def product_detail(request,category_slug,product_slug):
    try:
        product=Product.objects.get(category__slug=category_slug,slug=product_slug)
        in_cart=CartItem.objects.filter(cart__cart_id=_cart_id(request),product=product).exists()
    except Exception as e:
        raise e
    if request.user.is_authenticated:
        try:
            orderproduct = OrderProduct.objects.filter(user=request.user, product_id=product.id).exists()
        except OrderProduct.DoesNotExist:
            orderproduct = None
    else:
        orderproduct = None

        # Get the reviews
    reviews = ReviewRating.objects.filter(product_id=product.id, status=True)

    product_gallery=ProductGallery.objects.filter(product_id=product.id)

    context={
        "product":product,
        "in_cart":in_cart,
        "orderproduct":orderproduct,
        "reviews":reviews,
        "product_gallery":product_gallery,
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


def submit_review(request, product_id):
    url = request.META.get('HTTP_REFERER')
    if request.method == 'POST':
        try:
            reviews = ReviewRating.objects.get(user__id=request.user.id, product__id=product_id)
            form = ReviewForm(request.POST, instance=reviews)
            form.save()
            messages.success(request, 'Thank you! Your review has been updated.')
            return redirect(url)
        except ReviewRating.DoesNotExist:
            form = ReviewForm(request.POST)
            if form.is_valid():
                data = ReviewRating()
                data.subject = form.cleaned_data['subject']
                data.rating = form.cleaned_data['rating']
                data.review = form.cleaned_data['review']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id
                data.save()
                messages.success(request, 'Thank you! Your review has been submitted.')
                return redirect(url)

def filter_price(request):
    min_price = request.GET['min_price']
    max_peice = request.GET['max_price']
    price_filter = Product.objects.filter(is_available=True, price__gte=min_price, price__lte=max_peice)

    context={
        "price_filter":price_filter,
    }

    return render(request,'store.html',context)

def size_filter(request):
    XS = request.GET['XS']
    print(XS)

    product_value = list(Variation.objects.filter(variation_value=XS).values())
    product_list=[]
    for i in product_value:
        id=i["product_id"]
        product_list.append(Product.objects.get(id=id))


    print(product_list)

    context = {
        "size_filter": product_list,
    }

    return render(request, 'store.html', context)

def filter(request):
    min_price = request.GET['min_price']
    max_peice = request.GET['max_price']
    category=request.GET['category']
    print(type(category))
    size=request.GET['size']

    price_filter = Product.objects.filter(is_available=True, price__gte=min_price, price__lte=max_peice)

    product_value = list(Variation.objects.filter(variation_value=size).values())
    product_list=[]
    for i in product_value:
        id=i["product_id"]
        product_list.append(Product.objects.get(id=id))

    categores=Category.objects.filter(category_name=category)
    print(categores)
    category_product = Product.objects.filter(category=categores, is_available=True)


    context={
        "price_filter":price_filter,
        "size_filter": product_list,
        #"categores":categores,
        'category_product':category_product,
    }

    return render(request, 'store.html', context)