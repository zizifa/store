from django.db import models
from accounts.models import Accounts
from store.models import Product,Variation

class Payment(models.Model):
    user=models.ForeignKey(Accounts,on_delete=models.CASCADE)
    payment_id=models.CharField(max_length=100)
    payment_method=models.CharField(max_length=100)
    amount_paymenr=models.CharField(max_length=100)
    status=models.CharField(max_length=100)
    crated_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.payment_id


class Order(models.Model):
    STATUS_CHOISES=(
        ('new',"new"),
        ('accepted', "accepted"),
        ('completed', "completed"),
        ('cancelled', "cancelled"),
    )
    user=models.ForeignKey(Accounts,on_delete=models.CASCADE,null=True)
    order_num=models.CharField(max_length=20)
    payment=models.ForeignKey(Payment,on_delete=models.CASCADE,blank=True,null=True)
    first_name=models.CharField(max_length=50)
    last_name=models.CharField(max_length=50)
    phone_num=models.CharField(max_length=50)
    email=models.EmailField(max_length=50,blank=True)
    addres=models.CharField(max_length=50)
    city=models.CharField(max_length=50)
    state=models.CharField(max_length=50)
    order_note=models.TextField(max_length=200,blank=True)
    order_total=models.FloatField()
    post_price=models.FloatField()
    status=models.CharField(max_length=19,choices=STATUS_CHOISES,default="new")
    ip=models.CharField(max_length=20,blank=True)
    is_ordered=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.first_name



class OrderProduct(models.Model):
    order=models.ForeignKey(Order,on_delete=models.CASCADE)
    payment=models.ForeignKey(Payment,on_delete=models.CASCADE,blank=True,null=True)
    user=models.ForeignKey(Accounts,on_delete=models.CASCADE,null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variation=models.ForeignKey(Variation,on_delete=models.CASCADE)
    color=models.CharField(max_length=15)
    size=models.CharField(max_length=10)
    quantity=models.IntegerField()
    product_price=models.FloatField()
    ordered=models.BooleanField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.product.product_name


