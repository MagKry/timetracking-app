from django.contrib import admin

from .models import Person, LoggedHours, Department, SalesChannel

# Register your models here.


class PersonAdmin(admin.ModelAdmin):
    model = Person
    list_display = ['first_name', 'last_name', 'email', 'department', 'is_active']

class DepartmentAdmin(admin.ModelAdmin):
    model = Department
    list_display = ['department_name', 'get_manager']

    def get_manager(self, obj):
        return obj.manager.last_name, obj.manager.first_name if obj.manager else 'No Manager'

    get_manager.short_description = 'Manager name'

class LoggedHoursAdmin(admin.ModelAdmin):
    model = LoggedHours
    list_display = ['date', 'get_employee_name', 'hour', 'sales_channel', 'department']

    def get_employee_name(self, obj):
        return obj.employee.last_name, obj.employee.first_name if obj.employee else 'No employee'


admin.site.register(Person, PersonAdmin)
admin.site.register(LoggedHours, LoggedHoursAdmin)
admin.site.register(Department, DepartmentAdmin)
admin.site.register(SalesChannel)