from .models import CartItem,Cart
from .views import _cart_id

def counter(request):
    quantity_counter=0
    if 'admin'in request.path:
        return {}
    try:
        cart=Cart.objects.filter(cart_id=_cart_id(request))
        cart_items=CartItem.objects.filter(cart=cart[:1])
        for cart_item in cart_items:
            quantity_counter += cart_item.quantity
    except Cart.DoesNotExist:
        quantity_counter=0
    return dict(quantity_counter=quantity_counter)