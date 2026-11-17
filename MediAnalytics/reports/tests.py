from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from reports.models import GeneratedReport
from datasets.models import UploadedDataset


class ReportTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='tester', password='password123')
        self.client.login(username='tester', password='password123')
        self.dataset = UploadedDataset.objects.create(
            title='Test Dataset',
            file='uploaded_datasets/sample.csv',
            row_count=100,
            column_count=5
        )

    def test_report_list_accessible(self):
        response = self.client.get(reverse('reports:list'))
        self.assertEqual(response.status_code, 200)

    def test_report_generate_view_get(self):
        response = self.client.get(reverse('reports:generate'))
        self.assertEqual(response.status_code, 200)
