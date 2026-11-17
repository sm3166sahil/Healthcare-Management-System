from django import forms
from .models import MedicalRecord


class MedicalRecordForm(forms.ModelForm):
    """
    Form for creating and editing clinical medical records with Bootstrap 5 styling.
    """
    class Meta:
        model = MedicalRecord
        exclude = ['record_id', 'created_by', 'created_at', 'updated_at']
        widgets = {
            'patient': forms.Select(attrs={'class': 'form-select'}),
            'test_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'heart_rate': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Heart Rate (bpm)'}),
            'bp_systolic': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Systolic BP (mmHg)'}),
            'bp_diastolic': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Diastolic BP (mmHg)'}),
            'cholesterol': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Total Cholesterol (mg/dL)'}),
            'blood_glucose': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'placeholder': 'Blood Glucose (mg/dL)'}),
            'ck_mb': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01', 'placeholder': 'CK-MB (ng/mL)'}),
            'troponin': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.001', 'placeholder': 'Troponin (ng/mL)'}),
            'outcome': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Clinical observations or diagnosis summary'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        bp_sys = cleaned_data.get('bp_systolic')
        bp_dia = cleaned_data.get('bp_diastolic')

        if bp_sys is not None and bp_dia is not None:
            if bp_dia >= bp_sys:
                self.add_error('bp_diastolic', "Diastolic blood pressure should typically be lower than systolic blood pressure.")

        return cleaned_data
