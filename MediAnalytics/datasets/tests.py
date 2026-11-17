from django.test import TestCase
from django.contrib.auth.models import User
from .models import UploadedDataset


class DatasetModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='analyst1', password='password123')
        self.dataset = UploadedDataset.objects.create(
            title='Sample Dataset',
            description='Test cardiac data',
            file_size=2048,
            row_count=100,
            column_count=5,
            uploaded_by=self.user
        )

    def test_dataset_str(self):
        """Test dataset string representation."""
        self.assertEqual(str(self.dataset), 'Sample Dataset')

    def test_file_size_display(self):
        """Test human readable file size."""
        self.assertEqual(self.dataset.file_size_display, '2.0 KB')
