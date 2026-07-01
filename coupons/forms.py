from django import forms
from .models import Coupon


class CouponApplyForm(forms.Form):
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code',
        })
    )

    def clean_code(self):
        code = self.cleaned_data.get('code', '').upper().strip()
        try:
            coupon = Coupon.objects.get(code=code)
        except Coupon.DoesNotExist:
            raise forms.ValidationError('Invalid coupon code.')
        if not coupon.is_valid():
            raise forms.ValidationError('This coupon has expired or is no longer valid.')
        return code
