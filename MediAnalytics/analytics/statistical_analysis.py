"""
Statistical Healthcare Analysis Engine
FDS Unit 1 & Unit 4 Coverage: Descriptive Statistics, Pearson & Spearman Correlation,
Distribution Characteristics, Skewness, Kurtosis, and Clinical Interpretations.
"""

import pandas as pd
import numpy as np


class HealthcareStatisticalAnalyzer:
    """
    Statistical engine calculating descriptive, inferential, and correlation matrices
    with academic narrative generation for healthcare datasets.
    """

    def __init__(self, df):
        self.df = df.copy()

    # ---------------------------------------------------------
    # 1. DESCRIPTIVE STATISTICS TABLE
    # ---------------------------------------------------------
    def get_descriptive_statistics(self):
        """Calculates comprehensive univariate statistical properties for numeric columns."""
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.empty:
            return []

        stats_list = []
        for col in numeric_df.columns:
            series = numeric_df[col].dropna()
            if len(series) == 0:
                continue

            mean = float(series.mean())
            std = float(series.std())
            median = float(series.median())
            mode_s = series.mode()
            mode = float(mode_s[0]) if not mode_s.empty else mean
            min_val = float(series.min())
            max_val = float(series.max())
            val_range = max_val - min_val
            variance = float(series.var())
            q1 = float(series.quantile(0.25))
            q3 = float(series.quantile(0.75))
            iqr = q3 - q1
            skewness = float(series.skew()) if len(series) > 2 else 0.0
            kurtosis = float(series.kurtosis()) if len(series) > 3 else 0.0

            stats_list.append({
                'metric': col,
                'count': len(series),
                'mean': round(mean, 2),
                'std': round(std, 2),
                'variance': round(variance, 2),
                'median': round(median, 2),
                'mode': round(mode, 2),
                'min': round(min_val, 2),
                'max': round(max_val, 2),
                'range': round(val_range, 2),
                'q1': round(q1, 2),
                'q3': round(q3, 2),
                'iqr': round(iqr, 2),
                'skewness': round(skewness, 2),
                'kurtosis': round(kurtosis, 2)
            })

        return stats_list

    # ---------------------------------------------------------
    # 2. CORRELATION ANALYSIS (PEARSON & SPEARMAN)
    # ---------------------------------------------------------
    def get_correlation_matrix(self, method='pearson'):
        """Computes pairwise correlation matrix (Pearson or Spearman)."""
        numeric_df = self.df.select_dtypes(include=[np.number])
        if numeric_df.shape[1] < 2:
            return {'error': 'At least two numerical columns are required for correlation analysis.'}

        corr = numeric_df.corr(method=method).round(3)
        cols = list(corr.columns)
        matrix = []

        for i, row_col in enumerate(cols):
            row_vals = []
            for j, col_col in enumerate(cols):
                row_vals.append({
                    'val': float(corr.iloc[i, j]),
                    'is_diagonal': i == j
                })
            matrix.append({'name': row_col, 'values': row_vals})

        # Identify top pairwise associations (excluding self-correlation)
        pairs = []
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                val = float(corr.iloc[i, j])
                if not np.isnan(val):
                    pairs.append({
                        'var1': cols[i],
                        'var2': cols[j],
                        'correlation': val,
                        'abs_corr': abs(val),
                        'strength': 'Strong' if abs(val) >= 0.7 else ('Moderate' if abs(val) >= 0.4 else 'Weak')
                    })
        pairs.sort(key=lambda x: x['abs_corr'], reverse=True)

        return {
            'columns': cols,
            'matrix': matrix,
            'top_pairs': pairs[:8],
            'method': method.title()
        }

    # ---------------------------------------------------------
    # 3. GROUP COMPARISONS
    # ---------------------------------------------------------
    def get_group_comparisons(self, group_by='Outcome'):
        """Computes metric distributions stratified by a categorical outcome or group."""
        if group_by not in self.df.columns:
            cats = self.df.select_dtypes(include=['object', 'category']).columns
            if len(cats) > 0:
                group_by = cats[0]
            else:
                return {}

        num_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(num_cols) == 0:
            return {}

        results = []
        for col in num_cols[:5]:  # Top 5 physiological measures
            grouped = self.df.groupby(group_by)[col].agg(['count', 'mean', 'std']).round(2).reset_index()
            records = []
            for row in grouped.to_dict(orient='records'):
                records.append({
                    'group': row.get(group_by, ''),
                    'count': row.get('count', 0),
                    'mean': row.get('mean', 0),
                    'std': row.get('std', 0),
                })
            results.append({
                'metric': col,
                'groups': records
            })

        return {
            'group_column': group_by,
            'comparisons': results
        }
