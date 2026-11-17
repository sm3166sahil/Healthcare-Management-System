"""
Pandas Healthcare Data Analysis Engine
FDS Unit 4 Coverage: Series, DataFrames, loc/iloc, Filtering, GroupBy,
Pivot Tables, Cross-Tabulation, Windowing, Time Series, Vectorization.
"""

import pandas as pd
import numpy as np


class HealthcarePandasAnalyzer:
    """
    Comprehensive Pandas data manipulation and analysis engine covering Unit 4.
    Dynamically adapts to available columns in any uploaded healthcare dataset.
    """

    def __init__(self, df):
        if not isinstance(df, pd.DataFrame):
            self.df = pd.DataFrame(df)
        else:
            self.df = df.copy()

    # ---------------------------------------------------------
    # A. SERIES & DATAFRAME INSPECTION & SLICING (Unit 4)
    # ---------------------------------------------------------
    def inspect_dataframe(self):
        """Returns fundamental DataFrame properties and structural summary."""
        return {
            'shape': self.df.shape,
            'rows': len(self.df),
            'columns': list(self.df.columns),
            'dtypes': {col: str(dtype) for col, dtype in self.df.dtypes.items()},
            'memory_usage_kb': round(self.df.memory_usage(deep=True).sum() / 1024, 2),
            'null_counts': self.df.isnull().sum().to_dict(),
            'numerical_columns': list(self.df.select_dtypes(include=[np.number]).columns),
            'categorical_columns': list(self.df.select_dtypes(include=['object', 'category']).columns),
        }

    def demonstrate_loc_iloc(self):
        """Demonstrates explicit label-based (loc) and integer-based (iloc) slicing."""
        if len(self.df) == 0:
            return {}

        iloc_slice = self.df.iloc[:5, :min(4, len(self.df.columns))].to_dict(orient='records')
        first_col = self.df.columns[0]
        loc_slice = self.df.loc[:4, [first_col]].to_dict(orient='records')

        return {
            'iloc_first_5x4': iloc_slice,
            'loc_sample': loc_slice
        }

    # ---------------------------------------------------------
    # B. GROUPBY & MULTI-METRIC AGGREGATION (Unit 4)
    # ---------------------------------------------------------
    def perform_groupby_analysis(self, group_col=None, value_col=None):
        """Performs robust multi-level groupby aggregation."""
        cats = self.df.select_dtypes(include=['object', 'category']).columns
        nums = self.df.select_dtypes(include=[np.number]).columns

        if group_col is None or group_col not in self.df.columns:
            group_col = cats[0] if len(cats) > 0 else None

        if value_col is None or value_col not in self.df.columns:
            value_col = nums[0] if len(nums) > 0 else None

        if not group_col or not value_col:
            return {'error': 'Insufficient categorical or numerical columns for GroupBy.'}

        agg_df = self.df.groupby(group_col)[value_col].agg([
            ('Count', 'count'),
            ('Mean', 'mean'),
            ('Std_Dev', 'std'),
            ('Median', 'median'),
            ('Min', 'min'),
            ('Max', 'max')
        ]).round(2).reset_index()

        records = []
        for row in agg_df.to_dict(orient='records'):
            row['group_value'] = row.get(group_col, '')
            records.append(row)

        return {
            'group_column': group_col,
            'value_column': value_col,
            'records': records,
            'columns': list(agg_df.columns)
        }

    # ---------------------------------------------------------
    # C. PIVOT TABLES & CROSSTABULATION (Unit 4)
    # ---------------------------------------------------------
    def create_pivot_table(self, index_col=None, columns_col=None, value_col=None):
        """Creates dynamic pivot table with margins/totals."""
        cats = list(self.df.select_dtypes(include=['object', 'category']).columns)
        nums = list(self.df.select_dtypes(include=[np.number]).columns)

        if len(cats) >= 2 and len(nums) >= 1:
            idx = index_col if index_col in cats else cats[0]
            col = columns_col if columns_col in cats and columns_col != idx else cats[1]
            val = value_col if value_col in nums else nums[0]

            pivot = pd.pivot_table(
                self.df,
                index=idx,
                columns=col,
                values=val,
                aggfunc='mean',
                fill_value=0.0,
                margins=True,
                margins_name='Overall Mean'
            ).round(2)

            return {
                'index_col': idx,
                'columns_col': col,
                'value_col': val,
                'html': pivot.to_html(classes='table table-bordered table-striped table-sm text-center'),
                'records': pivot.reset_index().to_dict(orient='records')
            }
        return {'notice': 'Pivot table requires at least 2 categorical and 1 numerical column.'}

    def create_crosstab(self, row_col=None, col_col=None):
        """Generates contingency matrix using pd.crosstab."""
        cats = list(self.df.select_dtypes(include=['object', 'category']).columns)
        if len(cats) >= 2:
            r = row_col if row_col in cats else cats[0]
            c = col_col if col_col in cats and col_col != r else cats[1]

            ct = pd.crosstab(self.df[r], self.df[c], margins=True, margins_name='Total')
            return {
                'row_col': r,
                'col_col': c,
                'html': ct.to_html(classes='table table-hover table-bordered table-sm text-center')
            }
        return {'notice': 'Contingency crosstab requires at least two categorical features.'}

    # ---------------------------------------------------------
    # D. TIME SERIES & ROLLING WINDOW OPERATIONS (Unit 4)
    # ---------------------------------------------------------
    def perform_window_and_timeseries(self):
        """Demonstrates rolling window operations and date arithmetic."""
        num_cols = self.df.select_dtypes(include=[np.number]).columns
        if len(num_cols) == 0:
            return {}

        metric_col = num_cols[0]
        series = self.df[metric_col].dropna().reset_index(drop=True)

        rolling_7 = series.rolling(window=7, min_periods=1).mean().round(2)
        rolling_std = series.rolling(window=7, min_periods=1).std().round(2)
        expanding_mean = series.expanding(min_periods=1).mean().round(2)

        n = min(14, len(series))
        comparison_df = pd.DataFrame({
            'Index': list(range(1, n + 1)),
            'Observed_Value': series.head(n).values,
            '7_Day_Moving_Avg': rolling_7.head(n).values,
            '7_Day_Moving_Std': rolling_std.head(n).fillna(0).values,
            'Expanding_Mean': expanding_mean.head(n).values
        })

        return {
            'metric': metric_col,
            'table': comparison_df.to_dict(orient='records')
        }
