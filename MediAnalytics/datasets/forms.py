import os
from django import forms
from .models import UploadedDataset


class DatasetUploadForm(forms.ModelForm):
    """
    Form for uploading healthcare CSV datasets with validation.
    """
    class Meta:
        model = UploadedDataset
        fields = ['title', 'description', 'file']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Heart Disease Clinical Cohort 2026'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Dataset overview, source, variables, or cohort information'}),
            'file': forms.FileInput(attrs={'class': 'form-control', 'accept': '.csv'}),
        }

    def clean_file(self):
        uploaded_file = self.cleaned_data.get('file')
        if uploaded_file:
            # Check extension
            ext = os.path.splitext(uploaded_file.name)[1].lower()
            if ext != '.csv':
                raise forms.ValidationError("Invalid file format. Only CSV files (.csv) are supported.")

            # Check file size (10MB limit)
            max_size = 10 * 1024 * 1024
            if uploaded_file.size > max_size:
                raise forms.ValidationError("File size exceeds 10 MB limit. Please upload a smaller file.")

        return uploaded_file
