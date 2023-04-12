from django.shortcuts import render , redirect
from carts.models import CartItem
from .models import Order
from .forms import OrederForm
from django.http import HttpResponse
import datetime

def place_order(request,total_price=0,quantity=0):

    current_user=request.user
    cart_items=CartItem.objects.filter(user=current_user)
    cart_items_count = cart_items.count()
    if cart_items_count <= 0:
        return redirect('store')

    post_price = 25000
    for cart_item in cart_items:
        total_price = total_price + (cart_item.product.price * cart_item.quantity)
        quantity = quantity + cart_item.quantity
    final_total = total_price + post_price

    form = OrederForm()
    if request.method == 'POST':
        print('before')
        form=OrederForm(request.POST)
        print('after')
        if form.is_valid():
            print('is valid')
            data = Order()
            data.user=current_user
            data.first_name=form.cleaned_data["first_name"]
            data.last_name=form.cleaned_data["last_name"]
            data.phone_num=form.cleaned_data["phone_num"]
            data.email=form.cleaned_data["email"]
            data.city=form.cleaned_data["city"]
            data.addres=form.cleaned_data["addres"]
            data.order_note=form.cleaned_data["order_note"]
            data.order_total= final_total
            #data.post_pay=post_price
            data.ip=request.META.get('REMOTE_ADDR')
            data.save()

            yr = int(datetime.date.today().strftime('%Y'))
            dt = int(datetime.date.today().strftime('%d'))
            mt = int(datetime.date.today().strftime('%m'))
            d = datetime.date(yr, mt, dt)
            current_date = d.strftime("%Y%m%d")
            order_num=current_date + str(data.id)
            data.order_num = order_num
            data.save()
            return redirect('checkout')
        # else:
        #     return HttpResponse("problem")
    else:
        return redirect('checkout')

