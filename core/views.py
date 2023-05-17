from django.shortcuts import render
from carts.views import cart
from store.models import Product
# Create your views here.
def index(request):

    solded = list(Product.objects.all())
    for j in solded:
        jj = j.stock / 2
        if j.solded > jj:
            product=Product.objects.filter(product_name=j)
        else:
            product = Product.objects.all()
    # product=cart(request).globalproduct
    context={
        "product":product,
    }
    return render(request,"index.html", context)