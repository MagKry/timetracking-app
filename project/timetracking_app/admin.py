from django.contrib import admin

from .models import Person, LoggedHours, Department, SalesChannel

# Register your models here.


class PersonAdmin(admin.ModelAdmin):
    model = Person
    list_display = ['first_name', 'last_name', 'email', 'department', 'is_active']


admin.site.register(Person, PersonAdmin)
admin.site.register(LoggedHours)
admin.site.register(Department)
admin.site.register(SalesChannel)