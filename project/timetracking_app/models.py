from datetime import datetime

from django.contrib.auth.models import User, AbstractUser
from django.db import models

# Create your models here.


class Person(AbstractUser):
    department = models.ForeignKey('Department', related_name='persons_department', on_delete=models.CASCADE, null=True)
    sales_channels = models.ManyToManyField('SalesChannel')

    def __str__(self):
        return f"{self.username}"



class Department(models.Model):
    department_name = models.CharField(max_length=64, unique=True)
    manager = models.ForeignKey(Person, related_name='department_manager', on_delete=models.CASCADE)

    def __str__(self):
        return self.department_name


class SalesChannel(models.Model):
    channel_name = models.CharField(max_length=64, unique=True)
    department = models.ManyToManyField(Department)

    def __str__(self):
        return self.channel_name


class LoggedHours(models.Model):
    date = models.DateField(null=True)
    hour = models.FloatField()
    employee = models.ManyToManyField(Person)
    sales_channel = models.ForeignKey(SalesChannel, on_delete=models.CASCADE)

    def __str__(self):
        return self.date, self.hour, self.employee, self.sales_channel


