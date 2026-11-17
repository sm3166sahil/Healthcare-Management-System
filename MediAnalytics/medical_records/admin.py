from django.contrib import admin
from .models import MedicalRecord


@admin.register(MedicalRecord)
class MedicalRecordAdmin(admin.ModelAdmin):
    list_display = (
        'record_id',
        'patient',
        'test_date',
        'heart_rate',
        'bp_systolic',
        'bp_diastolic',
        'cholesterol',
        'blood_glucose',
        'outcome',
        'created_by'
    )
    list_filter = ('outcome', 'test_date', 'created_at')
    search_fields = ('record_id', 'patient__name', 'patient__patient_id', 'notes')
    readonly_fields = ('record_id', 'created_at', 'updated_at')
    ordering = ('-test_date', '-created_at')
