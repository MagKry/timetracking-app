import sendgrid
import os

from sendgrid.helpers.mail import *

from django.utils import timezone
from django.utils.timezone import timedelta

from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.contrib.auth.models import Permission, Group
from django.contrib.auth.views import LoginView
from django.contrib.contenttypes.models import ContentType
from django.contrib import messages
from django.contrib.auth.tokens import default_token_generator
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from django.http import HttpResponse, QueryDict
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.views import View
from django.views.generic import FormView, ListView, DeleteView, UpdateView, CreateView, DetailView
from django.contrib.auth import authenticate, login, logout
from django.core.mail import send_mail
from django.conf import settings

from .forms import AddHoursForm, LoginForm, ResetPasswordForm, SearchEmployeeForm
from .models import LoggedHours, SalesChannel, Person, Department


#Create a parent class with methods that will be reused in the code.
class DateFilterView(View):

#Setting up query strings to be used for filtering data
    def set_up_query_strings(self, *args, **kwargs):
        query_params = QueryDict(mutable=True)
        #Setting up query parameters
        query_params['filter_type'] = 'value'

        # Redirecting to the selected page dependent on selected parameter
        redirect_url = '/channel_hours/?' + query_params.urlencode()
        return redirect_url

#Filtering based on specified timeframes (weekly, monthly, yearly or without any filter)
    def filter_by_dates_range(self, filter_type):
        #filter 'weekly'
        if filter_type == 'weekly':
            all_entries = LoggedHours.objects.filter(date__gte=timezone.now(),
                                                     date__lte=timezone.now() + timedelta(days=6))
            return all_entries
        # filter 'monthly'
        elif filter_type == 'monthly':
            all_entries = LoggedHours.objects.filter(date__gte=timezone.now().replace(day=1).strftime('%Y-%m-%d'))
            return all_entries
        # filter 'yearly'
        elif filter_type == 'yearly':
            all_entries = LoggedHours.objects.filter(
                date__gte=timezone.now().replace(day=1, month=1).strftime('%Y-%m-%d'))
            return all_entries
        # no date filter - all data
        else:
            all_entries = LoggedHours.objects.all()
            return all_entries


#Home page - visible to logged in users only.
class HomePageView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        return render(request, 'base.html')

#Login page + redirection to login from restricted views
class LoginView(FormView):
    template_name = 'login_form.html'
    form_class = LoginForm
    success_url = reverse_lazy('home-page')

    def form_valid(self, form):
        # username = form.cleaned_data['username'] #fetch login
        email = form.cleaned_data['email']
        password = form.cleaned_data['password'] #fetch password
        user = authenticate(username=email, password=password) #authenticate user

        #if user is aythenticated - log them in
        if user is not None:
            login(self.request, user)
            return redirect(self.get_success_url())
        #return the form with the error message to the users that did not successfully login
        else:
            return render(self.request, self.template_name,  {'user': user, 'form': form, 'error_message': 'Login error.'})

#Logout the user, display a message
class LogoutView(View):
    def get(self, request):
        user = request.user
        logout(request)
        return render(request, 'logout_page.html',  {'user': user, 'message': 'logged out successfully.'})

#Add hours of a logged in user to the database.
class AddHoursView(LoginRequiredMixin, FormView):
    login_url = '/login/'
    template_name = 'add_hours.html'
    form_class = AddHoursForm
    success_url = reverse_lazy('list-all-hours')


    def form_valid(self, form):
        # Fetch info about the user
        user = self.request.user

        # Create add hours form, prefill the user data and let the user fill in the ramining details
        form = form
        form.fields['employee'].initial = user
        date = form.cleaned_data['date']
        form_sales_channel = form.cleaned_data['sales_channel']
        form_department = form.cleaned_data['department']
        sales_channel = get_object_or_404(SalesChannel, channel_name=form_sales_channel)
        department = get_object_or_404(Department, department_name=form_department)
        hour = form.cleaned_data['hour']

        #Add hours to the database
        employee_hours = LoggedHours.objects.create(date=date, hour=hour, employee=user, sales_channel=sales_channel, department=department)

        return super().form_valid(form)


