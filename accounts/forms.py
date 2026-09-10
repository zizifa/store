from django import forms
from django.core.exceptions import ValidationError
from phonenumber_field.phonenumber import to_python


class RequestOTPForm(forms.Form):
    phone_number = forms.CharField(max_length=20, label='Phone number')
    next = forms.CharField(required=False, widget=forms.HiddenInput())
    purpose = forms.CharField(required=False, initial='LOGIN', widget=forms.HiddenInput())

    def clean_phone_number(self):
        phone_raw = self.cleaned_data.get('phone_number')
        phone = to_python(phone_raw, region='IR')
        if not phone or not phone.is_valid():
            raise ValidationError('Please enter a valid phone number.')
        self.cleaned_phone = phone.as_e164
        return self.cleaned_phone


class VerifyOTPForm(forms.Form):
    phone_number = forms.CharField(max_length=20, label='Phone number')
    otp = forms.CharField(max_length=6, label='OTP code')
    next = forms.CharField(required=False, widget=forms.HiddenInput())
    purpose = forms.CharField(required=False, initial='LOGIN', widget=forms.HiddenInput())

    def clean_phone_number(self):
        phone_raw = self.cleaned_data.get('phone_number')
        phone = to_python(phone_raw, region='IR')
        if not phone or not phone.is_valid():
            raise ValidationError('Invalid phone number.')
        self.cleaned_phone = phone.as_e164
        return self.cleaned_phone

    def clean_otp(self):
        otp = self.cleaned_data.get('otp', '')
        if not otp.isdigit() or len(otp) != 6:
            raise ValidationError('Please enter a valid 6-digit OTP code.')
        return otp
