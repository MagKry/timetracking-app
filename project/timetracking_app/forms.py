from datetime import datetime

from django import forms
from django.forms import PasswordInput

SALES_CHANNELS = ['channel_1', 'channel_2', 'channel_3', 'channel_4']


class LoginForm(forms.Form):
    login = forms.EmailField(max_length=64)
    password = forms.CharField(max_length=64, widget=PasswordInput)


class AddHoursForm(forms.Form):
    date = forms.DateField(widget=forms.DateInput)
    sales_channel = forms.ChoiceField(choices=SALES_CHANNELS)
    hours = forms.FloatField(min_value=0, max_value=8)
