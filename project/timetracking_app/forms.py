from datetime import datetime

from django import forms
from django.forms import PasswordInput
from .models import SalesChannel, LoggedHours

SALES_CHANNELS = (
    (1, 'channel_1'),
    (2, 'channel_2'),
    (3, 'channel_3'),
    (4, 'channel_4'),
)


class LoginForm(forms.Form):
    login = forms.CharField(max_length=64)
    password = forms.CharField(max_length=64, widget=PasswordInput)


class AddHoursForm(forms.ModelForm):
    class Meta:
        model = LoggedHours
        fields = ['date', 'sales_channel', 'hour']
        widgets = {'date': forms.DateInput(format=('%Y/%d/%m'), attrs={'placeholder': 'Select a date', 'type': 'date'})}
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sales_channel'].queryset = SalesChannel.objects.all()

