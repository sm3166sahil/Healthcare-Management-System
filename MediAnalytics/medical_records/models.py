from django.db import models
from django.contrib.auth.models import User
from patients.models import Patient


class MedicalRecord(models.Model):
    """
    Diagnostic, lab test, and biometric test record linked to a Patient.
    """
    OUTCOME_CHOICES = [
        ('Positive', 'Positive'),
        ('Negative', 'Negative'),
        ('Inconclusive', 'Inconclusive'),
    ]

    record_id = models.CharField(max_length=20, unique=True, editable=False)
    patient = models.ForeignKey(Patient, on_delete=models.CASCADE, related_name='medical_records')
    test_date = models.DateField()
    heart_rate = models.FloatField(null=True, blank=True, help_text='bpm')
    bp_systolic = models.FloatField(null=True, blank=True, help_text='mmHg')
    bp_diastolic = models.FloatField(null=True, blank=True, help_text='mmHg')
    cholesterol = models.FloatField(null=True, blank=True, help_text='mg/dL')
    blood_glucose = models.FloatField(null=True, blank=True, help_text='mg/dL')
    ck_mb = models.FloatField(null=True, blank=True, help_text='ng/mL')
    troponin = models.FloatField(null=True, blank=True, help_text='ng/mL')
    outcome = models.CharField(max_length=50, choices=OUTCOME_CHOICES, blank=True)
    notes = models.TextField(blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='records_created')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-test_date', '-created_at']
        verbose_name = 'Medical Record'
        verbose_name_plural = 'Medical Records'

    def __str__(self):
        return f'{self.record_id} - {self.patient.name}'

    @property
    def bp(self):
        if self.bp_systolic is not None and self.bp_diastolic is not None:
            return f"{int(self.bp_systolic)}/{int(self.bp_diastolic)}"
        return "N/A"

    @property
    def blood_pressure(self):
        return self.bp

    @property
    def glucose(self):
        return self.blood_glucose

    @property
    def diagnosis(self):
        return self.outcome

    @property
    def remarks(self):
        return self.notes

    def save(self, *args, **kwargs):
        if not self.record_id:
            last_record = MedicalRecord.objects.order_by('-id').first()
            next_num = (last_record.id + 1) if (last_record and last_record.id) else 1
            candidate_id = f'MR-{next_num:05d}'
            while MedicalRecord.objects.filter(record_id=candidate_id).exists():
                next_num += 1
                candidate_id = f'MR-{next_num:05d}'
            self.record_id = candidate_id
        super().save(*args, **kwargs)