#Display all hours added by a logged in user.
class ListAllHoursView(LoginRequiredMixin, ListView, DateFilterView):
    login_url = '/login/'
    model = LoggedHours
    success_url = '/list_all_hours/'
    template_name = 'list_hours.html'
    context_object_name = 'employee_entries'
    paginate_by = 10
    ordering = ['sales_channel']

    def get_queryset(self):
        user = self.request.user
        queryset = LoggedHours.objects.filter(employee=user)
        queryset = self.filter_by_dates_range(queryset)
        return queryset

    # filter data dependent on dates range
    def filter_by_dates_range(self, queryset):
        filter_type = self.request.GET.get('filter_type')
        if filter_type == 'weekly':
            start_date = timezone.now() - timezone.timedelta(days=7)
        elif filter_type == 'monthly':
            start_date = timezone.now() - timezone.timedelta(days=30)
        elif filter_type == 'yearly':
            start_date = timezone.now() - timezone.timedelta(days=365)
        else:
            # Default: no filtering
            return queryset

        return queryset.filter(date__gte=start_date)

    # summarize data per channel and dates range selected by user
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_type = self.request.GET.get('filter_type')
        # apply filter by date
        context['filter_type'] = filter_type
        # get queryset
        all_entries = self.get_queryset()


        # get context data to the filtering buttons
        context['weekly'] = self.set_up_query_strings('weekly')
        context['monthly_url'] = self.set_up_query_strings('monthly')
        context['yearly_url'] = self.set_up_query_strings('yearly')

        return context


#Allow access to view summarised hours per sales channel to logged in users with specified permissions.
class HoursPerChannelView(LoginRequiredMixin, PermissionRequiredMixin, ListView, DateFilterView):
    login_url = '/login/'
    permission_required = ['timetracking_app.view_hours_per_channel']

    model = LoggedHours
    fields = '__all__'
    template_name = 'channel_hours.html'
    context_object_name = 'logged_hours'

    #Filter queryset dependent on the user group.
    def get_queryset(self):
        user = self.request.user

        # restricting data visibility - managers can view their departments only, director can view all departments
        if user.groups.filter(name='director_user').exists():
            queryset = LoggedHours.objects.all()
        elif user.groups.filter(name='manager_user').exists():
            queryset = LoggedHours.objects.filter(department=user.department)

        else:
            queryset = LoggedHours.objects.all()

        queryset = self.filter_by_dates_range(queryset)
        return queryset

    #filter data dependent on dates range
    def filter_by_dates_range(self, queryset):
        filter_type = self.request.GET.get('filter_type')
        if filter_type == 'weekly':
            start_date = timezone.now() - timezone.timedelta(days=7)
        elif filter_type == 'monthly':
            start_date = timezone.now() - timezone.timedelta(days=30)
        elif filter_type == 'yearly':
            start_date = timezone.now() - timezone.timedelta(days=365)
        else:
            # Default: no filtering
            return queryset

        return queryset.filter(date__gte=start_date)

    #summarize data per channel and dates range selected by user
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        filter_type = self.request.GET.get('filter_type')
        #apply filter by date
        context['filter_type'] = filter_type
        #get queryset
        all_entries = self.get_queryset()

        #summarize hours per channel (of all users)
        hours_per_channel = {}
        for entry in all_entries:
            sales_channel = entry.sales_channel
            hours = entry.hour
            if sales_channel in hours_per_channel:
                hours_per_channel[sales_channel] += hours
            else:
                hours_per_channel[sales_channel] = hours
        context['hours_per_channel'] = hours_per_channel

        #calling function that sets up the context data for charts
        labels_data = self.get_labels_data(all_entries)
        context.update(labels_data)

        #get context data to the filtering buttons
        context['weekly'] = self.set_up_query_strings('weekly')
        context['monthly_url'] = self.set_up_query_strings('monthly')
        context['yearly_url'] = self.set_up_query_strings('yearly')

        return context

    #structure the context data for the charts
    def get_labels_data(self, logged_hours):
        labels = []
        data = []
        for entry in logged_hours:
            sales_channel = entry.sales_channel.channel_name
            if sales_channel not in labels:
                labels.append(sales_channel)
                hours = sum(entry.hour for entry in logged_hours if entry.sales_channel.channel_name == sales_channel)
                data.append(hours)
        return {'labels': labels, 'data': data}


