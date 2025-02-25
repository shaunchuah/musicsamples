import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.test import Client
from django.urls import reverse

from app.choices import FileCategoryChoices, StudyNameChoices
from app.models import DataStore

User = get_user_model()


@pytest.mark.django_db
def test_datastore_list_view_get_context_data():
    # Create test data for DataStore, adjust field values as needed.
    ds1 = DataStore.objects.create(
        study_name=StudyNameChoices.GIDAMPS.value,
        category=FileCategoryChoices.ENDOSCOPY_VIDEOS.value,  # must be a valid choice for FileCategoryChoices
        file_type="mov",
        original_file_name="testfile1.mov",
        formatted_file_name="Study1_testfile1_abcd123.mov",
    )

    ds2 = DataStore.objects.create(
        study_name=StudyNameChoices.MUSIC.value,  # must be a valid choice for StudyNameChoices
        category=FileCategoryChoices.UNCATEGORISED.value,  # must be a valid choice for FileCategoryChoices
        file_type="txt",
        original_file_name="testfile2.txt",
        formatted_file_name="Study2_testfile2_efgh456.txt",
    )
    # Verify objects were created
    assert DataStore.objects.count() == 2

    # Create a test user and assign permissions

    user = User.objects.create_user(email="testuser@test.com", password="testpass")
    content_type = ContentType.objects.get_for_model(DataStore)
    permission = Permission.objects.get(content_type=content_type, codename="view_datastore")
    user.user_permissions.add(permission)

    # Create client and log in
    client = Client()
    client.login(username="testuser@test.com", password="testpass")

    response = client.get(reverse("datastore_list"))

    # Check that the response status is 200 OK.
    assert response.status_code == 200

    # Verify the context includes 'datastores' and that it matches the test instances.
    datastores = response.context["datastores"]
    retrieved_ids = {ds.pk for ds in datastores}
    expected_ids = {ds1.pk, ds2.pk}
    assert retrieved_ids == expected_ids

    # Verify the template used
    assert "datastore/datastore_list.html" in [t.name for t in response.templates]
