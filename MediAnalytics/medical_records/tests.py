from django.test import TestCase
from django.contrib.auth.models import User
from patients.models import Patient
from .models import MedicalRecord
import datetime


class MedicalRecordModelTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='doc2', password='password123')
        self.patient = Patient.objects.create(
            name='Bob Jones',
            age=45,
            gender='Male',
            phone='+1987654321',
            created_by=self.user
        )
        self.record = MedicalRecord.objects.create(
            patient=self.patient,
            test_date=datetime.date.today(),
            heart_rate=78.5,
            bp_systolic=120.0,
            bp_diastolic=80.0,
            outcome='Negative',
            created_by=self.user
        )

    def test_record_id_auto_generated(self):
        """Test that record_id starts with MR- and has 5 digits."""
        self.assertTrue(self.record.record_id.startswith('MR-'))
        self.assertEqual(len(self.record.record_id), 8)

    def test_record_str(self):
        """Test string representation of MedicalRecord."""
        expected = f"{self.record.record_id} - Bob Jones"
        self.assertEqual(str(self.record), expected)
