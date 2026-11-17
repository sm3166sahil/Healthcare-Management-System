from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile


class UserRegistrationForm(UserCreationForm):
    """
    Form for registering a new user with optional role selection and personal details.
    """
    first_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        initial='analyst',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department (e.g., Cardiology, Data Science)'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            if 'class' not in field.widget.attrs:
                field.widget.attrs['class'] = 'form-control'
            if not field.widget.attrs.get('placeholder'):
                field.widget.attrs['placeholder'] = field.label

    def save(self, commit=True):
        user = super().save(commit=commit)
        role = self.cleaned_data.get('role', 'analyst')
        department = self.cleaned_data.get('department', '')
        phone = self.cleaned_data.get('phone', '')

        if commit:
            profile, _ = UserProfile.objects.get_or_create(user=user)
            profile.role = role
            profile.department = department
            profile.phone = phone
            profile.save()
        return user


class UserLoginForm(AuthenticationForm):
    """
    Custom authentication form styled with Bootstrap 5.
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter username',
            'autocomplete': 'username',
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter password',
            'autocomplete': 'current-password',
        })


class UserProfileForm(forms.ModelForm):
    """
    Form for updating UserProfile details.
    """
    class Meta:
        model = UserProfile
        fields = ['role', 'phone', 'department']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'department': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Department'}),
        }


class UserUpdateForm(forms.ModelForm):
    """
    Form for updating the basic User details (first name, last name, email).
    """
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
