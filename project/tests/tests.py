import pytest
from django.db.models import Sum
from django.shortcuts import resolve_url
from django.test import TestCase, Client
from django.urls import reverse
from timetracking_app.models import LoggedHours



@pytest.mark.django_db
def test_HomePageView(client, create_test_user):
    response = client.get(reverse('home-page'))
    assert response.status_code == 302
    # Check if the redirection URL is the login page
    assert response.url == '/login/?redirect_to=/home/'
    test_user = create_test_user
    test_user_authenticated = client.login(username=test_user.username, password='test_user')
    assert test_user_authenticated is True
    response = client.get(reverse('home-page'))
    assert response.status_code == 200


@pytest.mark.django_db
def test_LoginView(client, create_test_user):
    response = client.get('/login/')
    assert response.status_code == 200
    test_user = create_test_user
    test_user_authenticated = client.login(username=test_user.username, password='test_user')
    assert test_user_authenticated is True


@pytest.mark.django_db
def test_LoginView_redirect(client, create_test_user):
    response = client.get('/home/')  # Assuming '/homepage/' is the URL to be redirected to after login
    assert response.status_code == 302  # Ensure that the request is redirected (status code 302)

    # Perform login
    test_user = create_test_user
    login_data = {'username': test_user.username, 'password': 'test_user'}
    response = client.post(reverse('login-page'), login_data, follow=True)
    assert response.status_code == 200  # Ensure that the login was successful and redirected to the homepage
    response = client.get(reverse('home-page'))
    assert response.url == '/login/?redirect_to=/home/'

@pytest.mark.django_db
def test_LogoutView(client, create_test_user):
    test_user = create_test_user
    test_user_authenticated = client.login(username=test_user.username, password='test_user')
    assert test_user_authenticated is True
    test_user_authenticated = client.logout()
    assert test_user_authenticated is None
    response = client.get(reverse('logout-page'))
    assert response.status_code == 200

@pytest.mark.django_db
def test_AddHoursView(client, create_test_user, add_test_hours):
    response = client.get('/add_hours/')
    assert response.status_code == 302

    test_user = create_test_user
    login_data = {'username': test_user.username, 'password': 'test_user'}
    response = client.post(reverse('add-hours'), login_data, follow=True)
    assert response.status_code == 200

    # Fetch all logged hours from the database
    hours_in_db = LoggedHours.objects.all()
    # Calculate the total hours before adding test hours
    hours_in_db_before = hours_in_db.aggregate(Sum('hour'))['hour__sum']
    # Add the test hours to the database
    hours = add_test_hours
    # Calculate the total hours after adding test hours
    hours_in_db_after = hours_in_db.aggregate(Sum('hour'))['hour__sum'] + hours.hour
    # Assert that the total hours in the database increased by the added test hours
    assert hours_in_db_after == hours_in_db_before + hours.hour


@pytest.mark.django_db
def test_own_hours_context_check(client, create_test_user):
    pass


@pytest.mark.django_db
def test_own_hours_authentication_redirect(client, create_test_user, add_test_hours):
    response = client.get('/list_all_hours/')
    assert response.status_code == 302  # Ensure that the request is redirected after unsuccessful(status code 302)

    # Perform login
    test_user = create_test_user
    login_data = {'username': test_user.username, 'password': 'test_user'}
    response = client.post(reverse('login-page'), login_data, follow=True)
    assert response.status_code == 200  # Ensure that the login was successful and redirected to the homepage

    logged_hours = add_test_hours
    response = client.get(reverse('list-all-hours'))

    assert response.context['employee'] == logged_hours.employee
    assert response.context['date'] == logged_hours.date
    assert response.context['sales_channel'] == logged_hours.sales_channel
    assert response.context['department'] == logged_hours.department
    assert response.context['hour'] == logged_hours.hour


