"""
Healthcare Data Visualization Engine using Matplotlib and Seaborn
FDS Unit 5 Coverage: Univariate, Bivariate, and Multivariate Clinical Visualizations.
Uses non-interactive 'Agg' backend for thread-safe Django rendering.
"""

import os
import uuid
from datetime import datetime
import matplotlib
matplotlib.use('Agg')  # Thread-safe headless rendering backend
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from django.conf import settings

# Set global visual style
sns.set_theme(style="whitegrid", palette="deep")
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cbd5e0'
plt.rcParams['axes.linewidth'] = 0.8


class HealthcareVisualizer:
    """
    Renders publication-ready clinical visualizations saved to media/charts/.
    Adapts dynamically to dataset columns.
    """

    def __init__(self, df):
        self.df = df.copy()
        self.charts_dir = os.path.join(settings.MEDIA_ROOT, 'charts')
        os.makedirs(self.charts_dir, exist_ok=True)

    def _get_save_path(self, prefix='chart'):
        unique_id = uuid.uuid4().hex[:8]
        filename = f"{prefix}_{unique_id}.png"
        abs_path = os.path.join(self.charts_dir, filename)
        rel_url = f"{settings.MEDIA_URL}charts/{filename}"
        return abs_path, rel_url

    # ---------------------------------------------------------
    # A. UNIVARIATE NUMERICAL PLOTS (Unit 5)
    # ---------------------------------------------------------
    def plot_histogram_kde(self, column):
        """Generates histogram with Kernel Density Estimation (KDE)."""
        if column not in self.df.columns:
            return None

        fig, ax = plt.subplots(figsize=(8, 4.5))
        data = self.df[column].dropna()
        sns.histplot(data, kde=True, color='#2c7a7b', ax=ax, bins=25, edgecolor='white', alpha=0.6)
        ax.set_title(f'Distribution of {column.replace("_", " ")} (Histogram & KDE)', fontsize=13, fontweight='bold', color='#1a365d')
        ax.set_xlabel(column.replace('_', ' '), fontsize=11)
        ax.set_ylabel('Frequency', fontsize=11)
        fig.tight_layout()

        abs_path, rel_url = self._get_save_path('hist')
        fig.savefig(abs_path, dpi=130)
        plt.close(fig)
        return rel_url

    def plot_boxplot(self, column):
        """Generates box plot displaying quartiles, median, and outliers."""
        if column not in self.df.columns:
            return None

        fig, ax = plt.subplots(figsize=(7, 4))
        data = self.df[column].dropna()
        sns.boxplot(x=data, color='#3182ce', ax=ax, flierprops={'marker': 'o', 'markersize': 5, 'markerfacecolor': '#e53e3e'})
        ax.set_title(f'Box Plot Analysis: {column.replace("_", " ")}', fontsize=13, fontweight='bold', color='#1a365d')
        ax.set_xlabel(column.replace('_', ' '), fontsize=11)
        fig.tight_layout()

        abs_path, rel_url = self._get_save_path('box')
        fig.savefig(abs_path, dpi=130)
        plt.close(fig)
        return rel_url

    def plot_violin(self, column, group_by=None):
        """Generates violin plot showing multimodal probability densities."""
        if column not in self.df.columns:
            return None

        fig, ax = plt.subplots(figsize=(8, 4.5))
        if group_by and group_by in self.df.columns:
            sns.violinplot(data=self.df, x=group_by, y=column, palette='Set2', ax=ax, inner='quartile')
            ax.set_title(f'{column.replace("_", " ")} Density stratified by {group_by.replace("_", " ")}', fontsize=13, fontweight='bold', color='#1a365d')
        else:
            sns.violinplot(y=self.df[column].dropna(), color='#38a169', ax=ax, inner='quartile')
            ax.set_title(f'Violin Density Plot: {column.replace("_", " ")}', fontsize=13, fontweight='bold', color='#1a365d')

        fig.tight_layout()
        abs_path, rel_url = self._get_save_path('violin')
        fig.savefig(abs_path, dpi=130)
        plt.close(fig)
        return rel_url

    # ---------------------------------------------------------
    # B. UNIVARIATE CATEGORICAL PLOTS (Unit 5)
    # ---------------------------------------------------------
    def plot_countplot(self, column):
        """Generates count / frequency bar chart for categorical features."""
        if column not in self.df.columns:
            return None

        fig, ax = plt.subplots(figsize=(7, 4.5))
        sns.countplot(data=self.df, x=column, palette='Blues_r', ax=ax, order=self.df[column].value_counts().index)
        ax.set_title(f'Frequency Count: {column.replace("_", " ")}', fontsize=13, fontweight='bold', color='#1a365d')
        ax.set_xlabel(column.replace('_', ' '), fontsize=11)
        ax.set_ylabel('Patient Count', fontsize=11)
        for p in ax.patches:
            height = p.get_height()
            if not np.isnan(height):
                ax.annotate(f'{int(height)}', (p.get_x() + p.get_width() / 2., height),
                            ha='center', va='bottom', fontsize=9, xytext=(0, 3), textcoords='offset points')
        fig.tight_layout()

        abs_path, rel_url = self._get_save_path('count')
        fig.savefig(abs_path, dpi=130)
        plt.close(fig)
        return rel_url

    def plot_pie_chart(self, column):
        """Generates proportion pie chart."""
        if column not in self.df.columns:
            return None

        counts = self.df[column].value_counts()
        if len(counts) == 0:
            return None

        fig, ax = plt.subplots(figsize=(6, 5))
        colors_list = ['#1a365d', '#2c7a7b', '#3182ce', '#38a169', '#d69e2e', '#e53e3e']
        ax.pie(counts, labels=counts.index, autopct='%1.1f%%', startangle=140, colors=colors_list[:len(counts)],
               wedgeprops={'edgecolor': 'white', 'linewidth': 1.5})
        ax.set_title(f'Proportional Share: {column.replace("_", " ")}', fontsize=13, fontweight='bold', color='#1a365d')
        fig.tight_layout()

        abs_path, rel_url = self._get_save_path('pie')
        fig.savefig(abs_path, dpi=130)
        plt.close(fig)
        return rel_url

    # ---------------------------------------------------------
    # C. BIVARIATE NUMERICAL & REGRESSION PLOTS (Unit 5)
    # ---------------------------------------------------------
    def plot_scatter_reg(self, x_col, y_col, hue=None):
        """Generates bivariate scatter plot with optional linear regression line."""
        if x_col not in self.df.columns or y_col not in self.df.columns:
            return None

        fig, ax = plt.subplots(figsize=(8, 5))
        if hue and hue in self.df.columns:
            sns.scatterplot(data=self.df, x=x_col, y=y_col, hue=hue, palette='tab10', alpha=0.75, s=60, ax=ax)
        else:
            sns.regplot(data=self.df, x=x_col, y=y_col, scatter_kws={'alpha': 0.6, 'color': '#2c7a7b'}, line_kws={'color': '#e53e3e'}, ax=ax)

        ax.set_title(f'{y_col.replace("_", " ")} vs. {x_col.replace("_", " ")}', fontsize=13, fontweight='bold', color='#1a365d')
        ax.set_xlabel(x_col.replace('_', ' '), fontsize=11)
        ax.set_ylabel(y_col.replace('_', ' '), fontsize=11)
        fig.tight_layout()

        abs_path, rel_url = self._get_save_path('scatter')
        fig.savefig(abs_path, dpi=130)
        plt.close(fig)
        return rel_url

    # ---------------------------------------------------------
    # D. MULTIVARIATE CORRELATION HEATMAP (Unit 5)
    # ---------------------------------------------------------
    def plot_correlation_heatmap(self):
        """Generates Seaborn correlation matrix heatmap for all numeric features."""
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return None

        corr = numeric_df.corr()
        fig, ax = plt.subplots(figsize=(9, 7))
        mask = np.triu(np.ones_like(corr, dtype=bool))
        sns.heatmap(corr, annot=True, fmt='.2f', cmap='vlag', vmin=-1, vmax=1,
                    square=True, linewidths=0.5, cbar_kws={"shrink": .8}, ax=ax, mask=mask)
        ax.set_title('Correlation Heatmap (Numeric Biomarkers)', fontsize=14, fontweight='bold', color='#1a365d')
        fig.tight_layout()

        abs_path, rel_url = self._get_save_path('heatmap')
        fig.savefig(abs_path, dpi=130)
        plt.close(fig)
        return rel_url
