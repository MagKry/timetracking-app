from datetime import datetime

from django import forms
from django.forms import PasswordInput

SALES_CHANNELS = (
    (1, 'channel_1'),
    (2, 'channel_2'),
    (3, 'channel_3'),
    (4, 'channel_4'),
)


class LoginForm(forms.Form):
    login = forms.EmailField(max_length=64)
    password = forms.CharField(max_length=64, widget=PasswordInput)


class AddHoursForm(forms.Form):
    date = forms.DateField(widget=forms.SelectDateWidget)
    sales_channel = forms.ChoiceField(choices=SALES_CHANNELS)
    hours = forms.FloatField(min_value=0, max_value=8)
