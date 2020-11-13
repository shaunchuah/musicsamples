from django.test import TestCase, SimpleTestCase, Client
from ..models import Sample
from django.urls import reverse, resolve
from ..views import *
import datetime
import pytz
from django.contrib.auth import get_user_model

class TestViews(TestCase):

    def setUp(self):
        Sample.objects.create(
            musicsampleid = 'TEST001',
            patientid = 'TEST001',
            sample_location = 'test location',
            sample_type = 'test sample type',
            sample_datetime = datetime.datetime.now(tz=pytz.utc),
            created_by = 'test_user',
            last_modified_by = 'test_user',
        )
        User = get_user_model()
        test_user = User.objects.create_user('temporary', 'temporary@gamil.com', 'temporary')
        self.client.login(username='temporary', password='temporary')


    def test_sample_detail_GET(self):        
        response = self.client.get(reverse('sample_detail', kwargs={'pk':1}))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'sample-detail.html')
    
    def test_sample_detail_404_GET(self):
        response = self.client.get(reverse('sample_detail', kwargs={'pk':100}))
        self.assertEquals(response.status_code, 404)

    def test_sample_edit_GET(self):        
        response = self.client.get(reverse('sample_edit', kwargs={'pk':1}))
        self.assertEquals(response.status_code, 200)
        self.assertTemplateUsed(response, 'sample-edit.html')
