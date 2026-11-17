from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.http import JsonResponse

from .models import Patient
from .forms import PatientForm


def _user_can_delete_patient(user, patient):
    """Check if the user is authorized to delete the patient."""
    if user.is_superuser:
        return True
    if hasattr(user, 'profile') and user.profile.is_admin:
        return True
    if patient.created_by == user:
        return True
    return False


@login_required
def patient_list(request):
    """
    List all patients with search, filtering by gender/age, and pagination.
    """
    queryset = Patient.objects.all().order_by('-created_at')

    search_query = request.GET.get('q', '').strip()
    gender_filter = request.GET.get('gender', '').strip()
    min_age = request.GET.get('min_age', '').strip()
    max_age = request.GET.get('max_age', '').strip()

    if search_query:
        queryset = queryset.filter(
            Q(name__icontains=search_query) |
            Q(patient_id__icontains=search_query) |
            Q(phone__icontains=search_query) |
            Q(email__icontains=search_query)
        )

    if gender_filter:
        queryset = queryset.filter(gender=gender_filter)

    if min_age.isdigit():
        queryset = queryset.filter(age__gte=int(min_age))

    if max_age.isdigit():
        queryset = queryset.filter(age__lte=int(max_age))

    paginator = Paginator(queryset, 10)
    page_number = request.GET.get('page')
    try:
        patients = paginator.page(page_number)
    except PageNotAnInteger:
        patients = paginator.page(1)
    except EmptyPage:
        patients = paginator.page(paginator.num_pages)

    context = {
        'patients': patients,
        'search_query': search_query,
        'gender_filter': gender_filter,
        'min_age': min_age,
        'max_age': max_age,
        'total_count': queryset.count(),
    }
    return render(request, 'patients/list.html', context)


@login_required
def patient_add(request):
    """
    Add a new patient.
    """
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save(commit=False)
            patient.created_by = request.user
            patient.save()
            messages.success(request, f'Patient "{patient.name}" ({patient.patient_id}) added successfully.')
            return redirect('patients:patient_detail', pk=patient.pk)
        else:
            messages.error(request, 'Error saving patient. Please check the form fields.')
    else:
        form = PatientForm()

    return render(request, 'patients/form.html', {
        'form': form,
        'title': 'Register New Patient',
        'is_edit': False
    })


@login_required
def patient_detail(request, pk):
    """
    Display comprehensive patient details along with associated medical records.
    """
    patient = get_object_or_404(Patient, pk=pk)
    records = patient.medical_records.all().order_by('-test_date', '-created_at')

    can_delete = _user_can_delete_patient(request.user, patient)

    context = {
        'patient': patient,
        'records': records,
        'medical_records': records,
        'can_delete': can_delete,
    }
    return render(request, 'patients/detail.html', context)


@login_required
def patient_edit(request, pk):
    """
    Edit an existing patient's details.
    """
    patient = get_object_or_404(Patient, pk=pk)

    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f'Patient "{patient.name}" updated successfully.')
            return redirect('patients:patient_detail', pk=patient.pk)
        else:
            messages.error(request, 'Failed to update patient. Please review errors.')
    else:
        form = PatientForm(instance=patient)

    return render(request, 'patients/form.html', {
        'form': form,
        'patient': patient,
        'title': f'Edit Patient: {patient.name}',
        'is_edit': True
    })


@login_required
def patient_delete(request, pk):
    """
    Delete a patient record with permission checks.
    """
    patient = get_object_or_404(Patient, pk=pk)

    if not _user_can_delete_patient(request.user, patient):
        messages.error(request, 'Permission denied: You do not have permission to delete this patient.')
        return redirect('patients:patient_detail', pk=patient.pk)

    if request.method == 'POST':
        patient_name = patient.name
        patient_id = patient.patient_id
        patient.delete()
        messages.success(request, f'Patient "{patient_name}" ({patient_id}) was successfully deleted.')
        return redirect('patients:patient_list')

    return render(request, 'patients/confirm_delete.html', {'patient': patient})


@login_required
def patient_search(request):
    """
    AJAX endpoint for autocomplete search of patients by name or patient ID.
    Returns JSON list of matching patients.
    """
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        patients = Patient.objects.filter(
            Q(name__icontains=query) | Q(patient_id__icontains=query)
        )[:15]

        for p in patients:
            results.append({
                'id': p.id,
                'patient_id': p.patient_id,
                'name': p.name,
                'age': p.age,
                'gender': p.gender,
                'phone': p.phone,
                'text': f'{p.patient_id} - {p.name} ({p.gender}, {p.age} yrs)'
            })

    return JsonResponse({'results': results})
