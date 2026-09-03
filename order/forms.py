from django import forms
from .views import Order

class OrederForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('first_name','last_name','phone_num','email','city','addres','order_note')