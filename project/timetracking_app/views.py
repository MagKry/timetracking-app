from datetime import datetime, timedelta

from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView, ListView, DeleteView
from django.contrib.auth import authenticate, login, logout

from .forms import LoginForm, AddHoursForm
from .models import LoggedHours, SalesChannel


class HomePageView(View):
    def get(self, request):
        return render(request, 'base.html')


class LoginView(FormView):
    template_name = 'login_form.html'
    form_class = LoginForm
    success_url = 'home-page'

    def form_valid(self, form):
        username = form.cleaned_data['login']
        password = form.cleaned_data['password']
        user = authenticate(username=username, password=password)


        if user is not None:
            login(self.request, user)
            return render(self.request, 'base.html')
        else:
            return render(self.request, self.template_name,  {'user': user, 'form': form, 'error_message': 'Błąd logowania'})


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
        sales_channel = get_object_or_404(SalesChannel, channel_name=form_sales_channel)
        hour = form.cleaned_data['hour']
        user = self.request.user

        employee_hours = LoggedHours.objects.create(date=date, hour=hour, sales_channel=sales_channel)
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
    paginate_by = 1000
    ordering = ['sales_channel']


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
        return context


class HoursThisWeekView(ListView):
    model = LoggedHours
    success_url = 'hours-this-week'
    template_name = 'list_hours.html'
    context_object_name = 'employee_entries'
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



class ViewDepartmentHoursView(View):
    def get(self, request):
        return render(request, 'department_hours.html')


class ViewEmployeesHoursView(View):
    def get(self, request):
        return render(request, 'all_employees_hours.html')


class AddEmployeeView(View):
    def get(self, request):
        return render(request, 'add_employee.html')


class DeleteHoursView(DeleteView):
    model = LoggedHours
    success_url = reverse_lazy('list-all-hours')
    template_name ='loggedhours_confirm_delete.html'
