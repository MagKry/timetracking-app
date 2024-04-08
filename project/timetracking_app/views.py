from datetime import datetime, timedelta

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView
from django.http import HttpResponse, QueryDict
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, DeleteView, UpdateView, CreateView
from django.contrib.auth import authenticate, login, logout

from .forms import AddHoursForm, LoginForm
from .models import LoggedHours, SalesChannel, Person, Department


class DateFilterView(View):
    def set_up_query_strings(self, *args, **kwargs):
        query_params = QueryDict(mutable=True)
        # Dodawanie parametrów
        query_params['filter_type'] = 'value'

        # Przekierowanie na nową stronę z query stringiem
        redirect_url = '/channel_hours/?' + query_params.urlencode()
        return redirect_url

    def filter_by_dates_range(self, filter_type):

        if filter_type == 'weekly':
            all_entries = LoggedHours.objects.filter(date__gte=datetime.today(),
                                                     date__lte=datetime.today() + timedelta(days=6))
            return all_entries
        elif filter_type == 'monthly':
            all_entries = LoggedHours.objects.filter(date__gte=datetime.now().replace(day=1).strftime('%Y-%m-%d'))
            return all_entries
        elif filter_type == 'yearly':
            all_entries = LoggedHours.objects.filter(
                date__gte=datetime.now().replace(day=1, month=1).strftime('%Y-%m-%d'))
            return all_entries
        else:
            all_entries = LoggedHours.objects.all()
            return all_entries


# class SummarisedHours(View):
#
#     def get_queryset(self):
#         employee_entries = LoggedHours.objects.all()
#         return employee_entries
#
#     def get_summarised_data(self, field_name, **kwargs):
#         context = self.super().get_context_data()
#         employee_entries = self.get_queryset()
#         hours_per_field = {}
#         for entry in employee_entries:
#             field_value = getattr(entry, field_name)
#             hours = entry.hour
#             if field_value in hours_per_field:
#                 hours_per_field[field_value] += hours
#             else:
#                 hours_per_field[field_value] = hours
#         context['hours_per_field'] = hours_per_field
#         return context


class HomePageView(View):
    def get(self, request):
        return render(request, 'base.html')


class LoginView(FormView):
    template_name = 'login_form.html'
    form_class = LoginForm
    success_url = reverse_lazy('home-page')

    def form_valid(self, form):
        username = form.cleaned_data['login']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)

        if user is not None:
            login(self.request, user)
            return redirect(self.get_success_url())
        else:
            return render(self.request, self.template_name,  {'user': user, 'form': form, 'error_message': 'Login error.'})


class LogoutView(View):
    def get(self, request):
        user = request.user
        logout(request)
        return render(request, 'logout_page.html',  {'user': user, 'message': 'logged out successfully.'})


class AddHoursView(LoginRequiredMixin, FormView):
    template_name = 'add_hours.html'
    form_class = AddHoursForm
    success_url = reverse_lazy('view-hours')

    def form_valid(self, form):
        # Pobierz wartość
        user = self.request.user

        # Utwórz formularz i przekaż wartość do pola
        form = form
        form.fields['employee'].initial = user
        date = form.cleaned_data['date']
        form_sales_channel = form.cleaned_data['sales_channel']
        form_department = form.cleaned_data['department']
        sales_channel = get_object_or_404(SalesChannel, channel_name=form_sales_channel)
        department = get_object_or_404(Department, department_name=form_department)
        hour = form.cleaned_data['hour']

        employee_hours = LoggedHours.objects.create(date=date, hour=hour, employee=user, sales_channel=sales_channel, department=department)

        return super().form_valid(form)


class ViewOwnHoursView(View):
    def get(self, request):
        return render(request, 'view_own_hours.html')


class ListAllHoursView(ListView):
    model = LoggedHours
    success_url = 'list_all_hours/'
    template_name = 'list_hours.html'
    context_object_name = 'employee_entries'
    paginate_by = 10
    ordering = ['sales_channel']


