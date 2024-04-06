from django.contrib import admin

from .models import Person, LoggedHours, Department, SalesChannel

# Register your models here.

admin.site.register(Person)
admin.site.register(LoggedHours)
admin.site.register(Department)
admin.site.register(SalesChannel)