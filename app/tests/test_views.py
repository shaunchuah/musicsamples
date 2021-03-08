import pytest
import json
from django.test import RequestFactory
from ..models import Sample, Note
from django.urls import reverse
from django.contrib.auth import get_user_model
from .. import views
from django.contrib.auth.models import AnonymousUser
from mixer.backend.django import mixer
from pytest_django.asserts import assertTemplateUsed, assertRaisesMessage
from django.core.paginator import EmptyPage, PageNotAnInteger


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
def other_user(db, django_user_model):
    return django_user_model.objects.create(username='user2', password='user2')


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


def test_index_pagination_not_an_integer(auto_login_user):
    client, user = auto_login_user()
    number_of_samples = 10
    for i in range(number_of_samples):
        mixer.blend('app.Sample')
    path = reverse('home') + '?page=notaninteger'
    response = client.get(path)
    assertRaisesMessage(PageNotAnInteger, response)
    assert response.context['sample_list'].number == 1  # test page number returns as 1


def test_index_pagination_empty_page(auto_login_user):
    client, user = auto_login_user()
    path = reverse('home') + '?page=2'
    response = client.get(path)
    assertRaisesMessage(EmptyPage, response)


def test_index_pagination(auto_login_user):
    client, user = auto_login_user()
    number_of_samples = 60
    for i in range(number_of_samples):
        mixer.blend('app.Sample')
    path = reverse('home') + '?page=1'
    response = client.get(path)
    assert response.context['sample_list'].paginator.num_pages == 2


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
    assertTemplateUsed(response, 'samples/used_samples.html'), 'Check that used samples page is accessible through url and returns the used_samples.html template.'


def test_barcode_main_page(admin_client):
    path = reverse('barcode')
    response = admin_client.get(path)
    assertTemplateUsed(response, 'barcode.html'), 'Check that used samples page is accessible through url and returns the used_samples.html template.'


def test_barcode_samples_used_page(admin_client):
    path = reverse('barcode_samples_used')
    response = admin_client.get(path)
    assertTemplateUsed(response, 'barcode-markused.html'), 'Check that used samples page is accessible through url and returns the used_samples.html template.'


def test_archive_page(admin_client):
    path = reverse('sample_archive')
    response = admin_client.get(path)
    assert response.status_code == 200, 'Check archive view and url is working. (Soft deleted samples.)'
    assertTemplateUsed(response, 'samples/sample-archive.html')


def test_error_404_template(admin_client):
    path = ('/doesnotexist.html')
    response = admin_client.get(path)
    assert response.status_code == 404, 'Check 404 is working.'

# TESTS FOR SAMPLES #############


def test_add_sample_page(auto_login_user):
    client, user = auto_login_user()
    path = reverse('sample_add')
    response = client.get(path)
    assert response.status_code == 200, 'Should return add new sample page via GET request.'
    response = client.post(path)
    assert response.status_code == 200, 'Should return add new sample page via POST request without form data.'



def test_add_sample_post(auto_login_user):
    client, user = auto_login_user()
    path = reverse('sample_add')
    form_data = {
        'musicsampleid': 'test001',
        'patientid': 'patient001',
        'sample_location': 'location001',
        'sample_type': 'test_sample_type',
        'sample_datetime': '2020-01-01T13:20:30+00',
        'sample_comments': '',
        'processing_datetime': '',
        'sample_sublocation': '',
        'sample_volume': '',
        'sample_volume_units': '',
        'freeze_thaw_count': '',
        'haemolysis_reference': '',
        'biopsy_location': '',
        'biopsy_inflamed_status': ''
    }
    response = client.post(path, data=form_data, content_type="application/x-www-form-urlencoded")
    print(response)
    assert response.status_code == 302



