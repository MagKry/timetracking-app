from django import forms
from django.forms import PasswordInput


class LoginForm(forms.Form):
    login = forms.EmailField(max_length=64)
    password = forms.CharField(max_length=64, widget=PasswordInput)
