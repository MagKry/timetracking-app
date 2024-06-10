"""
URL configuration for project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from .views import (HomePageView, LoginView, AddHoursView, ViewOwnHoursView, ViewDepartmentHoursView,
                    ViewEmployeesHoursView, AddEmployeeView, LogoutView, ListAllHoursView, HoursThisWeekView,
                    HoursThisMonthView,
                    HoursThisYearView, HoursPerChannelView, DeleteHoursView, EditHoursView, EditEmployeeView,
                    ListEmployeesView, DeactivateEmployeeView)

urlpatterns = [
    path('home/', HomePageView.as_view(), name='home-page'),
    path('login/', LoginView.as_view(), name='login-page'),
    path('logout/', LogoutView.as_view(), name='logout-page'),
    path('add_hours/', AddHoursView.as_view(), name='add-hours'),
    path('view_hours/', ViewOwnHoursView.as_view(), name='view-hours'),
    path('list_all_hours/', ListAllHoursView.as_view(), name='list-all-hours'),
    path('hours_this_week/', HoursThisWeekView.as_view(), name='hours-this-week'),
    path('hours_this_month/', HoursThisMonthView.as_view(), name='hours-this-month'),
    path('hours_this_year/', HoursThisYearView.as_view(), name='hours-this-year'),
    path('channel_hours/', HoursPerChannelView.as_view(), name='hours-per-channel'),
    path('department_hours/', ViewDepartmentHoursView.as_view(), name='department-hours'),
    path('employees_hours/', ViewEmployeesHoursView.as_view(), name='employees-hours'),
    path('add_employee/', AddEmployeeView.as_view(), name='add-employee'),
    path('delete_hours/<int:pk>/', DeleteHoursView.as_view(), name='delete-hours'),
    path('edit_hours/<int:pk>/', EditHoursView.as_view(), name='edit-hours'),
    path('edit_employee/<int:pk>/', EditEmployeeView.as_view(), name='edit-employee'),
    path('list_employees/', ListEmployeesView.as_view(), name='list-employees'),
    path('deactivate_employee/<int:pk>', DeactivateEmployeeView.as_view(), name='deactivate-employee'),

]
