import os
import pandas as pd
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import FileResponse, Http404
from django.db.models import Q

from .models import UploadedDataset
from .forms import DatasetUploadForm


@login_required
def dataset_list(request):
    """
    List all uploaded datasets with search and pagination.
    """
    datasets_qs = UploadedDataset.objects.select_related('uploaded_by').order_by('-uploaded_at')

    search_query = request.GET.get('q', '').strip()
    status_filter = request.GET.get('status', '').strip()

    if search_query:
        datasets_qs = datasets_qs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(column_names__icontains=search_query)
        )

    if status_filter == 'cleaned':
        datasets_qs = datasets_qs.filter(is_cleaned=True)
    elif status_filter == 'raw':
        datasets_qs = datasets_qs.filter(is_cleaned=False)

    paginator = Paginator(datasets_qs, 10)
    page_number = request.GET.get('page')
    try:
        datasets = paginator.page(page_number)
    except PageNotAnInteger:
        datasets = paginator.page(1)
    except EmptyPage:
        datasets = paginator.page(paginator.num_pages)

    context = {
        'datasets': datasets,
        'search_query': search_query,
        'status_filter': status_filter,
        'total_count': datasets_qs.count(),
    }
    return render(request, 'datasets/list.html', context)


@login_required
def dataset_upload(request):
    """
    Upload a new healthcare CSV dataset, automatically parsing shape and column metadata.
    """
    if request.method == 'POST':
        post_data = request.POST.copy()
        if 'name' in post_data and not post_data.get('title'):
            post_data['title'] = post_data['name']

        form = DatasetUploadForm(post_data, request.FILES)
        if form.is_valid():
            dataset = form.save(commit=False)
            dataset.uploaded_by = request.user
            dataset.file_size = dataset.file.size
            dataset.save()

            # Attempt to parse dimensions and column names with pandas
            try:
                try:
                    df = pd.read_csv(dataset.file.path, nrows=50000)
                except UnicodeDecodeError:
                    df = pd.read_csv(dataset.file.path, encoding='latin1', nrows=50000)

                dataset.row_count = len(df)
                dataset.column_count = len(df.columns)
                dataset.column_names = ', '.join([str(col) for col in df.columns])
                dataset.save(update_fields=['row_count', 'column_count', 'column_names'])
                messages.success(
                    request,
                    f'Dataset "{dataset.title}" uploaded successfully with {dataset.row_count} rows and {dataset.column_count} columns.'
                )
            except Exception as e:
                messages.warning(
                    request,
                    f'Dataset uploaded, but metadata extraction encountered an issue: {str(e)}'
                )

            return redirect('datasets:dataset_explore', pk=dataset.pk)
        else:
            for field, errs in form.errors.items():
                for err in errs:
                    messages.error(request, f'{field.capitalize()}: {err}')
    else:
        form = DatasetUploadForm()

    return render(request, 'datasets/upload.html', {'form': form})


@login_required
def dataset_explore(request, pk):
    """
    Interactive exploration of dataset structure, column information, summary statistics, and head rows.
    """
    dataset = get_object_or_404(UploadedDataset, pk=pk)
    file_path = dataset.active_file_path

    if not file_path or not os.path.exists(file_path):
        messages.error(request, 'The file associated with this dataset could not be located on disk.')
        return redirect('datasets:dataset_list')

    head_data = []
    columns_info = []
    summary_stats = []
    total_rows = 0
    total_cols = 0
    error_message = None

    try:
        df = pd.read_csv(file_path)
        total_rows = len(df)
        total_cols = len(df.columns)

        # Column metadata: type, missing values, unique values
        for col in df.columns:
            columns_info.append({
                'name': col,
                'dtype': str(df[col].dtype),
                'non_null_count': int(df[col].count()),
                'null_count': int(df[col].isnull().sum()),
                'null_pct': round((df[col].isnull().sum() / total_rows) * 100, 2) if total_rows > 0 else 0,
                'unique_count': int(df[col].nunique()),
            })

        # Head rows as list of dicts
        head_df = df.head(15).fillna('')
        head_data = head_df.to_dict(orient='records')
        head_columns = list(head_df.columns)

        # Descriptive statistics for numerical columns
        numeric_df = df.select_dtypes(include=['number'])
        if not numeric_df.empty:
            describe_df = numeric_df.describe().round(3).reset_index()
            # Convert describe table into rows
            summary_stats = {
                'columns': list(describe_df.columns),
                'rows': describe_df.to_dict(orient='records')
            }
        else:
            summary_stats = None

    except Exception as e:
        error_message = f"Error reading or processing dataset: {str(e)}"

    context = {
        'dataset': dataset,
        'columns_info': columns_info,
        'head_data': head_data,
        'head_columns': head_columns if 'head_columns' in locals() else [],
        'summary_stats': summary_stats,
        'total_rows': total_rows,
        'total_cols': total_cols,
        'error_message': error_message,
    }
    return render(request, 'datasets/explore.html', context)


@login_required
def dataset_download(request, pk):
    """
    Download the dataset file (cleaned version if available, otherwise original).
    """
    dataset = get_object_or_404(UploadedDataset, pk=pk)
    file_path = dataset.active_file_path

    if not file_path or not os.path.exists(file_path):
        raise Http404("Dataset file does not exist.")

    response = FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))
    return response


@login_required
def dataset_delete(request, pk):
    """
    Delete a dataset and its physical file from storage.
    """
    dataset = get_object_or_404(UploadedDataset, pk=pk)

    # Permission check: admin or uploader
    is_authorized = (
        request.user.is_superuser or
        (hasattr(request.user, 'profile') and request.user.profile.is_admin) or
        dataset.uploaded_by == request.user
    )

    if not is_authorized:
        messages.error(request, 'Permission denied: You cannot delete this dataset.')
        return redirect('datasets:dataset_list')

    if request.method == 'POST':
        title = dataset.title
        # Delete file from storage
        if dataset.file and os.path.exists(dataset.file.path):
            try:
                os.remove(dataset.file.path)
            except OSError:
                pass
        if dataset.cleaned_file and os.path.exists(dataset.cleaned_file.path):
            try:
                os.remove(dataset.cleaned_file.path)
            except OSError:
                pass

        dataset.delete()
        messages.success(request, f'Dataset "{title}" was successfully deleted.')
        return redirect('datasets:dataset_list')

    return render(request, 'datasets/confirm_delete.html', {'dataset': dataset})
