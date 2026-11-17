from django.db import models
from django.contrib.auth.models import User
from datasets.models import UploadedDataset


class CleaningHistory(models.Model):
    """
    Log of data cleaning and pre-processing operations performed on a dataset.
    """
    dataset = models.ForeignKey(UploadedDataset, on_delete=models.CASCADE, related_name='cleaning_logs')
    cleaned_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    cleaning_action = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    rows_before = models.IntegerField(null=True, blank=True)
    rows_after = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Cleaning History'
        verbose_name_plural = 'Cleaning Histories'

    def __str__(self):
        return f'{self.dataset.title} - {self.cleaning_action} ({self.created_at.strftime("%Y-%m-%d %H:%M")})'


class AnalysisHistory(models.Model):
    """
    Records analytical executions (NumPy, Pandas, Statistics, Visualizations)
    along with parameters and output summaries.
    """
    dataset = models.ForeignKey(
        UploadedDataset,
        on_delete=models.CASCADE,
        related_name='analysis_logs',
        null=True,
        blank=True
    )
    analysis_type = models.CharField(max_length=100)
    parameters = models.TextField(blank=True, help_text="JSON serialized input parameters")
    results_summary = models.TextField(blank=True, help_text="Executive summary of computation results")
    generated_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Analysis History'
        verbose_name_plural = 'Analysis Histories'

    def __str__(self):
        dataset_name = self.dataset.title if self.dataset else "Ad-hoc"
        return f'{self.analysis_type} on {dataset_name} ({self.created_at.strftime("%Y-%m-%d %H:%M")})'
