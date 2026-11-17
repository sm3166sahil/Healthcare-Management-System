import os
import csv
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import FileResponse, Http404
from django.core.paginator import Paginator
from django.conf import settings
import pandas as pd
import numpy as np

from datasets.models import UploadedDataset
from .models import GeneratedReport
from .pdf_generator import HealthcareReportGenerator


@login_required
def report_list(request):
    """
    List all generated analytical reports with filtering and pagination.
    """
    reports = GeneratedReport.objects.all().order_by('-generated_at')
    report_type = request.GET.get('type')
    if report_type:
        reports = reports.filter(report_type=report_type)

    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'selected_type': report_type,
        'title': 'Analytical Reports & Summaries',
    }
    return render(request, 'reports/list.html', context)


@login_required
def report_generate(request):
    """
    Generate a new analytical report (PDF or CSV summary) based on chosen dataset.
    """
    datasets = UploadedDataset.objects.all().order_by('-uploaded_at')

    if request.method == 'POST':
        dataset_id = request.POST.get('dataset_id')
        report_title = request.POST.get('title', 'Healthcare Analytics Summary')
        report_type = request.POST.get('report_type', 'PDF')
        summary_text = request.POST.get('summary', '')

        dataset = None
        if dataset_id:
            try:
                dataset = UploadedDataset.objects.get(pk=dataset_id)
            except UploadedDataset.DoesNotExist:
                pass

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        safe_title = "".join(c for c in report_title if c.isalnum() or c in (' ', '_', '-')).rstrip()
        safe_title = safe_title.replace(' ', '_').lower()

        # Compute summary stats if dataset exists
        stats_list = []
        if dataset and os.path.exists(dataset.active_file_path):
            try:
                df = pd.read_csv(dataset.active_file_path)
                num_cols = df.select_dtypes(include=[np.number]).columns
                for col in num_cols:
                    s = df[col].dropna()
                    if len(s) > 0:
                        stats_list.append({
                            'metric': col.replace('_', ' ').title(),
                            'mean': float(s.mean()),
                            'std': float(s.std()),
                            'median': float(s.median()),
                            'min': float(s.min()),
                            'max': float(s.max())
                        })
            except Exception as e:
                pass

        if report_type == 'PDF':
            filename = f"report_{safe_title}_{timestamp}.pdf"
            generator = HealthcareReportGenerator(
                filename=filename,
                title=report_title,
                dataset=dataset,
                summary_text=summary_text,
                stats_data=stats_list,
                author=request.user.get_full_name() or request.user.username
            )
            file_path = generator.generate()
            rel_path = os.path.join('reports', filename)

            report = GeneratedReport.objects.create(
                title=report_title,
                report_type='PDF',
                dataset=dataset,
                file=rel_path,
                summary=summary_text,
                generated_by=request.user
            )
            messages.success(request, f"PDF report '{report_title}' generated successfully!")
            return redirect('reports:list')

        elif report_type == 'CSV':
            filename = f"summary_{safe_title}_{timestamp}.csv"
            abs_dir = os.path.join(settings.MEDIA_ROOT, 'reports')
            os.makedirs(abs_dir, exist_ok=True)
            file_path = os.path.join(abs_dir, filename)

            # Write descriptive stats to CSV
            with open(file_path, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(['Metric', 'Mean', 'Std_Dev', 'Median', 'Min', 'Max'])
                for item in stats_list:
                    writer.writerow([
                        item['metric'],
                        round(item['mean'], 4),
                        round(item['std'], 4),
                        round(item['median'], 4),
                        round(item['min'], 4),
                        round(item['max'], 4)
                    ])

            rel_path = os.path.join('reports', filename)
            GeneratedReport.objects.create(
                title=report_title,
                report_type='CSV',
                dataset=dataset,
                file=rel_path,
                summary=summary_text,
                generated_by=request.user
            )
            messages.success(request, f"CSV summary export '{report_title}' created successfully!")
            return redirect('reports:list')

    context = {
        'datasets': datasets,
        'title': 'Generate Analytical Report',
    }
    return render(request, 'reports/generate.html', context)


@login_required
def report_download(request, pk):
    """
    Download a previously generated report file.
    """
    report = get_object_or_404(GeneratedReport, pk=pk)
    if not report.file or not os.path.exists(report.file.path):
        raise Http404("Report file does not exist on disk.")

    return FileResponse(
        open(report.file.path, 'rb'),
        as_attachment=True,
        filename=os.path.basename(report.file.path)
    )


@login_required
def report_delete(request, pk):
    """
    Delete a generated report.
    """
    report = get_object_or_404(GeneratedReport, pk=pk)
    title = report.title
    if report.file and os.path.exists(report.file.path):
        try:
            os.remove(report.file.path)
        except OSError:
            pass
    report.delete()
    messages.success(request, f"Report '{title}' was deleted.")
    return redirect('reports:list')
