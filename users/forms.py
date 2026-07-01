from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Address


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
        }


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'country', 'avatar']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 123 456 7890'}),
            'country': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'United States'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if username:
            if User.objects.filter(username=username).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('This username is already taken.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError('This email is already in use.')
        return email

    def clean_avatar(self):
        avatar = self.cleaned_data.get('avatar')
        if avatar:
            if hasattr(avatar, 'size') and avatar.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image file size must be under 5MB.')
        return avatar


class AddressForm(forms.ModelForm):
    class Meta:
        model = Address
        fields = ['full_name', 'address_line_1', 'address_line_2', 'city', 'state', 'postal_code', 'country', 'is_default']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_1': forms.TextInput(attrs={'class': 'form-control'}),
            'address_line_2': forms.TextInput(attrs={'class': 'form-control'}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'postal_code': forms.TextInput(attrs={'class': 'form-control'}),
            'country': forms.TextInput(attrs={'class': 'form-control'}),
            'is_default': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
