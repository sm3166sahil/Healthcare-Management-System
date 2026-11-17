from django.contrib import admin
from .models import Patient


@admin.register(Patient)
class PatientAdmin(admin.ModelAdmin):
    list_display = ('patient_id', 'name', 'gender', 'age', 'phone', 'email', 'registration_date', 'created_by')
    list_filter = ('gender', 'registration_date', 'created_at')
    search_fields = ('patient_id', 'name', 'phone', 'email', 'emergency_contact')
    readonly_fields = ('patient_id', 'registration_date', 'created_at', 'updated_at')
    ordering = ('-created_at',)
