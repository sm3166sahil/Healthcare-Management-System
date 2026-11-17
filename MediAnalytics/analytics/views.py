import os
import re
import json
import pandas as pd
import numpy as np
from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.conf import settings

from datasets.models import UploadedDataset
from patients.models import Patient
from medical_records.models import MedicalRecord
from .models import CleaningHistory, AnalysisHistory
from .numpy_analysis import HealthcareNumpyAnalyzer
from .pandas_analysis import HealthcarePandasAnalyzer
from .data_cleaning import HealthcareDataCleaner
from .statistical_analysis import HealthcareStatisticalAnalyzer
from .visualization import HealthcareVisualizer


# Helper to load DataFrame from dataset
def get_dataset_dataframe(dataset):
    if dataset and dataset.active_file_path and os.path.exists(dataset.active_file_path):
        for enc in ['utf-8', 'latin1', 'cp1252', 'iso-8859-1']:
            try:
                return pd.read_csv(dataset.active_file_path, encoding=enc)
            except (UnicodeDecodeError, UnicodeError):
                continue
            except Exception:
                return None
    return None


@login_required
def cleaning_view(request):
    """
    Module 5: Interactive Healthcare Data Cleaning Interface.
    Covers FDS Unit 2 & Unit 4.
    """
    datasets = UploadedDataset.objects.all().order_by('-uploaded_at')
    dataset_id = request.GET.get('dataset_id') or request.POST.get('dataset_id')
    selected_dataset = None
    audit_data = None
    cleaning_summary = None

    if dataset_id:
        try:
            selected_dataset = UploadedDataset.objects.get(pk=dataset_id)
        except UploadedDataset.DoesNotExist:
            pass

    if selected_dataset:
        df = get_dataset_dataframe(selected_dataset)
        if df is not None:
            cleaner = HealthcareDataCleaner(df)

            # Handle POST cleaning operations
            if request.method == 'POST':
                action = request.POST.get('action')

                if action == 'impute_missing':
                    strategy = request.POST.get('strategy', 'mean')
                    column = request.POST.get('column') or None
                    custom_val = request.POST.get('custom_val') or None
                    res = cleaner.handle_missing_values(strategy=strategy, column=column, custom_value=custom_val)
                    messages.success(request, f"Missing values imputed using strategy '{strategy}'. Fixed {res['cleaned_count']} cells.")

                elif action == 'remove_duplicates':
                    res = cleaner.remove_duplicates()
                    messages.success(request, f"Removed {res['removed_duplicates']} duplicate rows.")

                elif action == 'handle_outliers':
                    column = request.POST.get('column')
                    method = request.POST.get('method', 'cap')
                    res = cleaner.handle_outliers(column=column, method=method)
                    if 'error' in res:
                        messages.error(request, res['error'])
                    else:
                        messages.success(request, f"Outlier handling '{method}' applied to '{column}'.")

                elif action == 'normalize_categories':
                    cleaner.standardize_categories()
                    messages.success(request, "Categorical columns normalized and standardized.")

                elif action == 'save_as_cleaned':
                    # Save cleaned dataframe to media/cleaned_datasets
                    cleaned_dir = os.path.join(settings.MEDIA_ROOT, 'cleaned_datasets')
                    os.makedirs(cleaned_dir, exist_ok=True)
                    fname = f"cleaned_{selected_dataset.pk}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    cleaned_abs_path = os.path.join(cleaned_dir, fname)
                    cleaner.df.to_csv(cleaned_abs_path, index=False)

                    # Update model
                    rel_path = os.path.join('cleaned_datasets', fname)
                    selected_dataset.is_cleaned = True
                    selected_dataset.cleaned_file = rel_path
                    selected_dataset.row_count = len(cleaner.df)
                    selected_dataset.column_count = len(cleaner.df.columns)
                    selected_dataset.save()

                    # Record history
                    CleaningHistory.objects.create(
                        dataset=selected_dataset,
                        cleaned_by=request.user,
                        cleaning_action="Comprehensive Data Cleaning & Imputation",
                        description="; ".join(cleaner.operations_performed) if cleaner.operations_performed else "Standard cleaning",
                        rows_before=len(cleaner.original_df),
                        rows_after=len(cleaner.df)
                    )
                    messages.success(request, f"Cleaned dataset saved successfully as new version! Total rows: {len(cleaner.df)}.")

                elif action == 'restore_original':
                    if selected_dataset.cleaned_file and os.path.exists(selected_dataset.cleaned_file.path):
                        try:
                            os.remove(selected_dataset.cleaned_file.path)
                        except OSError:
                            pass
                    selected_dataset.is_cleaned = False
                    selected_dataset.cleaned_file = None
                    # Reload original counts
                    orig_df = pd.read_csv(selected_dataset.file.path)
                    selected_dataset.row_count = len(orig_df)
                    selected_dataset.column_count = len(orig_df.columns)
                    selected_dataset.save()
                    messages.info(request, "Dataset restored to original uploaded state.")
                    return redirect(f"{request.path}?dataset_id={selected_dataset.pk}")

            # Quality audit
            audit_data = cleaner.audit_quality()
            cleaning_summary = cleaner.get_summary()

    context = {
        'datasets': datasets,
        'selected_dataset': selected_dataset,
        'audit': audit_data,
        'cleaning_summary': cleaning_summary,
        'title': 'Healthcare Data Preprocessing & Cleaning',
    }
    return render(request, 'analytics/cleaning.html', context)


