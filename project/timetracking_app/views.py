from datetime import datetime, timedelta

from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, DeleteView, UpdateView, CreateView
from django.contrib.auth import authenticate, login, logout

from .forms import AddHoursForm, LoginForm
from .models import LoggedHours, SalesChannel, Person, Department


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


class AddHoursView(FormView):
    template_name = 'add_hours.html'
    form_class = AddHoursForm
    success_url = reverse_lazy('view-hours')

    def form_valid(self, form):
        date = form.cleaned_data['date']
        form_sales_channel = form.cleaned_data['sales_channel']
        form_department = form.cleaned_data['department']
        sales_channel = get_object_or_404(SalesChannel, channel_name=form_sales_channel)
        department = get_object_or_404(Department, department_name=form_department)
        hour = form.cleaned_data['hour']
        user = self.request.user

        employee_hours = LoggedHours.objects.create(date=date, hour=hour, sales_channel=sales_channel, department=department)
        employee_hours.employee.add(user)

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


class HoursPerChannelView(ListView):
    model = LoggedHours
    fields = '__all__'
    template_name = 'channel_hours.html'
    context_object_name = 'logged_hours'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        employee_entries = LoggedHours.objects.filter(employee=self.request.user)
        hours_per_channel = {}
        for entry in employee_entries:
            sales_channel = entry.sales_channel
            hours = entry.hour
            if sales_channel in hours_per_channel:
                hours_per_channel[sales_channel] += hours
            else:
                hours_per_channel[sales_channel] = hours
        context['hours_per_channel'] = hours_per_channel
        labels_data = self.get_labels_data(self.request.user)
        context.update(labels_data)
        return context

    def get_labels_data(self, user):
        logged_hours = LoggedHours.objects.filter(employee=user)
        labels = [entry.sales_channel.channel_name for entry in logged_hours]
        data = [entry.hour for entry in logged_hours]
        return {'labels': labels, 'data': data}



class ViewDepartmentHoursView(ListView):
    model = LoggedHours
    fields = '__all__'
    template_name = 'department_hours.html'
    context_object_name = 'logged_hours'

    def get_queryset(self):
        return LoggedHours.objects.all()

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
        return context


class ViewEmployeesHoursView(ListView):
    model = LoggedHours
    fields = '__all__'
    template_name = 'all_employees_hours.html'
    success_url = 'employees_hours/'
    context_object_name = 'employee_entries'
    ordering = ['employee']

    def get_queryset(self):
        employees = Person.objects.all()
        # Tworzymy słownik, w którym kluczem jest pracownik, a wartością jest lista jego godzin
        all_hours = {}
        for employee in employees:
            all_hours[employee] = LoggedHours.objects.filter(employee=employee)
        return all_hours.items()


class AddEmployeeView(CreateView):
    model = Person
    fields = ['username', 'first_name', 'last_name', 'email', 'password', 'department']
    template_name = 'add_employee.html'
    success_url = reverse_lazy('employees-hours')

    def form_valid(self, form):
        username = form.cleaned_data['username']
        first_name = form.cleaned_data['first_name']
        last_name = form.cleaned_data['last_name']
        email = form.cleaned_data['email']
        password = form.cleaned_data['password']
        department = form.cleaned_data['department']

        user = Person.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name,department=department)
        user.set_password(password)

        return HttpResponse(f'User {user} successfully added.')



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
