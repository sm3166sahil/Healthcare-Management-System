from django.test import TestCase
from django.contrib.auth.models import User
from .models import Patient


class PatientModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='doctor', password='password123')
        self.patient = Patient.objects.create(
            name='Alice Smith',
            age=34,
            gender='Female',
            phone='+1234567890',
            email='alice@example.com',
            created_by=self.user
        )

    def test_auto_generated_patient_id(self):
        """Test that patient_id is automatically generated in format PAT-XXXX."""
        self.assertTrue(self.patient.patient_id.startswith('PAT-'))
        self.assertEqual(len(self.patient.patient_id), 8)

    def test_patient_str(self):
        """Test the string representation of Patient."""
        expected = f"{self.patient.patient_id} - Alice Smith"
        self.assertEqual(str(self.patient), expected)
