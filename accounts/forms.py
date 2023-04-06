from django import forms
from .models import Accounts

class RegisterForm(forms.ModelForm):
    password=forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'Enter password',
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'placeholder':'confirm password'
    }))

    class Meta:
        model = Accounts
        fields=["first_name","last_name","email","phone_number","password"]

    def clean(self):
        cleaned_data=super(RegisterForm, self).clean()
        password=cleaned_data.get('password')
        confirm_password=cleaned_data.get('confirm_password')

        if password != confirm_password:
            raise forms.ValidationError(
                'password does not match'
            )


    #css style
    def __init__(self , *args, **kwargs):
        super(RegisterForm , self).__init__(*args,**kwargs)
        self.fields["first_name"].widget.attrs['placeholder'] = 'Enter Firstname'
        self.fields["last_name"].widget.attrs['placeholder'] = 'Enter Lastname'
        self.fields["phone_number"].widget.attrs['placeholder'] = 'Enter phone number'
        self.fields["email"].widget.attrs['placeholder'] = 'Enter email'
        for field in self.fields:
            self.fields[field].widget.attrs['class']='form-control'