#Display hours per department to logged in users, who have appropriate permissions
class ViewDepartmentHoursView(LoginRequiredMixin, PermissionRequiredMixin, ListView, DateFilterView):
    login_url = '/login/'
    permission_required = ['timetracking_app.view_hours_per_department']

    model = LoggedHours
    fields = '__all__'
    template_name = 'department_hours.html'
    context_object_name = 'logged_hours'

    def get_queryset(self):
        user = self.request.user
        #restricting data visibility - managers can view their departments only, director can view all departments
        if user.groups.filter(name='director_user').exists():
            queryset = LoggedHours.objects.all()
            return queryset
        elif user.groups.filter(name='manager_user').exists():
            queryset = LoggedHours.objects.filter(department=user.department)
            return queryset

        #calling function that filters data by specified date ranges
        filter_type = self.request.GET.get('filter_type')
        return self.filter_by_dates_range(filter_type)

    #summarizing hours added by all users per sales channel and per department
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

        #calling functions setting up context data for charts
        labels_data = self.get_labels_data(self.request.user)
        context.update(labels_data)

        return context

    #stucture the context data for the charts
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

        #convert a dictionary to lists of labels and data
        for department, hours in hours_per_department.items():
            labels.append(department)
            data.append(hours)

        return {'labels': labels, 'data': data}


#Display list of hours added by all employees to loggedin users with specified permissions.
class ViewEmployeesHoursView(LoginRequiredMixin, PermissionRequiredMixin, ListView, DateFilterView):
    login_url = '/login/'
    permission_required = ['timetracking_app.view_hours_per_employee']

    model = LoggedHours
    fields = '__all__'
    template_name = 'all_employees_hours.html'
    success_url = 'employees_hours/'
    context_object_name = 'employee_entries'
    ordering = ['employee']
    paginate_by = 10

    def get_queryset(self):
        user = self.request.user
        #restricting data visibility - managers can view their departments only, director can view all departments
        if user.groups.filter(name='director_user').exists():
            queryset = LoggedHours.objects.all()
            return queryset
        elif user.groups.filter(name='manager_user').exists():
            queryset = LoggedHours.objects.filter(department=user.department)
            return queryset

        #calling function that filters data by specified date ranges
        filter_type = self.request.GET.get('filter_type')
        return self.filter_by_dates_range(filter_type)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # list all employyes hours
        employee_entries = self.get_queryset()
        context['employee_entries'] = employee_entries

        # Sum hours per employee
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

