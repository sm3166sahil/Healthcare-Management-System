from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q

from .models import MedicalRecord
from .forms import MedicalRecordForm
from patients.models import Patient


def _user_can_delete_record(user, record):
    """Check if the user is authorized to delete the record."""
    if user.is_superuser:
        return True
    if hasattr(user, 'profile') and user.profile.is_admin:
        return True
    if record.created_by == user:
        return True
    return False


@login_required
def record_list(request):
    """
    List medical records with filtering by patient, outcome, date range, and pagination.
    """
    records_qs = MedicalRecord.objects.select_related('patient', 'created_by').order_by('-test_date', '-created_at')

    search_query = request.GET.get('q', '').strip()
    patient_id = request.GET.get('patient_id', '').strip()
    outcome_filter = request.GET.get('outcome', '').strip()
    start_date = request.GET.get('start_date', '').strip()
    end_date = request.GET.get('end_date', '').strip()

    if search_query:
        records_qs = records_qs.filter(
            Q(record_id__icontains=search_query) |
            Q(patient__name__icontains=search_query) |
            Q(patient__patient_id__icontains=search_query) |
            Q(notes__icontains=search_query)
        )

    if patient_id:
        records_qs = records_qs.filter(patient_id=patient_id)

    if outcome_filter:
        records_qs = records_qs.filter(outcome=outcome_filter)

    if start_date:
        records_qs = records_qs.filter(test_date__gte=start_date)

    if end_date:
        records_qs = records_qs.filter(test_date__lte=end_date)

    paginator = Paginator(records_qs, 10)
    page_number = request.GET.get('page')
    try:
        records = paginator.page(page_number)
    except PageNotAnInteger:
        records = paginator.page(1)
    except EmptyPage:
        records = paginator.page(paginator.num_pages)

    patients = Patient.objects.all().order_by('name')

    context = {
        'records': records,
        'patients': patients,
        'search_query': search_query,
        'selected_patient': patient_id,
        'outcome_filter': outcome_filter,
        'start_date': start_date,
        'end_date': end_date,
        'total_count': records_qs.count(),
    }
    return render(request, 'medical_records/list.html', context)


@login_required
def record_add(request):
    """
    Create a new medical record. Allows pre-selecting patient via ?patient_id=X.
    """
    initial_data = {}
    preselected_patient_id = request.GET.get('patient_id')
    if preselected_patient_id:
        try:
            patient = Patient.objects.get(pk=preselected_patient_id)
            initial_data['patient'] = patient
        except (Patient.DoesNotExist, ValueError):
            pass

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.created_by = request.user
            record.save()
            messages.success(request, f'Medical record {record.record_id} successfully created for {record.patient.name}.')
            return redirect('medical_records:record_detail', pk=record.pk)
        else:
            messages.error(request, 'Error creating medical record. Please verify input data.')
    else:
        form = MedicalRecordForm(initial=initial_data)

    return render(request, 'medical_records/form.html', {
        'form': form,
        'title': 'Add Medical Record',
        'is_edit': False
    })


@login_required
def record_detail(request, pk):
    """
    View details of an individual medical record.
    """
    record = get_object_or_404(MedicalRecord.objects.select_related('patient', 'created_by'), pk=pk)
    can_delete = _user_can_delete_record(request.user, record)

    context = {
        'record': record,
        'patient': record.patient,
        'can_delete': can_delete,
    }
    return render(request, 'medical_records/detail.html', context)


@login_required
def record_edit(request, pk):
    """
    Edit an existing medical record.
    """
    record = get_object_or_404(MedicalRecord, pk=pk)

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, f'Medical record {record.record_id} updated successfully.')
            return redirect('medical_records:record_detail', pk=record.pk)
        else:
            messages.error(request, 'Failed to update medical record. Please fix errors below.')
    else:
        form = MedicalRecordForm(instance=record)

    return render(request, 'medical_records/form.html', {
        'form': form,
        'record': record,
        'title': f'Edit Medical Record: {record.record_id}',
        'is_edit': True
    })


@login_required
def record_delete(request, pk):
    """
    Delete a medical record with permission validation.
    """
    record = get_object_or_404(MedicalRecord, pk=pk)

    if not _user_can_delete_record(request.user, record):
        messages.error(request, 'Permission denied: You do not have permission to delete this record.')
        return redirect('medical_records:record_detail', pk=record.pk)

    patient_id = record.patient.pk
    record_id = record.record_id

    if request.method == 'POST':
        record.delete()
        messages.success(request, f'Medical record {record_id} was deleted successfully.')
        return redirect('patients:patient_detail', pk=patient_id)

    return render(request, 'medical_records/confirm_delete.html', {
        'record': record,
        'patient': record.patient
    })
