from django.shortcuts import render
from store.models import Product,ReviewRating
# Create your views here.

def index(request):
    products=Product.objects.all().filter(is_available=True).order_by('created_at')
    #print(products)

    for product in products:
        reviews = ReviewRating.objects.filter(product_id=product.id, status=True)


    # for i in dd:
    #     dd = Product.objects.all().filter(stock__gte=0)
    #     print(dd)
    #     bb=i/2
    #     solds=Product.objects.filter(sold__gte=bb)
    #     print(solds)


    # papuler_pro=0
    # review = ReviewRating.objects.filter(product_id=product.id)
    # for i in review:
    #     papuler=i.rating
    #     if papuler >1.5:
    #         pro_id=i.id
    #         papuler_pro=ReviewRating.objects.filter(product_id=pro_id)
    #         print(papuler_pro)



    context={
        "products":products,
        "reviews":reviews,
        #'papuler_pro':papuler_pro,
    }
    return render(request,"index.html", context)