@login_required
def numpy_view(request):
    """
    Module 6: NumPy Computational Analysis Engine.
    Covers FDS Unit 1 in complete academic depth.
    """
    datasets = UploadedDataset.objects.all().order_by('-uploaded_at')
    dataset_id = request.GET.get('dataset_id')

    selected_dataset = None
    custom_stats = None
    column_name = None

    if dataset_id:
        try:
            selected_dataset = UploadedDataset.objects.get(pk=dataset_id)
            df = get_dataset_dataframe(selected_dataset)
            if df is not None:
                num_cols = df.select_dtypes(include=[np.number]).columns
                if len(num_cols) > 0:
                    column_name = request.GET.get('column') or num_cols[0]
                    if column_name in df.columns:
                        analyzer = HealthcareNumpyAnalyzer(df[column_name].dropna().values)
                        custom_stats = analyzer.compute_statistics()
        except UploadedDataset.DoesNotExist:
            pass

    # Standard Unit 1 Demonstrations
    array_creation = HealthcareNumpyAnalyzer.demonstrate_array_creation()
    manipulation = HealthcareNumpyAnalyzer.demonstrate_manipulation()
    math_ops = HealthcareNumpyAnalyzer.demonstrate_math_broadcasting()
    distributions = HealthcareNumpyAnalyzer.generate_random_distributions()
    linalg = HealthcareNumpyAnalyzer.demonstrate_linear_algebra()

    context = {
        'datasets': datasets,
        'selected_dataset': selected_dataset,
        'column_name': column_name,
        'custom_stats': custom_stats,
        'array_creation': array_creation,
        'manipulation': manipulation,
        'math_ops': math_ops,
        'distributions': distributions,
        'linalg': linalg,
        'title': 'NumPy Numerical Analysis Engine (FDS Unit 1)',
    }
    return render(request, 'analytics/numpy_analysis.html', context)


