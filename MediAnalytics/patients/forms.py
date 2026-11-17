import re
from django import forms
from .models import Patient


class PatientForm(forms.ModelForm):
    """
    Form for creating and updating Patient records with Bootstrap 5 styling and validation.
    """
    class Meta:
        model = Patient
        exclude = ['patient_id', 'created_by', 'registration_date', 'created_at', 'updated_at']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'age': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Age (0-150)', 'min': '0', 'max': '150'}),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890 or 10-digit number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Residential address'}),
            'emergency_contact': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Contact Name & Phone'}),
            'notes': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Medical background or extra notes'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        phone_regex = r'^\+?[0-9]{10,15}$'
        if not re.match(phone_regex, phone):
            raise forms.ValidationError("Please enter a valid phone number (10 to 15 digits, optional '+' prefix).")
        return phone

    def clean_age(self):
        age = self.cleaned_data.get('age')
        if age is not None and (age < 0 or age > 150):
            raise forms.ValidationError("Age must be between 0 and 150 years.")
        return age

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if email:
            # Check duplicate email excluding current instance
            qs = Patient.objects.filter(email__iexact=email)
            if self.instance and self.instance.pk:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise forms.ValidationError("A patient with this email address already exists.")
        return email
