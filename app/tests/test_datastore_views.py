from datetime import date

import pytest
from django.test import Client
from django.urls import reverse

from app.choices import FileCategoryChoices, StudyNameChoices
from app.models import DataStore
from app.views.datastore_views import DataStoreListView


def test_datastore_list_view_attributes():
    assert DataStoreListView.model == DataStore
    assert DataStoreListView.template_name == "datastore/datastore_list.html"
    assert DataStoreListView.context_object_name == "datastores"


@pytest.mark.django_db
def test_datastore_list_view_get_context_data():
    # Create test data for DataStore, adjust field values as needed.
    ds1 = DataStore.objects.create(
        study_name=StudyNameChoices.GIDAMPS.value,
        file_date=date.today(),
        category=FileCategoryChoices.ENDOSCOPY_VIDEOS.value,  # must be a valid choice for FileCategoryChoices
        file_type="mov",
        original_file_name="testfile1.mov",
        formatted_file_name="Study1_testfile1_abcd123.mov",
    )

    ds2 = DataStore.objects.create(
        study_name=StudyNameChoices.MUSIC.value,  # must be a valid choice for StudyNameChoices
        file_date=date.today(),
        category=FileCategoryChoices.UNCATEGORISED.value,  # must be a valid choice for FileCategoryChoices
        file_type="txt",
        original_file_name="testfile2.txt",
        formatted_file_name="Study2_testfile2_efgh456.txt",
    )
    # Verify objects were created
    assert DataStore.objects.count() == 2

    client = Client()
    response = client.get(reverse("datastore_list"))

    # Check that the response status is 200 OK.
    assert response.status_code == 200

    # Verify the context includes 'datastores' and that it matches the test instances.
    datastores = response.context_data.get("datastores")
    retrieved_ids = {ds.pk for ds in datastores}
    expected_ids = {ds1.pk, ds2.pk}
    assert retrieved_ids == expected_ids

    # Verify the template used
    assert "datastore/datastore_list.html" in [t.name for t in response.templates]
