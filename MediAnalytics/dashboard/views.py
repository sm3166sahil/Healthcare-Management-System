import io
import base64
from collections import Counter
import numpy as np
import pandas as pd

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Avg

from patients.models import Patient
from medical_records.models import MedicalRecord
from datasets.models import UploadedDataset


def _render_age_chart(ages):
    """Generate high-DPI patient age distribution histogram with KDE curve."""
    fig, ax = plt.subplots(figsize=(7.2, 3.8), dpi=120)
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#f8fafc')

    if len(ages) > 0:
        ages_arr = np.array(ages, dtype=float)
        mean_age = float(np.mean(ages_arr))
        median_age = float(np.median(ages_arr))

        sns.histplot(
            ages_arr,
            kde=True,
            color='#0d9488',
            edgecolor='#ffffff',
            linewidth=1.2,
            bins=14,
            ax=ax,
            alpha=0.75
        )

        ax.axvline(mean_age, color='#e11d48', linestyle='--', linewidth=1.8, label=f'Mean: {mean_age:.1f} yrs')
        ax.axvline(median_age, color='#1e3a8a', linestyle=':', linewidth=2.0, label=f'Median: {median_age:.1f} yrs')

        ax.set_title('Patient Age Demographic Distribution', fontsize=12, fontweight='bold', pad=12, color='#0f172a')
        ax.set_xlabel('Age (Years)', fontsize=10, fontweight='bold', color='#334155')
        ax.set_ylabel('Patient Count', fontsize=10, fontweight='bold', color='#334155')
        ax.grid(True, linestyle='--', alpha=0.5, color='#cbd5e1')
        ax.legend(frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=9, loc='upper right')
    else:
        ax.text(0.5, 0.5, 'No Patient Records Available', ha='center', va='center', transform=ax.transAxes, color='#94a3b8')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    return buf.getvalue()


def _render_gender_outcome_chart(genders_list, records_df):
    """
    Generate publication-grade clinical visualization:
    Left: Gender Demographic Donut
    Right: Grouped Bar Chart of Diagnostic Outcomes Stratified by Gender (Female vs Male)
    """
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(8.8, 3.8), dpi=130, gridspec_kw={'width_ratios': [1, 1.4]})
    fig.patch.set_facecolor('#ffffff')

    # 1. Left: Gender Demographics Donut
    if genders_list:
        gender_counts = Counter(genders_list)
        labels1 = list(gender_counts.keys())
        counts1 = list(gender_counts.values())
        palette1 = {'Female': '#0d9488', 'Male': '#2563eb', 'Other': '#f59e0b'}
        colors1 = [palette1.get(k, '#8b5cf6') for k in labels1]

        wedges1, texts1, autotexts1 = ax1.pie(
            counts1,
            labels=labels1,
            autopct='%1.1f%%',
            startangle=90,
            colors=colors1,
            pctdistance=0.72,
            wedgeprops=dict(width=0.45, edgecolor='#ffffff', linewidth=2.5)
        )
        for t in texts1:
            t.set_fontsize(9)
            t.set_fontweight('bold')
            t.set_color('#1e293b')
        for at in autotexts1:
            at.set_fontsize(9)
            at.set_fontweight('bold')
            at.set_color('#ffffff')

        total_p = sum(counts1)
        ax1.text(0, 0, f'{total_p}\nPatients', ha='center', va='center', fontsize=10, fontweight='bold', color='#0f172a')
        ax1.set_title('Gender Demographics', fontsize=11, fontweight='bold', pad=10, color='#0f172a')
    else:
        ax1.text(0.5, 0.5, 'No Gender Data', ha='center', va='center', transform=ax1.transAxes, color='#94a3b8')

    # 2. Right: Grouped Bar Chart of Outcomes Stratified by Gender
    if records_df is not None and not records_df.empty and 'patient__gender' in records_df.columns and 'outcome' in records_df.columns:
        ct = pd.crosstab(records_df['patient__gender'], records_df['outcome'])
        genders_order = [g for g in ['Female', 'Male'] if g in ct.index]
        if not genders_order:
            genders_order = list(ct.index)
        outcomes_order = [o for o in ['Negative', 'Positive', 'Inconclusive'] if o in ct.columns]
        if not outcomes_order:
            outcomes_order = list(ct.columns)

        x = np.arange(len(genders_order))
        width = 0.24
        color_map = {
            'Negative': '#10b981',
            'Normal': '#10b981',
            'Healthy': '#10b981',
            'Positive': '#ef4444',
            'Abnormal': '#ef4444',
            'Critical': '#ef4444',
            'Inconclusive': '#f59e0b',
        }

        ax2.set_facecolor('#f8fafc')
        for i, outcome in enumerate(outcomes_order):
            values = [ct.loc[g, outcome] if (g in ct.index and outcome in ct.columns) else 0 for g in genders_order]
            offset = (i - (len(outcomes_order) - 1) / 2) * (width + 0.04)
            bars = ax2.bar(x + offset, values, width, label=outcome, color=color_map.get(outcome, '#64748b'), edgecolor='none', alpha=0.92)
            for bar in bars:
                h = bar.get_height()
                if h > 0:
                    ax2.text(bar.get_x() + bar.get_width() / 2, h + 8, f'{int(h)}', ha='center', va='bottom', fontsize=8.5, fontweight='bold', color='#1e293b')

        ax2.set_xticks(x)
        ax2.set_xticklabels([f'{g}\n(N={int(ct.loc[g].sum())})' for g in genders_order], fontsize=9, fontweight='bold')
        ax2.set_ylabel('Clinical Records', fontsize=9, fontweight='bold', color='#334155')
        max_h = float(ct.values.max()) if ct.size > 0 else 100
        ax2.set_ylim(0, max_h * 1.25)
        ax2.grid(True, axis='y', linestyle='--', alpha=0.5, color='#cbd5e1')
        ax2.legend(frameon=True, facecolor='#ffffff', edgecolor='#e2e8f0', fontsize=8.5, loc='upper right')
        tot_recs = len(records_df)
        ax2.set_title(f'Outcome Breakdown by Gender (N={tot_recs})', fontsize=11, fontweight='bold', pad=10, color='#0f172a')
    else:
        ax2.text(0.5, 0.5, 'No Clinical Records Available', ha='center', va='center', transform=ax2.transAxes, color='#94a3b8')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', bbox_inches='tight', facecolor=fig.get_facecolor(), edgecolor='none')
    plt.close(fig)
    return buf.getvalue()


