import pytest
from django.test import RequestFactory
from ..models import Sample
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from .. import views
from django.contrib.auth.models import AnonymousUser
from mixer.backend.django import mixer

User = get_user_model()

pytestmark = pytest.mark.django_db

def test_home_page_authenticated():
    path = reverse('home')
    request = RequestFactory().get(path)
    User = get_user_model()
    request.user = mixer.blend(User) 
    response = views.index(request)
    assert response.status_code == 200, 'Should show homepage when logged in.'

def test_home_page_as_anonymouse_user():
    path = reverse('home')
    request = RequestFactory().get(path)
    request.user = AnonymousUser()
    response = views.index(request)
    assert 'login' in response.url, 'Should not show homepage and redirect to login'

@pytest.fixture
def api_client():
   from rest_framework.test import APIClient
   return APIClient()


def test_unauthorized_request(api_client):
   response = api_client.get('/api/samples')
   assert response.status_code == 301


