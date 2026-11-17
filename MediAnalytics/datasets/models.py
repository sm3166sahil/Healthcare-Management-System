import os
from django.db import models
from django.contrib.auth.models import User


class UploadedDataset(models.Model):
    """
    Model representing uploaded healthcare CSV datasets.
    Stores metadata including dimensions, column names, cleaning status, and file paths.
    """
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='uploaded_datasets/')
    file_size = models.PositiveIntegerField(default=0, help_text="File size in bytes")
    row_count = models.PositiveIntegerField(null=True, blank=True)
    column_count = models.PositiveIntegerField(null=True, blank=True)
    column_names = models.TextField(blank=True, help_text="Comma-separated column names")
    is_cleaned = models.BooleanField(default=False)
    cleaned_file = models.FileField(upload_to='cleaned_datasets/', null=True, blank=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='datasets_uploaded'
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-uploaded_at']
        verbose_name = 'Uploaded Dataset'
        verbose_name_plural = 'Uploaded Datasets'

    def __str__(self):
        return self.title

    @property
    def file_name(self):
        return os.path.basename(self.file.name) if self.file else ''

    @property
    def filename(self):
        return self.file_name

    @property
    def name(self):
        return self.title

    @name.setter
    def name(self, value):
        self.title = value

    @property
    def rows(self):
        return self.row_count

    @property
    def columns(self):
        return self.column_count

    @property
    def status(self):
        return "Cleaned" if self.is_cleaned else "Raw"

    @property
    def file_size_display(self):
        """Format file size in KB or MB."""
        if self.file_size < 1024:
            return f"{self.file_size} B"
        elif self.file_size < 1024 * 1024:
            return f"{self.file_size / 1024:.1f} KB"
        else:
            return f"{self.file_size / (1024 * 1024):.2f} MB"

    @property
    def active_file_path(self):
        """Returns path of cleaned file if available, otherwise original file."""
        if self.is_cleaned and self.cleaned_file:
            return self.cleaned_file.path
        return self.file.path if self.file else ''
