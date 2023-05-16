from django.db import models
from store.models import Product ,Variation
from accounts.models import Accounts
# Create your models here.

class Cart(models.Model):
    cart_id=models.CharField(max_length=250,blank=True,null=True)
    date_added=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.cart_id

class CartItem(models.Model):
    user=models.ForeignKey(Accounts,on_delete=models.CASCADE , null=True)
    product=models.ForeignKey(Product,on_delete=models.CASCADE)
    variations=models.ManyToManyField(Variation ,blank=True)
    cart=models.ForeignKey(Cart ,on_delete=models.CASCADE,null=True)
    quantity=models.IntegerField(default=0)
    is_active=models.BooleanField(default=True)

    def sub_total(self):
        if self.product.off_price>0:
            return self.product.off_price * self.quantity
        else:
            return self.product.price * self.quantity

    def __unicode__(self):
        return self.product