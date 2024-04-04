from datetime import datetime, timedelta

from django import forms
from django.forms import PasswordInput
from django.core.exceptions import ValidationError

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


# def date_validator(date):
#     if date > datetime.now():
#         raise ValidationError(f"The date cannot be in the future.")
#     elif date < datetime.now() - timedelta(days=30):
#         raise ValidationError(f"The date must be within last 30 days.")

class AddHoursForm(forms.ModelForm):
    class Meta:
        model = LoggedHours
        fields = ['date', 'sales_channel', 'department', 'hour']
        widgets = {'date': forms.DateInput(format=('%Y/%d/%m'), attrs={'placeholder': 'Select a date', 'type': 'date'})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['sales_channel'].queryset = SalesChannel.objects.all()

    def clean_date(self):
        date = self.cleaned_data['date']
        if date > date.today():
            raise ValidationError ('The date cannot be in the future.')
        elif date < date.today() - timedelta(days=30):
            raise ValidationError(f"The date must be within last 30 days.")
        return date

