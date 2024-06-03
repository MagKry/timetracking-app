from datetime import datetime, timedelta

from django import forms
from django.forms import PasswordInput
from django.core.exceptions import ValidationError

from .models import SalesChannel, LoggedHours, Department, Person


class LoginForm(forms.Form):
    # username = forms.CharField(label='login', max_length=64)
    email = forms.EmailField(label='email')
    password = forms.CharField(label='password', max_length=64, widget=PasswordInput)


class AddHoursForm(forms.ModelForm):
    employee = forms.ModelChoiceField(queryset=Person.objects.all(), widget=forms.HiddenInput(), required=False)
    class Meta:
        model = LoggedHours
        fields = ['date', 'sales_channel', 'department', 'hour']
        widgets = {'date': forms.DateInput(format=('%Y/%d/%m'), attrs={'placeholder': 'Select a date', 'type': 'date'})}

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Pobierz użytkownika przekazanego do formularza
        super().__init__(*args, **kwargs)
        if user:
            # Jeśli użytkownik jest dostępny, ustaw jego wartość dla pola employee
            self.initial['employee'] = user
            # Ukryj pole employee w formularzu
            self.fields['employee'].widget = forms.HiddenInput()
        self.fields['sales_channel'].queryset = SalesChannel.objects.all()
        self.fields['department'].queryset = Department.objects.all()


    def clean_date(self):
        date = self.cleaned_data['date']
        if date > date.today():
            raise ValidationError ('The date cannot be in the future.')
        elif date < date.today() - timedelta(days=30):
            raise ValidationError(f"The date must be within last 30 days.")
        return date

