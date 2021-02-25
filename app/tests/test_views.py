import pytest
from django.test import RequestFactory
from ..models import Sample
from django.urls import reverse, resolve
from django.contrib.auth import get_user_model
from .. import views
from django.contrib.auth.models import AnonymousUser
from mixer.backend.django import mixer
from pytest_django.asserts import assertTemplateUsed

pytestmark = pytest.mark.django_db

@pytest.fixture
def test_password():
   return 'strong-test-pass'

@pytest.fixture
def create_user(db, django_user_model, test_password):
   def make_user(**kwargs):
       kwargs['password'] = test_password
       if 'username' not in kwargs:
           kwargs['username'] = 'testuser1'
       return django_user_model.objects.create_user(**kwargs)
   return make_user

@pytest.fixture
def auto_login_user(db, client, create_user, test_password):
   def make_auto_login(user=None):
       if user is None:
           user = create_user()
       client.login(username=user.username, password=test_password)
       return client, user
   return make_auto_login

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

def test_archive_page(admin_client):
    path = reverse('archive')
    response = admin_client.get(path)
    assert response.status_code == 200, 'Check archive view and url is working. (Soft deleted samples.)'
    assertTemplateUsed(response, 'archive.html')

def test_error_404_template(admin_client):
    path = ('/doesnotexist.html')
    response = admin_client.get(path)
    assert response.status_code == 404, 'Check 404 is working.'

########## TESTS FOR SAMPLES #############

def test_add_sample_page(auto_login_user):
    client, user = auto_login_user()
    path = reverse('new_sample')
    response = client.get(path)
    assert response.status_code == 200, 'Should return add new sample page via GET request.'
    response = client.post(path)
    assert response.status_code == 200, 'Should return add new sample page via POST request without form data.'

def test_sample_detail_page(auto_login_user):
    client, user = auto_login_user()
    sample = mixer.blend('app.sample', musicsampleid='TEST001')
    path = reverse('sample_detail', kwargs={'pk':1})
    response = client.get(path)
    assert response.context['sample'].musicsampleid == 'TEST001', 'Should create sample instance with ID TEST001 and be able to retrieve sample detail view corresponding to this objects.'

def test_sample_detail_processing_datetime_logic(auto_login_user):
    client, user = auto_login_user()
    sample = mixer.blend('app.sample', sample_datetime='2020-01-01T13:20:30', processing_datetime='2020-01-01T13:25:30')
    path = reverse('sample_detail', kwargs={'pk':1})
    response = client.get(path)
    assert response.context['processing_time'] == 5, 'Should test that processing_time calculation is correct given sampling datetime and processing datetime.'

def test_sample_detail_linkage_to_redcap_db(auto_login_user):
    client, user = auto_login_user()
    sample = mixer.blend('app.sample', patientid='GID-312-P')
    path = reverse('sample_detail', kwargs={'pk':1})
    response = client.get(path)
    assert response.context['gid_id'] == 312, 'Should return study ID number integer value.'

def test_sample_edit_page(auto_login_user):
    client, user = auto_login_user()
    sample = mixer.blend('app.sample', musicsampleid='TEST002')
    sample2 = mixer.blend('app.sample', musicsampleid='TEST003')
    path = reverse('sample_edit', kwargs={'pk':2})
    response = client.get(path)
    assertTemplateUsed(response, 'sample-edit.html')
    assert response.context['form'].initial['musicsampleid'] == 'TEST003', 'Should create two separate sample instances and return the second one.'