@login_required
def pandas_view(request):
    """
    Module 7: Pandas Data Analysis Engine.
    Covers FDS Unit 4.
    """
    datasets = UploadedDataset.objects.all().order_by('-uploaded_at')
    dataset_id = request.GET.get('dataset_id')
    selected_dataset = None
    inspection = None
    loc_iloc = None
    groupby_result = None
    pivot_result = None
    crosstab_result = None
    timeseries_result = None

    if dataset_id:
        try:
            selected_dataset = UploadedDataset.objects.get(pk=dataset_id)
            df = get_dataset_dataframe(selected_dataset)
            if df is not None:
                analyzer = HealthcarePandasAnalyzer(df)
                inspection = analyzer.inspect_dataframe()
                loc_iloc = analyzer.demonstrate_loc_iloc()

                # GroupBy
                grp_col = request.GET.get('grp_col')
                val_col = request.GET.get('val_col')
                groupby_result = analyzer.perform_groupby_analysis(grp_col, val_col)

                # Pivot & Crosstab
                pivot_result = analyzer.create_pivot_table()
                crosstab_result = analyzer.create_crosstab()
                timeseries_result = analyzer.perform_window_and_timeseries()
        except UploadedDataset.DoesNotExist:
            pass

    context = {
        'datasets': datasets,
        'selected_dataset': selected_dataset,
        'inspection': inspection,
        'loc_iloc': loc_iloc,
        'groupby_result': groupby_result,
        'pivot_result': pivot_result,
        'crosstab_result': crosstab_result,
        'timeseries_result': timeseries_result,
        'title': 'Pandas Data Analysis Engine (FDS Unit 4)',
    }
    return render(request, 'analytics/pandas_analysis.html', context)


@login_required
def statistics_view(request):
    """
    Module 8: Statistical Healthcare Analysis.
    Covers FDS Unit 1 & Unit 4.
    """
    datasets = UploadedDataset.objects.all().order_by('-uploaded_at')
    dataset_id = request.GET.get('dataset_id')
    selected_dataset = None
    stats_list = None
    pearson_corr = None
    spearman_corr = None
    group_comp = None

    if dataset_id:
        try:
            selected_dataset = UploadedDataset.objects.get(pk=dataset_id)
            df = get_dataset_dataframe(selected_dataset)
            if df is not None:
                analyzer = HealthcareStatisticalAnalyzer(df)
                stats_list = analyzer.get_descriptive_statistics()
                pearson_corr = analyzer.get_correlation_matrix(method='pearson')
                spearman_corr = analyzer.get_correlation_matrix(method='spearman')
                group_comp = analyzer.get_group_comparisons()
        except UploadedDataset.DoesNotExist:
            pass

    context = {
        'datasets': datasets,
        'selected_dataset': selected_dataset,
        'stats_list': stats_list,
        'pearson_corr': pearson_corr,
        'spearman_corr': spearman_corr,
        'group_comp': group_comp,
        'title': 'Descriptive & Inferential Statistical Analysis',
    }
    return render(request, 'analytics/statistics.html', context)


@login_required
def visualization_view(request):
    """
    Module 9: Clinical Data Visualization using Matplotlib & Seaborn.
    Covers FDS Unit 5.
    """
    datasets = UploadedDataset.objects.all().order_by('-uploaded_at')
    dataset_id = request.GET.get('dataset_id')
    chart_type = request.GET.get('chart_type', 'histogram')
    x_col = request.GET.get('x_col')
    y_col = request.GET.get('y_col')
    hue_col = request.GET.get('hue')

    selected_dataset = None
    chart_url = None
    columns_list = []
    numeric_cols = []
    categorical_cols = []

    if dataset_id:
        try:
            selected_dataset = UploadedDataset.objects.get(pk=dataset_id)
            df = get_dataset_dataframe(selected_dataset)
            if df is not None:
                columns_list = list(df.columns)
                numeric_cols = list(df.select_dtypes(include=[np.number]).columns)
                categorical_cols = list(df.select_dtypes(include=['object', 'category']).columns)

                viz = HealthcareVisualizer(df)

                if chart_type == 'histogram':
                    col = x_col if x_col in numeric_cols else (numeric_cols[0] if numeric_cols else None)
                    if col:
                        chart_url = viz.plot_histogram_kde(col)
                elif chart_type == 'boxplot':
                    col = x_col if x_col in numeric_cols else (numeric_cols[0] if numeric_cols else None)
                    if col:
                        chart_url = viz.plot_boxplot(col)
                elif chart_type == 'violin':
                    col = x_col if x_col in numeric_cols else (numeric_cols[0] if numeric_cols else None)
                    grp = y_col if y_col in categorical_cols else None
                    if col:
                        chart_url = viz.plot_violin(col, group_by=grp)
                elif chart_type == 'countplot':
                    col = x_col if x_col in categorical_cols else (categorical_cols[0] if categorical_cols else None)
                    if col:
                        chart_url = viz.plot_countplot(col)
                elif chart_type == 'pie':
                    col = x_col if x_col in categorical_cols else (categorical_cols[0] if categorical_cols else None)
                    if col:
                        chart_url = viz.plot_pie_chart(col)
                elif chart_type == 'scatter':
                    x = x_col if x_col in numeric_cols else (numeric_cols[0] if len(numeric_cols) > 0 else None)
                    y = y_col if y_col in numeric_cols else (numeric_cols[1] if len(numeric_cols) > 1 else None)
                    h = hue_col if hue_col in categorical_cols else None
                    if x and y:
                        chart_url = viz.plot_scatter_reg(x, y, hue=h)
                elif chart_type == 'heatmap':
                    chart_url = viz.plot_correlation_heatmap()

        except UploadedDataset.DoesNotExist:
            pass

    context = {
        'datasets': datasets,
        'selected_dataset': selected_dataset,
        'chart_type': chart_type,
        'x_col': x_col,
        'y_col': y_col,
        'hue_col': hue_col,
        'columns_list': columns_list,
        'numeric_cols': numeric_cols,
        'categorical_cols': categorical_cols,
        'chart_url': chart_url,
        'title': 'Clinical Data Visualization (FDS Unit 5)',
    }
    return render(request, 'analytics/visualization.html', context)


