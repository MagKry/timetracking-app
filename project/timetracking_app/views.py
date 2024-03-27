from django.http import HttpResponse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import FormView
from django.contrib.auth import authenticate, login, logout

from .forms import LoginForm, AddHoursForm


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
            return super().form_valid(form)
        else:
            return render(self.request, 'base.html',  {'user': user, 'form': form, 'error_message': 'Błąd logowania'})


class LogoutView(View):
    def get(self, request):
        user = request.user
        logout(request)
        return render(self.request, 'logout_page.html',  {'user': user, 'message': 'logged out successfully.'})


class AddHoursView(FormView):
    form_template = 'add_hours.html'
    form_class = AddHoursForm
    success_url = 'view-hours'
    def get(self, request):
        return render(request, 'add_hours.html')


class ViewOwnHoursView(View):
    def get(self, request):
        return render(request, 'view_own_hours.html')


class ViewDepartmentHoursView(View):
    def get(self, request):
        return render(request, 'department_hours.html')


class ViewEmployeesHoursView(View):
    def get(self, request):
        return render(request, 'all_employees_hours.html')


class AddEmployeeView(View):
    def get(self, request):
        return render(request, 'add_employee.html')


