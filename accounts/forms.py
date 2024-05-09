# Django
from django import forms
from django.contrib.auth.password_validation import validate_password
# Project
from .models import User


class RegisterForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "placeholder": "ایمیل"
    }))
    password = forms.CharField(max_length=128, required=True, validators=[validate_password], widget=forms.PasswordInput(attrs={
        "placeholder": "رمز عبور"
    }))
    confirm_password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput(attrs={
        "placeholder": "تکرار رمز عبور"
    }))

    def clean_confirm_password(self):
        """Check the equality of password and confirm_password"""
        password = self.data["password"]
        confirm_password = self.data["confirm_password"]
        if password == confirm_password:
            return confirm_password
        raise forms.ValidationError("عدم مطابقت با گذرواژه")

    def clean_email(self):
        """Check the uniqueness of the email"""
        email = self.data["email"]
        try:
            User.objects.get(email=email)
        except:
            return email
        else:
            raise forms.ValidationError("این ایمیل تکراری است")


class LoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "placeholder": "ایمیل"
    }))
    password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput(attrs={
        "placeholder": "رمز عبور"
    }))


class ForgotPasswordForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        "placeholder": "ایمیل"
    }))


class ResetPasswordForm(forms.Form):
    activation_code = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={
        "placeholder": "کد"
    }))
    password = forms.CharField(max_length=128, required=True, validators=[validate_password], widget=forms.PasswordInput(attrs={
        "placeholder": "رمز عبور"
    }))
    confirm_password = forms.CharField(max_length=128, required=True, widget=forms.PasswordInput(attrs={
        "placeholder": "تکرار رمز عبور"
    }))

    def clean_confirm_password(self):
        """Check the equality of password and confirm_password"""
        password = self.data["password"]
        confirm_password = self.data["confirm_password"]
        if password == confirm_password:
            return confirm_password
        raise forms.ValidationError("عدم مطابقت با گذرواژه")
