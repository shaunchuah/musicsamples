import pytest
from django.test import RequestFactory
from ..models import Sample
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from .. import views
from django.contrib.auth.models import AnonymousUser
from mixer.backend.django import mixer
from pytest_django.asserts import assertTemplateUsed

User = get_user_model()

pytestmark = pytest.mark.django_db

class TestHomePage:
    def test_home_page_authenticated(self):
        path = reverse('home')
        request = RequestFactory().get(path)
        User = get_user_model()
        request.user = mixer.blend(User) 
        response = views.index(request)
        assert response.status_code == 200, 'Should show homepage when logged in.'

    def test_home_page_unauthorized(self):
        path = reverse('home')
        request = RequestFactory().get(path)
        request.user = AnonymousUser()
        response = views.index(request)
        assert 'login' in response.url, 'Should not show homepage and redirect to login.'

def test_analytics_unauthorized(client):
    path = reverse('analytics')
    response = client.get(path)
    assert 'login' in response.url, 'Should not show analytics to unauthenticated users.'

def test_analytics_authorized(admin_client):
    path = reverse('analytics')
    response = admin_client.get(path)
    assert response.status_code == 200, 'Show analytics to authorised users.'

def test_gid_overview_page(admin_client):
    path = reverse('gid_overview')
    response = admin_client.get(path)
    assert response.status_code == 200, 'Show GID overview page to authorised users.'

def test_reference_page(admin_client):
    path = reverse('reference')
    response = admin_client.get(path)
    assertTemplateUsed(response, 'reference.html')

def test_account_page_unauthorized(client):
    path = reverse('account')
    response = client.get(path)
    assert 'login' in response.url, 'Should not show account page to unauthenticated users.'

def test_account_page(admin_client):
    path = reverse('account')
    response = admin_client.get(path)
    assertTemplateUsed(response, 'account.html'), 'Check that account page is accessible through url and returns the account.html template.'

def test_used_samples_page(admin_client):
    path = reverse('used_samples')
    response = admin_client.get(path)
    assertTemplateUsed(response, 'used_samples.html'), 'Check that used samples page is accessible through url and returns the used_samples.html template.'

def test_barcode_main_page(admin_client):
    path = reverse('barcode')
    response = admin_client.get(path)
    assertTemplateUsed(response, 'barcode.html'), 'Check that used samples page is accessible through url and returns the used_samples.html template.'

def test_barcode_samples_used_page(admin_client):
    path = reverse('barcode_samples_used')
    response = admin_client.get(path)
    assertTemplateUsed(response, 'barcode-markused.html'), 'Check that used samples page is accessible through url and returns the used_samples.html template.'
