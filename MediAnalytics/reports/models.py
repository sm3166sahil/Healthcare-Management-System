import os
from django.db import models
from django.contrib.auth.models import User
from datasets.models import UploadedDataset


class GeneratedReport(models.Model):
    """
    Model representing generated analytical and clinical summary reports (PDF / CSV).
    """
    REPORT_TYPES = (
        ('PDF', 'PDF Analytical Report'),
        ('CSV', 'CSV Data Summary Export'),
    )

    title = models.CharField(max_length=255)
    report_type = models.CharField(max_length=20, choices=REPORT_TYPES, default='PDF')
    dataset = models.ForeignKey(
        UploadedDataset,
        on_delete=models.CASCADE,
        related_name='reports',
        null=True,
        blank=True
    )
    file = models.FileField(upload_to='reports/')
    summary = models.TextField(blank=True, help_text="Executive summary of key findings in this report")
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reports_generated'
    )
    generated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-generated_at']
        verbose_name = 'Generated Report'
        verbose_name_plural = 'Generated Reports'

    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()}) - {self.generated_at.strftime('%Y-%m-%d %H:%M')}"

    @property
    def file_name(self):
        return os.path.basename(self.file.name) if self.file else ''

    @property
    def file_size_display(self):
        if not self.file or not os.path.exists(self.file.path):
            return "N/A"
        size = os.path.getsize(self.file.path)
        if size < 1024:
            return f"{size} B"
        elif size < 1024 * 1024:
            return f"{size / 1024:.1f} KB"
        return f"{size / (1024 * 1024):.2f} MB"
