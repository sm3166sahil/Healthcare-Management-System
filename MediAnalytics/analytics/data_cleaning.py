"""
Healthcare Data Cleaning and Preprocessing Engine
FDS Unit 4 & Module 5 Coverage: Missing Values Imputation, Duplicate Handling,
IQR Outlier Detection & Capping, Data Normalization, Type Casting.
"""

import pandas as pd
import numpy as np


class HealthcareDataCleaner:
    """
    Robust data cleaning and preprocessing engine for clinical records.
    Maintains reproducibility, audit history, and before-and-after metrics.
    """

    def __init__(self, df):
        self.original_df = df.copy()
        self.df = df.copy()
        self.operations_performed = []

    # ---------------------------------------------------------
    # 1. AUDIT & DIAGNOSTIC INSPECTION
    # ---------------------------------------------------------
    def audit_quality(self):
        """Analyzes missing values, duplicate records, and data types."""
        total_rows = len(self.df)
        total_cols = len(self.df.columns)

        # Missing values analysis
        null_counts = self.df.isnull().sum()
        null_pct = (null_counts / total_rows * 100).round(2) if total_rows > 0 else 0
        missing_summary = []
        for col in self.df.columns:
            if null_counts[col] > 0:
                missing_summary.append({
                    'column': col,
                    'null_count': int(null_counts[col]),
                    'null_pct': float(null_pct[col]),
                    'dtype': str(self.df[col].dtype)
                })

        # Duplicate records analysis
        duplicate_count = int(self.df.duplicated().sum())
        duplicate_pct = round(duplicate_count / total_rows * 100, 2) if total_rows > 0 else 0

        # Outlier diagnostics across numeric features
        outlier_summary = []
        num_cols = self.df.select_dtypes(include=[np.number]).columns
        for col in num_cols:
            s = self.df[col].dropna()
            if len(s) > 4:
                q1 = s.quantile(0.25)
                q3 = s.quantile(0.75)
                iqr = q3 - q1
                lb = q1 - 1.5 * iqr
                ub = q3 + 1.5 * iqr
                outliers = s[(s < lb) | (s > ub)]
                if len(outliers) > 0:
                    outlier_summary.append({
                        'column': col,
                        'q1': round(float(q1), 2),
                        'q3': round(float(q3), 2),
                        'iqr': round(float(iqr), 2),
                        'lower_bound': round(float(lb), 2),
                        'upper_bound': round(float(ub), 2),
                        'outlier_count': int(len(outliers)),
                        'outlier_pct': round(float(len(outliers) / len(s) * 100), 2)
                    })

        return {
            'total_rows': total_rows,
            'total_columns': total_cols,
            'total_missing_cells': int(null_counts.sum()),
            'missing_summary': missing_summary,
            'duplicate_count': duplicate_count,
            'duplicate_pct': duplicate_pct,
            'outlier_summary': outlier_summary
        }

    # ---------------------------------------------------------
    # 2. MISSING VALUES HANDLING
    # ---------------------------------------------------------
    def handle_missing_values(self, strategy='mean', column=None, custom_value=None):
        """
        Imputes or eliminates missing values based on chosen clinical strategy.
        Strategies: 'drop_rows', 'mean', 'median', 'mode', 'custom'
        """
        before_nulls = int(self.df.isnull().sum().sum())

        if strategy == 'drop_rows':
            if column and column in self.df.columns:
                self.df = self.df.dropna(subset=[column]).reset_index(drop=True)
                desc = f"Dropped rows with missing values in column '{column}'."
            else:
                self.df = self.df.dropna().reset_index(drop=True)
                desc = "Dropped all rows containing any missing value."
            self.operations_performed.append(desc)

        elif strategy == 'mean':
            if column and column in self.df.columns:
                target_cols = [column]
            else:
                target_cols = list(self.df.columns)

            imputed_cols = []
            for col in target_cols:
                num_series = pd.to_numeric(self.df[col], errors='coerce')
                if num_series.notnull().sum() > 0:
                    mean_val = float(num_series.mean())
                    if not np.isnan(mean_val):
                        self.df[col] = num_series.fillna(round(mean_val, 2))
                        imputed_cols.append(col)
                else:
                    mode_series = self.df[col].dropna().mode()
                    if not mode_series.empty:
                        self.df[col] = self.df[col].fillna(mode_series[0])
                        imputed_cols.append(col)
            self.operations_performed.append(f"Imputed missing values with Mean/Mode for columns: {imputed_cols}.")

        elif strategy == 'median':
            if column and column in self.df.columns:
                target_cols = [column]
            else:
                target_cols = list(self.df.columns)

            imputed_cols = []
            for col in target_cols:
                num_series = pd.to_numeric(self.df[col], errors='coerce')
                if num_series.notnull().sum() > 0:
                    median_val = float(num_series.median())
                    if not np.isnan(median_val):
                        self.df[col] = num_series.fillna(round(median_val, 2))
                        imputed_cols.append(col)
                else:
                    mode_series = self.df[col].dropna().mode()
                    if not mode_series.empty:
                        self.df[col] = self.df[col].fillna(mode_series[0])
                        imputed_cols.append(col)
            self.operations_performed.append(f"Imputed missing values with Median/Mode for columns: {imputed_cols}.")

        elif strategy == 'mode':
            if column and column in self.df.columns:
                target_cols = [column]
            else:
                target_cols = list(self.df.columns)

            imputed_cols = []
            for col in target_cols:
                mode_series = self.df[col].dropna().mode()
                if not mode_series.empty:
                    self.df[col] = self.df[col].fillna(mode_series[0])
                    imputed_cols.append(col)
            self.operations_performed.append(f"Imputed categorical missing values with Mode for columns: {imputed_cols}.")

        elif strategy == 'custom' and custom_value is not None:
            if column and column in self.df.columns:
                self.df[column] = self.df[column].fillna(custom_value)
                self.operations_performed.append(f"Replaced missing values in '{column}' with constant: {custom_value}.")

        after_nulls = int(self.df.isnull().sum().sum())
        return {'before_nulls': before_nulls, 'after_nulls': after_nulls, 'cleaned_count': before_nulls - after_nulls}

    # ---------------------------------------------------------
    # 3. DUPLICATE ELIMINATION
    # ---------------------------------------------------------
    def remove_duplicates(self):
        """Drops exact duplicate records."""
        before = len(self.df)
        self.df = self.df.drop_duplicates().reset_index(drop=True)
        removed = before - len(self.df)
        self.operations_performed.append(f"Removed {removed} duplicate rows using drop_duplicates().")
        return {'removed_duplicates': removed, 'remaining_rows': len(self.df)}

    # ---------------------------------------------------------
    # 4. OUTLIER HANDLING (IQR WINSORIZATION / TRIMMING)
    # ---------------------------------------------------------
    def handle_outliers(self, column, method='cap'):
        """
        Handles outliers detected via Interquartile Range (IQR).
        Methods: 'cap' (winsorize to 1.5*IQR bounds), 'remove' (drop row).
        """
        if column not in self.df.columns:
            return {'error': f"Column '{column}' not found in dataset."}

        num_s = pd.to_numeric(self.df[column], errors='coerce')
        if num_s.notnull().sum() == 0:
            return {'error': f"Column '{column}' is not numeric and contains no numerical values."}

        self.df[column] = num_s
        s = num_s.dropna()
        q1 = float(s.quantile(0.25))
        q3 = float(s.quantile(0.75))
        iqr = q3 - q1
        lb = q1 - 1.5 * iqr
        ub = q3 + 1.5 * iqr

        if method == 'cap':
            # Winsorize / Cap boundaries
            self.df[column] = self.df[column].clip(lower=lb, upper=ub)
            self.operations_performed.append(f"Capped extreme outliers in '{column}' to range [{lb:.2f}, {ub:.2f}].")
            return {'method': 'cap', 'lower_bound': lb, 'upper_bound': ub}

        elif method == 'remove':
            before = len(self.df)
            self.df = self.df[(self.df[column] >= lb) & (self.df[column] <= ub)].reset_index(drop=True)
            dropped = before - len(self.df)
            self.operations_performed.append(f"Removed {dropped} outlier rows from '{column}' exceeding 1.5*IQR bounds.")
            return {'method': 'remove', 'dropped': dropped, 'remaining_rows': len(self.df)}

    # ---------------------------------------------------------
    # 5. STRING NORMALIZATION & CATEGORY STANDARDIZATION
    # ---------------------------------------------------------
    def standardize_categories(self, column=None):
        """Standardizes casing, strips whitespace, and unifies categorical representations."""
        cat_cols = [column] if column and column in self.df.columns else self.df.select_dtypes(include=['object']).columns

        for col in cat_cols:
            if col in self.df.columns and self.df[col].dtype == 'object':
                # Strip leading/trailing whitespaces
                self.df[col] = self.df[col].astype(str).str.strip()

                # Map common gender variations
                if 'gender' in col.lower() or 'sex' in col.lower():
                    mapping = {
                        'm': 'Male', 'male': 'Male', 'MALE': 'Male', 'M': 'Male',
                        'f': 'Female', 'female': 'Female', 'FEMALE': 'Female', 'F': 'Female',
                        'other': 'Other', 'OTHER': 'Other'
                    }
                    self.df[col] = self.df[col].replace(mapping)

                # Map common outcome variations
                if 'outcome' in col.lower() or 'result' in col.lower():
                    mapping = {
                        'pos': 'Positive', 'positive': 'Positive', 'POSITIVE': 'Positive',
                        'neg': 'Negative', 'negative': 'Negative', 'NEGATIVE': 'Negative',
                        'inc': 'Inconclusive', 'inconclusive': 'Inconclusive', 'INCONCLUSIVE': 'Inconclusive'
                    }
                    self.df[col] = self.df[col].replace(mapping)

        self.operations_performed.append("Standardized categorical columns (whitespace stripped, title-cased labels).")
        return {'status': 'success'}

    # ---------------------------------------------------------
    # 6. EXECUTIVE CLEANING SUMMARY
    # ---------------------------------------------------------
    def get_summary(self):
        """Returns comprehensive before-vs-after comparison."""
        return {
            'rows_before': len(self.original_df),
            'rows_after': len(self.df),
            'cols_before': len(self.original_df.columns),
            'cols_after': len(self.df.columns),
            'nulls_before': int(self.original_df.isnull().sum().sum()),
            'nulls_after': int(self.df.isnull().sum().sum()),
            'duplicates_before': int(self.original_df.duplicated().sum()),
            'duplicates_after': int(self.df.duplicated().sum()),
            'operations': self.operations_performed
        }
