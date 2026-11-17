from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator, RegexValidator


class Patient(models.Model):
    """
    Patient demographics and medical record registration entity.
    """
    GENDER_CHOICES = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Other', 'Other'),
    ]

    phone_regex = RegexValidator(
        regex=r'^\+?[0-9]{10,15}$',
        message="Phone number must be in the format '+1234567890' or '1234567890' (10 to 15 digits)."
    )

    patient_id = models.CharField(max_length=20, unique=True, editable=False)
    name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    age = models.PositiveIntegerField(
        validators=[MinValueValidator(0), MaxValueValidator(150)]
    )
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone = models.CharField(max_length=20, validators=[phone_regex])
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    registration_date = models.DateField(auto_now_add=True)
    emergency_contact = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='patients_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Patient'
        verbose_name_plural = 'Patients'

    def __str__(self):
        return f'{self.patient_id} - {self.name}'

    def get_full_name(self):
        return self.name

    @property
    def dob(self):
        return self.date_of_birth

    @property
    def medical_history(self):
        return self.notes

    @property
    def blood_group(self):
        return getattr(self, '_blood_group', 'N/A')

    def save(self, *args, **kwargs):
        if not self.patient_id:
            last_patient = Patient.objects.order_by('-id').first()
            next_num = (last_patient.id + 1) if (last_patient and last_patient.id) else 1
            candidate_id = f'PAT-{next_num:04d}'
            while Patient.objects.filter(patient_id=candidate_id).exists():
                next_num += 1
                candidate_id = f'PAT-{next_num:04d}'
            self.patient_id = candidate_id
        super().save(*args, **kwargs)