class HoursThisWeekView(ListView):
    model = LoggedHours
    success_url = 'hours-this-week'
    template_name = 'list_hours.html'
    context_object_name = 'employee_entries'
    paginate_by = 10
    ordering = ['-date']

    def get_queryset(self):
        start_date = datetime.today()
        end_date = start_date + timedelta(days=6)
        return LoggedHours.objects.filter(date__gte=start_date, date__lte=end_date)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_entries = self.get_queryset()
        hours_per_channel = {}
        for entry in employee_entries:
            sales_channel = entry.sales_channel
            hours = entry.hour
            if sales_channel in hours_per_channel:
                hours_per_channel[sales_channel] += hours
            else:
                hours_per_channel[sales_channel] = hours
        context['hours_per_channel'] = hours_per_channel
        return context


class HoursThisMonthView(ListView):
    model = LoggedHours
    success_url = 'hours-this-month'
    template_name = 'list_hours.html'
    context_object_name = 'employee_entries'
    paginate_by = 10
    ordering = ['-date']

    def get_queryset(self):
        current_month = datetime.now().replace(day=1).strftime('%Y-%m-%d')
        return LoggedHours.objects.filter(date__gte=current_month)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_entries = self.get_queryset()
        hours_per_channel = {}
        for entry in employee_entries:
            sales_channel = entry.sales_channel
            hours = entry.hour
            if sales_channel in hours_per_channel:
                hours_per_channel[sales_channel] += hours
            else:
                hours_per_channel[sales_channel] = hours
        context['hours_per_channel'] = hours_per_channel
        return context


class HoursThisYearView(ListView):
    model = LoggedHours
    success_url = 'hours-this-year'
    template_name = 'list_hours.html'
    context_object_name = 'employee_entries'
    paginate_by = 10
    ordering = ['-date']

    def get_queryset(self):
        current_year = datetime.now().replace(day=1, month=1).strftime('%Y-%m-%d')
        return LoggedHours.objects.filter(date__gte=current_year)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_entries = self.get_queryset()
        hours_per_channel = {}
        for entry in employee_entries:
            sales_channel = entry.sales_channel
            hours = entry.hour
            if sales_channel in hours_per_channel:
                hours_per_channel[sales_channel] += hours
            else:
                hours_per_channel[sales_channel] = hours
        context['hours_per_channel'] = hours_per_channel
        return context


class HoursPerChannelView(ListView, DateFilterView):
    model = LoggedHours
    fields = '__all__'
    template_name = 'channel_hours.html'
    context_object_name = 'logged_hours'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_type = self.request.GET.get('filter_type')
        all_entries = self.filter_by_dates_range(filter_type)

        context['filter_type'] = filter_type

        hours_per_channel = {}
        for entry in all_entries:
            sales_channel = entry.sales_channel
            hours = entry.hour
            if sales_channel in hours_per_channel:
                hours_per_channel[sales_channel] += hours
            else:
                hours_per_channel[sales_channel] = hours
        context['hours_per_channel'] = hours_per_channel
        labels_data = self.get_labels_data()
        context.update(labels_data)

        context['weekly'] = self.set_up_query_strings('weekly')
        context['monthly_url'] = self.set_up_query_strings('monthly')
        context['yearly_url'] = self.set_up_query_strings('yearly')

        return context

    def get_labels_data(self):
        filter_type = self.request.GET.get('filter_type')
        logged_hours = self.filter_by_dates_range(filter_type)
        labels = []
        data = []
        for entry in logged_hours:
            sales_channel = entry.sales_channel.channel_name
            if sales_channel not in labels:
                labels.append(sales_channel)
                hours = sum(entry.hour for entry in logged_hours if entry.sales_channel.channel_name == sales_channel)
                data.append(hours)
        return {'labels': labels, 'data': data}