def test_sample_detail_page(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.sample', musicsampleid='TEST001')
    path = reverse('sample_detail', kwargs={'pk': 1})
    response = client.get(path)
    assert response.context['sample'].musicsampleid == 'TEST001', 'Should create sample instance with ID TEST001 and be able to retrieve sample detail view corresponding to this objects.'


def test_sample_detail_processing_datetime_logic(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.sample', sample_datetime='2020-01-01T13:20:30+00', processing_datetime='2020-01-01T13:25:30+00')
    path = reverse('sample_detail', kwargs={'pk': 1})
    response = client.get(path)
    assert response.context['processing_time'] == 5, 'Should test that processing_time calculation is correct given sampling datetime and processing datetime.'


def test_sample_detail_linkage_to_redcap_db(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.sample', patientid='GID-312-P')
    path = reverse('sample_detail', kwargs={'pk': 1})
    response = client.get(path)
    assert response.context['gid_id'] == 312, 'Should return study ID number integer value.'


def test_sample_edit_page(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.sample', musicsampleid='TEST002')
    mixer.blend('app.sample', musicsampleid='TEST003')
    path = reverse('sample_edit', kwargs={'pk': 2})
    response = client.get(path)
    assertTemplateUsed(response, 'samples/sample-edit.html')
    assert response.context['form'].initial['musicsampleid'] == 'TEST003', 'Should create two separate sample instances and return the second one.'


def test_sample_search_page(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.sample', musicsampleid='TEST002')
    mixer.blend('app.sample', musicsampleid='TEST003')
    mixer.blend('app.sample', musicsampleid='NO')
    mixer.blend('app.sample', musicsampleid='DONOTRETURN')
    path = reverse('sample_search')
    response = client.get(path + '?q=TEST')
    assertTemplateUsed(response, 'index.html')
    assert 'TEST002' in response.context['sample_list'][0].musicsampleid, 'Should create a few objects, run a search and return 2 objects.'
    assert response.context['sample_list'].count() == 2, 'Should create a few objects, run a search and return 2 objects.'

    response = client.get(path)
    assert response.context['query_string'] == 'Null', 'Should return no objects with empty query string.'


def test_sample_checkout_page(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.sample', sample_location='location1')
    path = reverse('sample_checkout', kwargs={'pk': 1})

    # Get the sample checkout page and check template is correct
    response = client.get(path)
    assert response.context['form'].initial['sample_location'] == 'location1', 'Should retrieve an instance to checkout.'
    assertTemplateUsed(response, 'samples/sample-checkout.html')

    # Checkout the sample from location1 to location2
    response = client.post(path, data={'sample_location': 'location2'})
    assert Sample.objects.get(pk=1).sample_location == 'location2', 'Should checkout the sample location from location1 to location2.'
    assert Sample.objects.get(pk=1).last_modified_by == 'testuser1'
    assert response.status_code == 302


def test_sample_delete(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.sample', musicpatientid='TEST05')
    path = reverse('sample_delete', kwargs={'pk': 1})

    # Get the delete page first and check template is correct
    response = client.get(path)
    assertTemplateUsed(response, 'samples/sample-delete.html')

    # Make the delete request now and also pass a next_url to check redirection
    response = client.post(path + '?next=/samples/1/', data={'is_deleted': True})

    assert Sample.objects.get(pk=1).is_deleted is True, 'Should delete the created sample'
    assert response.url == '/samples/1/', 'Should redirect to passed url string after deleting sample.'


def test_sample_restore(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.sample', is_deleted=True)
    path = reverse('sample_restore', kwargs={'pk': 1})

    # Get the restore page and check template is correct
    response = client.get(path)
    assertTemplateUsed(response, 'samples/sample-restore.html')

    # Restore the sample
    response = client.post(path, data={'is_deleted': False})
    assert Sample.objects.get(pk=1).is_deleted is False, 'Should restore the deleted sample'
    assert response.url == '/'


def test_sample_fully_used(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.sample')
    path = reverse('sample_fully_used', kwargs={'pk': 1})

    # Get the delete page first and check template is correct
    response = client.get(path)
    assertTemplateUsed(response, 'samples/sample-fullyused.html')

    # Make the delete request now and also pass a next_url to check redirection
    response = client.post(path, data={'is_fully_used': True})

    assert Sample.objects.get(pk=1).is_fully_used is True, 'Should delete the created sample'
    assert response.status_code == 302


def test_sample_reactivate(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.sample', is_fully_used=True)
    path = reverse('reactivate_sample', kwargs={'pk': 1})

    # Get the restore page and check template is correct
    response = client.get(path)
    assertTemplateUsed(response, 'samples/sample-reactivate.html')

    # Restore the sample
    response = client.post(path, data={'is_fully_used': False})
    assert Sample.objects.get(pk=1).is_fully_used is False, 'Should restore the deleted sample'
    assert response.url == '/'

# TESTS FOR NOTES #############


def test_shared_notes_page(auto_login_user):
    client, user = auto_login_user()
    path = reverse('notes')
    response = client.get(path)
    assertTemplateUsed(response, 'notes/notes-main.html')


def test_personal_notes_page(auto_login_user):
    client, user = auto_login_user()
    path = reverse('note_personal')
    response = client.get(path)
    assertTemplateUsed(response, 'notes/notes-main.html')


def test_unable_to_get_other_user_private_note(auto_login_user, other_user):
    client, user = auto_login_user()
    mixer.blend('app.note', title='private', author=other_user, is_public=False)  # Private note
    assert Note.objects.count() == 1
    path = reverse('note_detail', kwargs={'pk': 1})
    response = client.get(path)
    assert response.status_code == 302


def test_get_own_private_note(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.note', title='my private note', is_public=False, author=user)  # Private note
    path = reverse('note_detail', kwargs={'pk': 1})
    response = client.get(path)
    assert response.context['note'].title == 'my private note'


def test_get_public_note(auto_login_user, other_user):
    client, user = auto_login_user()
    mixer.blend('app.note', title='Public Note', author=other_user, is_public=True)  # Other user note

    path = reverse('note_detail', kwargs={'pk': 1})
    response = client.get(path)
    assert response.context['note'].title == 'Public Note'
    assert response.context['note'].author.username == 'user2'


def test_get_note_with_tags(auto_login_user):
    client, user = auto_login_user()
    note = mixer.blend('app.note', title='tag test', is_public=True)
    note.tags.add('tag1')
    path = reverse('note_tags', kwargs={'slug': 'tag1'})
    response = client.get(path)
    assert response.context['notes'][0].title == 'tag test'


def test_get_note_by_author(auto_login_user, other_user):
    client, user = auto_login_user()
    mixer.blend('app.note', title='post by user2', author=other_user, is_public=True)  # Other user note

    path = reverse('note_authors', kwargs={'pk': other_user.id})
    response = client.get(path)
    assert response.context['notes'][0].title == 'post by user2'


def test_note_add(auto_login_user):
    client, user = auto_login_user()
    path = reverse('note_add')
    response = client.get(path)
    assertTemplateUsed('notes/notes-add.html')
    response = client.post(path)
    assert response.context['form'].is_bound is True


def test_note_edit(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.note', title='unedited title', author=user)
    path = reverse('note_edit', kwargs={'pk': 1})

    response = client.get(path)
    assert response.context['form'].initial['title'] == 'unedited title'


def test_missing_note_edit(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.note', title='unedited title', author=user)
    path = reverse('note_edit', kwargs={'pk': 1})

    response = client.post(path)
    assert response.context['form'].initial['title'] == 'unedited title'


def test_note_delete(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.note', title='soft delete this note', author=user)
    path = reverse('note_delete', kwargs={'pk': 1})
    response = client.get(path)
    assertTemplateUsed(response, 'notes/notes-delete.html')
    assert response.context['note'].title == 'soft delete this note'


def test_note_search(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.note', title='TEST002')
    mixer.blend('app.note', title='TEST003')
    mixer.blend('app.note', title='NO')
    mixer.blend('app.note', title='DONOTRETURN')
    path = reverse('note_search')
    response = client.get(path + '?q=TEST')
    assertTemplateUsed(response, 'notes/notes-main.html')
    assert 'TEST' in response.context['notes'][0].title, 'Should create a few objects, run a search and return 2 objects.'
    assert response.context['notes'].count() == 2, 'Should create a few objects, run a search and return 2 objects.'

    response = client.get(path)
    assert response.status_code == 302


# AUTOCOMPLETE TESTS


def test_autocomplete_locations(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.Sample', sample_location='location1')
    mixer.blend('app.Sample', sample_location='test2')
    path = reverse('autocomplete_locations')
    response = client.get(path + '?term=loc')
    assert 'location1' in json.loads(response.content)
    assert 'test2' not in json.loads(response.content)

    response_2 = client.get(path + '?term=te')
    assert 'location1' not in json.loads(response_2.content)
    assert 'test2' in json.loads(response_2.content)

    response_3 = client.get(path)
    assert 'location1' in json.loads(response_3.content)
    assert 'test2' in json.loads(response_3.content)


def test_autocomplete_patient_id(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('app.Sample', patientid='GID-123-P')
    mixer.blend('app.Sample', patientid='GID-003-P')
    path = reverse('autocomplete_patients')
    response = client.get(path + '?term=GID-123')
    assert 'GID-123-P' in json.loads(response.content)
    assert 'GID-003-P' not in json.loads(response.content)

    response_2 = client.get(path + '?term=003')
    assert 'GID-123-P' not in json.loads(response_2.content)
    assert 'GID-003-P' in json.loads(response_2.content)

    response_3 = client.get(path)
    assert 'GID-123-P' in json.loads(response_3.content)
    assert 'GID-003-P' in json.loads(response_3.content)


def test_autocomplete_tags(auto_login_user):
    client, user = auto_login_user()
    mixer.blend('taggit.Tag', name='tag1')
    mixer.blend('taggit.Tag', name='Test2')
    path = reverse('autocomplete_tags')
    response = client.get(path + '?term=ta')
    assert 'tag1' in json.loads(response.content)
    assert 'Test2' not in json.loads(response.content)

    response_2 = client.get(path + '?term=test')
    assert 'tag1' not in json.loads(response_2.content)
    assert 'Test2' in json.loads(response_2.content)

    response_3 = client.get(path)
    assert 'tag1' in json.loads(response_3.content)
    assert 'Test2' in json.loads(response_3.content)
