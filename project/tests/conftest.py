import random

import pytest
from django.shortcuts import get_object_or_404
from django.test import Client
from django.utils import timezone

from timetracking_app.models import Person, Department, SalesChannel, LoggedHours



@pytest.fixture
def client():
    return Client()

@pytest.fixture
def create_test_user(create_test_department):
    username = 'test_user'
    first_name = 'test_user'
    last_name = 'test_user'
    email = 'test_user@example.com'
    password = 'test_user'
    department = create_test_department
    test_user = Person.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name,
                                           department=department)
    test_user.set_password(password)
    test_user.save()
    return test_user

@pytest.fixture
def create_test_channel():
    sales_channel = SalesChannel.objects.create(channel_name='test_channel')
    return sales_channel

@pytest.fixture
def create_test_department():
    username = 'test_manager_user'
    first_name = 'test_manager_user'
    last_name = 'test_manager_user'
    email = 'test_manager_user@example.com'
    password = 'test_manager_user'
    test_manager_user = Person.objects.create_user(username=username, email=email, first_name=first_name, last_name=last_name)
    test_manager_user.set_password(password)
    test_manager_user.save()

    department = Department.objects.create(department_name='test_department', manager=test_manager_user)
    return department

@pytest.fixture
def add_test_hours(create_test_user, create_test_channel, create_test_department):
    user = create_test_user
    date = timezone.now().date()
    department = create_test_department
    sales_channel = create_test_channel
    hour = random.randint(1, 8)
    added_hours = LoggedHours.objects.create(date=date, hour=hour, employee=user, sales_channel=sales_channel, department=department)
    return added_hours


