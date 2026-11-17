from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
import numpy as np
import pandas as pd
from analytics.numpy_analysis import HealthcareNumpyAnalyzer
from analytics.pandas_analysis import HealthcarePandasAnalyzer
from analytics.data_cleaning import HealthcareDataCleaner
from analytics.statistical_analysis import HealthcareStatisticalAnalyzer


class AnalyticsUnitTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='analyst', password='password123')
        self.client.login(username='analyst', password='password123')

        # Test clinical dataset
        self.df = pd.DataFrame({
            'Patient_ID': ['PAT-0001', 'PAT-0002', 'PAT-0003', 'PAT-0004', 'PAT-0005', 'PAT-0001'],
            'Age': [45, 62, 58, np.nan, 71, 45],
            'Gender': ['Male', 'Female', 'M', 'Female', 'Other', 'Male'],
            'Heart_Rate': [72.0, 85.0, 92.0, 68.0, 220.0, 72.0],
            'Cholesterol': [190.0, 240.0, np.nan, 180.0, 290.0, 190.0],
            'Outcome': ['Negative', 'Positive', 'Negative', 'Inconclusive', 'Positive', 'Negative']
        })

    def test_numpy_computation(self):
        data = [72, 85, 90, 68, 74]
        analyzer = HealthcareNumpyAnalyzer(data)
        stats = analyzer.compute_statistics()
        self.assertEqual(stats['count'], 5)
        self.assertAlmostEqual(stats['mean'], 77.8)

    def test_pandas_groupby(self):
        analyzer = HealthcarePandasAnalyzer(self.df)
        res = analyzer.perform_groupby_analysis('Outcome', 'Heart_Rate')
        self.assertIn('records', res)

    def test_data_cleaning_pipeline(self):
        cleaner = HealthcareDataCleaner(self.df)
        # Duplicate detection
        dup_res = cleaner.remove_duplicates()
        self.assertEqual(dup_res['removed_duplicates'], 1)

        # Impute missing values with mean
        imp_res = cleaner.handle_missing_values(strategy='mean')
        self.assertGreater(imp_res['cleaned_count'], 0)

        # Outlier handling via IQR capping
        outlier_res = cleaner.handle_outliers('Heart_Rate', method='cap')
        self.assertEqual(outlier_res['method'], 'cap')

    def test_views_accessible(self):
        for route in ['numpy', 'pandas', 'statistics', 'visualization', 'json_regex', 'fds_coverage']:
            response = self.client.get(reverse(f'analytics:{route}'))
            self.assertEqual(response.status_code, 200)
