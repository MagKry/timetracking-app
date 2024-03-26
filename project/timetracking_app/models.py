from django.db import models

# Create your models here.


class Person(models.Model):
    name = models.CharField()
    email = models.CharField(max_length=64)
    department = models.ForeignKey('Department', related_name='persons_department', on_delete=models.CASCADE, null=True)


class Department(models.Model):
    department_name = models.CharField(max_length=64, unique=True)
    manager = models.ForeignKey(Person, related_name='department_manager', on_delete=models.CASCADE)


class SalesChannel(models.Model):
    channel_name = models.CharField(max_length=64, unique=True)
    employee = models.ManyToManyField(Person)
    department = models.ManyToManyField(Department)


class LoggedHours(models.Model):
    hour = models.FloatField()
    employee = models.ManyToManyField(Person)
    sales_channel = models.ForeignKey(SalesChannel, on_delete=models.CASCADE)