#Add new employee form, visible to logged in users, who have appropriate permissions
class AddEmployeeView(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    login_url = '/login/'
    permission_required = 'timetracking_app.add_person'

    #define the form
    model = Person
    fields = ['username', 'first_name', 'last_name', 'email', 'password', 'department']
    template_name = 'add_employee.html'
    success_url = reverse_lazy('employees-hours')

    #create user and save the details to the db
    def form_valid(self, form):
        password = form.cleaned_data['password']
        response = super().form_valid(form)
        self.object.set_password(password)
        self.object.save()
        return response


#delete hours view (for logged in users with permissions)
class DeleteHoursView(LoginRequiredMixin, PermissionRequiredMixin, DeleteView):
    login_url = '/login/'
    permission_required = 'timetracking_app.delete_hours'

    model = LoggedHours
    success_url = reverse_lazy('list-all-hours')
    template_name ='loggedhours_confirm_delete.html'


#Edit own hours
class EditHoursView(LoginRequiredMixin, UpdateView):
    login_url = '/login/'
    model = LoggedHours
    fields = ['date', 'hour', 'sales_channel', 'department']
    template_name = 'loggedhours_update_form.html'
    success_url = reverse_lazy('list-all-hours')


#Edit employee form
class EditEmployeeView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    login_url = '/login/'
    permission_required = 'timetracking_app.edit_employee'

    model = Person
    fields = ['username', 'first_name', 'last_name', 'email', 'password', 'department']
    template_name = 'person_update_form.html'
    success_url = reverse_lazy('employees-hours')


class SearchEmployeeView(LoginRequiredMixin, PermissionRequiredMixin, FormView):
    login_url = '/login/'
    permission_required = 'timetracking_app.view_person'
    form_class = SearchEmployeeForm
    template_name = 'search_employee.html'
    success_url = reverse_lazy('employee-detail')

    def form_valid(self, form):
        form = form
        email = form.cleaned_data.get('email')
        first_name = form.cleaned_data.get('first_name')
        last_name = form.cleaned_data.get('last_name')
        department = form.cleaned_data.get('department')
        employees = Person.objects.all()
        if email:
            employees = employees.filter(email=email)
        if first_name:
            employees = employees.filter(first_name__icontains=first_name)
        if last_name:
            employees = employees.filter(last_name__icontains=last_name)
        if department:
            employees = employees.filter(department__department_name__icontains=department)

        return render(self.request, 'employee_detail.html', {'employees': employees})


#Deactivate the employee (for logged in users with specified permissions)
class DeactivateEmployeeView(LoginRequiredMixin, PermissionRequiredMixin, View):
    login_url = '/login/'
    permission_required = 'timetracking_app.delete_person'

    model = Person
    success_url = reverse_lazy('list-employees')
    template_name ='deactivate_employee.html'

    def get(self, request, pk):
        employee = Person.objects.get(pk=pk)
        return render(request, self.template_name, {'employee': employee})

    def post(self, request, pk):
        employee = Person.objects.get(pk=pk)
        employee.is_active = False
        employee.save()
        return redirect(self.success_url)


class ResetPasswordView(FormView):
    login_url = reverse_lazy('login-page')
    model = Person
    template_name = 'form.html'
    context_object_name = 'user'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('home-page')


    def send_password_reset_email(self, user):
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        password_reset_url = reverse('password_reset_confirm', kwargs={'uidb64': uid, 'token': token})
        password_reset_link = f"{settings.SITE_URL}{password_reset_url}"

        subject = 'Set your password'
        message = render_to_string('registration/set_password_email.html', {
            'user': user,
            'password_reset_link': password_reset_link,
        })
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])

        user.is_active = True
        user.save()

class PasswordChangeView(LoginRequiredMixin, FormView):
    login_url = '/login/'
    template_name = 'password_change.html'
    model = Person
    context_object_name = 'user'
    form_class = ResetPasswordForm
    success_url = reverse_lazy('home-page')


class PasswordChangeDoneView(LoginRequiredMixin, View):
    login_url = '/login/'
    template_name = 'password_change_done.html'


class EmployeeDetailView(LoginRequiredMixin, PermissionRequiredMixin, DetailView):
    login_url = '/login/'
    model = Person
    permission_required = 'timetracking_app.change_person'
    template_name = 'employee_full_details.html'
    context_object_name = 'employee'


    def get_object(self):
        pk = self.kwargs.get('pk')
        return get_object_or_404(Person, pk=pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Filter logged hours by employee id
        context['employee_entries'] = LoggedHours.objects.filter(employee=self.get_object())
        return context


