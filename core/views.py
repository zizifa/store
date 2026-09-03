from django.shortcuts import render
from store.models import Product,ReviewRating
# Create your views here.

def index(request):
    products = Product.objects.all().filter(is_available=True).order_by('created_at')
    
    # Get all reviews for available products
    product_ids = products.values_list('id', flat=True)
    reviews = ReviewRating.objects.filter(product_id__in=product_ids, status=True)

    context = {
        "products": products,
        "reviews": reviews,
    }
<<<<<<< HEAD
    return render(request, "index.html", context)
=======
    return render(request, "index.html", context)
>>>>>>> origin/master
