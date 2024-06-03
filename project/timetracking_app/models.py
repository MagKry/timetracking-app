from datetime import datetime

from django.contrib.auth.models import User, AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models

# Create your models here.


class Person(AbstractUser):
    email = models.EmailField(unique=True)
    department = models.ForeignKey('Department', related_name='persons_department', on_delete=models.CASCADE, null=True)
    sales_channels = models.ManyToManyField('SalesChannel')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return f"{self.username}, {self.first_name}, {self.last_name}, {self.email}"


class Department(models.Model):
    department_name = models.CharField(max_length=64, unique=True)
    manager = models.ForeignKey(Person, related_name='department_manager', on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.department_name}'


class SalesChannel(models.Model):
    channel_name = models.CharField(max_length=64, unique=True)
    department = models.ManyToManyField(Department)

    def __str__(self):
        return f'{self.channel_name}'


class LoggedHours(models.Model):
    date = models.DateField(null=True)
    hour = models.FloatField(validators=(MinValueValidator(0.25), MaxValueValidator(8)))
    employee = models.ForeignKey(Person, on_delete=models.CASCADE)
    sales_channel = models.ForeignKey(SalesChannel, on_delete=models.CASCADE)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, null=True)

    def __str__(self):
        return f'{self.date}, {self.hour}, {self.employee}, {self.sales_channel}'