@login_required
def index(request):
    """
    Main dashboard overview view.
    Aggregates key healthcare statistics and recent activity across patients,
    medical records, and uploaded datasets. Also serves dynamic Matplotlib charts.
    """
    ages = list(Patient.objects.values_list('age', flat=True))
    genders = list(Patient.objects.values_list('gender', flat=True))
    records_qs = list(MedicalRecord.objects.select_related('patient').values('patient__gender', 'outcome'))
    records_df = pd.DataFrame(records_qs) if records_qs else pd.DataFrame(columns=['patient__gender', 'outcome'])

    chart_type = request.GET.get('chart')
    if chart_type == 'age_distribution':
        chart_bytes = _render_age_chart(ages)
        return HttpResponse(chart_bytes, content_type='image/png')
    elif chart_type == 'gender_distribution':
        chart_bytes = _render_gender_outcome_chart(genders, records_df)
        return HttpResponse(chart_bytes, content_type='image/png')

    total_patients = Patient.objects.count()
    total_records = MedicalRecord.objects.count()
    total_datasets = UploadedDataset.objects.count()

    # Calculate averages safely
    avg_age_dict = Patient.objects.aggregate(avg=Avg('age'))
    avg_age = round(avg_age_dict['avg'], 1) if avg_age_dict['avg'] is not None else 0.0

    avg_hr_dict = MedicalRecord.objects.filter(heart_rate__isnull=False).aggregate(avg=Avg('heart_rate'))
    avg_heart_rate = round(avg_hr_dict['avg'], 1) if avg_hr_dict['avg'] is not None else 0.0

    # Base64 pre-rendering for guaranteed instant display
    age_chart_base64 = ''
    gender_chart_base64 = ''
    if total_patients > 0:
        try:
            age_chart_base64 = base64.b64encode(_render_age_chart(ages)).decode('utf-8')
        except Exception:
            age_chart_base64 = ''

        try:
            gender_chart_base64 = base64.b64encode(_render_gender_outcome_chart(genders, records_df)).decode('utf-8')
        except Exception:
            gender_chart_base64 = ''

    # Detailed Patient Age Distribution Analytics
    age_analytics = {}
    if ages:
        ages_arr = np.array(ages, dtype=float)
        q25, q75 = np.percentile(ages_arr, [25, 75])
        tot_p = len(ages_arr)
        c_young = int(np.sum((ages_arr >= 18) & (ages_arr <= 35)))
        c_mid = int(np.sum((ages_arr >= 36) & (ages_arr <= 50)))
        c_senior = int(np.sum((ages_arr >= 51) & (ages_arr <= 65)))
        c_geriatric = int(np.sum(ages_arr >= 66))

        age_analytics = {
            'min': int(np.min(ages_arr)),
            'max': int(np.max(ages_arr)),
            'median': float(np.median(ages_arr)),
            'std': float(round(np.std(ages_arr), 1)),
            'iqr': float(round(q75 - q25, 1)),
            'brackets': [
                {'name': 'Young (18–35)', 'count': c_young, 'pct': round((c_young / tot_p) * 100, 1), 'class': 'border-info text-info'},
                {'name': 'Middle-Aged (36–50)', 'count': c_mid, 'pct': round((c_mid / tot_p) * 100, 1), 'class': 'border-primary text-primary'},
                {'name': 'Senior (51–65)', 'count': c_senior, 'pct': round((c_senior / tot_p) * 100, 1), 'class': 'border-teal text-teal'},
                {'name': 'Geriatric (66+)', 'count': c_geriatric, 'pct': round((c_geriatric / tot_p) * 100, 1), 'class': 'border-warning text-warning'},
            ]
        }

    # Detailed Gender & Outcome Stratification Analysis
    gender_analytics = []
    gender_counts = Counter(genders)
    tot_gender = sum(gender_counts.values())
    if tot_gender > 0:
        for g, count in gender_counts.items():
            gender_analytics.append({
                'label': g,
                'count': count,
                'pct': round((count / tot_gender) * 100, 1),
                'badge_class': 'bg-teal text-white' if g == 'Female' else 'bg-primary text-white'
            })

    # Overall Outcome Counts
    outcome_analytics = []
    outcomes = Counter(records_df['outcome'].tolist()) if not records_df.empty else Counter()
    tot_outcome = sum(outcomes.values())
    positivity_rate = 0.0
    if tot_outcome > 0:
        pos_count = outcomes.get('Positive', 0)
        positivity_rate = round((pos_count / tot_outcome) * 100, 1)

        badge_map = {
            'Negative': 'bg-success-subtle text-success border border-success-subtle',
            'Positive': 'bg-danger-subtle text-danger border border-danger-subtle',
            'Inconclusive': 'bg-warning-subtle text-warning border border-warning-subtle',
            'Normal': 'bg-success-subtle text-success border border-success-subtle',
            'Abnormal': 'bg-danger-subtle text-danger border border-danger-subtle',
        }
        for o, count in outcomes.items():
            outcome_analytics.append({
                'label': o,
                'count': count,
                'pct': round((count / tot_outcome) * 100, 1),
                'badge_class': badge_map.get(o, 'bg-secondary-subtle text-secondary')
            })

    # Cross-Tabulation: Outcomes Stratified BY Gender
    stratified_outcomes = []
    if not records_df.empty and 'patient__gender' in records_df.columns and 'outcome' in records_df.columns:
        ct = pd.crosstab(records_df['patient__gender'], records_df['outcome'])
        for g in ['Female', 'Male']:
            if g in ct.index:
                row = ct.loc[g]
                tot_g = int(row.sum())
                neg = int(row.get('Negative', 0))
                pos = int(row.get('Positive', 0))
                inc = int(row.get('Inconclusive', 0))
                stratified_outcomes.append({
                    'gender': g,
                    'total': tot_g,
                    'negative': neg,
                    'negative_pct': round((neg / tot_g) * 100, 1) if tot_g > 0 else 0.0,
                    'positive': pos,
                    'positive_pct': round((pos / tot_g) * 100, 1) if tot_g > 0 else 0.0,
                    'inconclusive': inc,
                    'inconclusive_pct': round((inc / tot_g) * 100, 1) if tot_g > 0 else 0.0,
                    'positivity_rate': round((pos / tot_g) * 100, 1) if tot_g > 0 else 0.0,
                })

    # Recent items
    recent_patients = Patient.objects.order_by('-created_at')[:5]
    recent_datasets = UploadedDataset.objects.order_by('-uploaded_at')[:5]
    recent_records = MedicalRecord.objects.select_related('patient').order_by('-created_at')[:5]

    context = {
        'total_patients': total_patients,
        'total_records': total_records,
        'total_datasets': total_datasets,
        'avg_age': avg_age,
        'avg_heart_rate': avg_heart_rate,
        'age_chart_base64': age_chart_base64,
        'gender_chart_base64': gender_chart_base64,
        'age_analytics': age_analytics,
        'gender_analytics': gender_analytics,
        'outcome_analytics': outcome_analytics,
        'stratified_outcomes': stratified_outcomes,
        'positivity_rate': positivity_rate,
        'recent_patients': recent_patients,
        'recent_datasets': recent_datasets,
        'recent_records': recent_records,
    }
    return render(request, 'dashboard/index.html', context)