class ViewDepartmentHoursView(ListView, DateFilterView):
    model = LoggedHours
    fields = '__all__'
    template_name = 'department_hours.html'
    context_object_name = 'logged_hours'

    def get_queryset(self):
        filter_type = self.request.GET.get('filter_type')
        return self.filter_by_dates_range(filter_type)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        logged_hours = self.get_queryset()
        hours_per_department = {}
        for entry in logged_hours:
            department = entry.department
            hours = entry.hour
            sales_channel = entry.sales_channel
            if department in hours_per_department:
                if sales_channel in hours_per_department[department]:
                    hours_per_department[department][sales_channel] += hours
                else:
                    hours_per_department[department][sales_channel] = hours
            else:
                hours_per_department[department] = {sales_channel:hours}
        context['hours_per_department'] = hours_per_department

        labels_data = self.get_labels_data(self.request.user)
        context.update(labels_data)

        return context

    def get_labels_data(self, user):
        logged_hours = self.get_queryset()
        labels = []
        data = []
        hours_per_department = {}
        for entry in logged_hours:
            department = entry.department.department_name
            if department not in hours_per_department:
                hours_per_department[department] = entry.hour
            else:
                hours_per_department[department] += entry.hour

        # Konwersja słownika na listy etykiet i danych
        for department, hours in hours_per_department.items():
            labels.append(department)
            data.append(hours)

        return {'labels': labels, 'data': data}


class ViewEmployeesHoursView(ListView):
    model = LoggedHours
    fields = '__all__'
    template_name = 'all_employees_hours.html'
    success_url = 'employees_hours/'
    context_object_name = 'employee_entries'
    ordering = ['employee']


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Lista godzin wszystkich pracowników
        employee_entries = LoggedHours.objects.all()
        context['employee_entries'] = employee_entries

        # Suma godzin dla każdego pracownika
        hours_per_employee = {}
        for entry in employee_entries:
            employee = entry.employee
            hours = entry.hour
            if employee is not None:
                employee = employee
                if employee in hours_per_employee:
                    hours_per_employee[employee] += hours
                else:
                    hours_per_employee[employee] = hours
        context['hours_per_employee'] = hours_per_employee

        return context

class AddEmployeeView(CreateView):
    model = Person
    fields = ['username', 'first_name', 'last_name', 'email', 'password', 'department']
    template_name = 'add_employee.html'
    success_url = reverse_lazy('employees-hours')

    def form_valid(self, form):
        # username = form.cleaned_data['username']
        # first_name = form.cleaned_data['first_name']
        # last_name = form.cleaned_data['last_name']
        # email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        # department = form.cleaned_data['department']
        response = super().form_valid(form)
        self.object.set_password(password)
        self.object.save()

        # user = Person.objects.create_user(username=username, password=password, email=email, first_name=first_name, last_name=last_name,department=department)

        return response
        # return HttpResponse(f'User {user} successfully added.') #metoda super



class DeleteHoursView(DeleteView):
    model = LoggedHours
    success_url = reverse_lazy('list-all-hours')
    template_name ='loggedhours_confirm_delete.html'


class EditHoursView(UpdateView):
    model = LoggedHours
    fields = ['date', 'hour', 'sales_channel', 'department']
    template_name = 'loggedhours_update_form.html'
    success_url = reverse_lazy('list-all-hours')


class EditEmployeeView(UpdateView): #brakuje przycisku umożliwiającego edycję
    model = Person
    fields = ['username', 'first_name', 'last_name', 'email', 'password', 'department']
    template_name = 'person_update_form.html'
    success_url = reverse_lazy('employees-hours')


class ListEmployeesView(ListView):
    model = Person
    success_url = reverse_lazy('list-all-people')
    template_name ='list_people.html'
    context_object_name = 'employee_entries'


class DeleteEmployeeView(DeleteView):
    model = Person
    success_url = reverse_lazy('list-employees')
    template_name ='delete_people_confirm_delete.html'