@login_required
def json_regex_view(request):
    """
    Module 10: JSON Processing & Regular Expressions.
    Covers FDS Unit 2.
    """
    regex_input = request.POST.get('regex_input', '')
    regex_type = request.POST.get('regex_type', 'email')
    regex_result = None

    json_input = request.POST.get('json_input', '')
    json_result = None

    if request.method == 'POST':
        action = request.POST.get('action')

        # Regex Validation Engine
        if action == 'test_regex':
            patterns = {
                'email': r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$',
                'phone': r'^\+?[0-9]{10,15}$',
                'patient_id': r'^PAT-\d{4}$',
                'record_id': r'^MR-\d{5}$',
                'blood_pressure': r'^\d{2,3}/\d{2,3}$'
            }
            pattern = patterns.get(regex_type, r'.*')
            match = re.match(pattern, regex_input.strip())
            regex_result = {
                'input': regex_input,
                'pattern': pattern,
                'is_valid': bool(match),
                'match_group': match.group(0) if match else None
            }

        # JSON Parser & Validator
        elif action == 'parse_json':
            try:
                parsed = json.loads(json_input)
                formatted = json.dumps(parsed, indent=4)
                json_result = {
                    'is_valid': True,
                    'formatted': formatted,
                    'type': type(parsed).__name__,
                    'element_count': len(parsed) if hasattr(parsed, '__len__') else 1
                }
            except json.JSONDecodeError as err:
                json_result = {
                    'is_valid': False,
                    'error': str(err)
                }

    # Patient export as JSON demo
    sample_patients = Patient.objects.all()[:5]
    patients_data = []
    for p in sample_patients:
        patients_data.append({
            'patient_id': p.patient_id,
            'name': p.name,
            'age': p.age,
            'gender': p.gender,
            'phone': p.phone,
            'email': p.email,
            'registration_date': p.registration_date.strftime('%Y-%m-%d') if p.registration_date else ''
        })
    sample_json = json.dumps(patients_data, indent=4)

    context = {
        'regex_result': regex_result,
        'regex_input': regex_input,
        'regex_type': regex_type,
        'json_result': json_result,
        'json_input': json_input,
        'sample_json': sample_json,
        'title': 'JSON Processing & Regular Expression Engine (FDS Unit 2)',
    }
    return render(request, 'analytics/json_regex.html', context)


@login_required
def fds_coverage_view(request):
    """
    FDS Syllabus Coverage Matrix & Viva Demonstration Guide.
    Displays alignment with Units 1, 2, 3, 4, and 5.
    """
    context = {
        'title': 'FDS Syllabus Mapping & Viva Defense Guide',
    }
    return render(request, 'analytics/fds_coverage.html', context)
