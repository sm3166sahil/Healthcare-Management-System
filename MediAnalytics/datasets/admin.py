from django.contrib import admin
from .models import UploadedDataset


@admin.register(UploadedDataset)
class UploadedDatasetAdmin(admin.ModelAdmin):
    list_display = ('title', 'file_size_display', 'row_count', 'column_count', 'is_cleaned', 'uploaded_by', 'uploaded_at')
    list_filter = ('is_cleaned', 'uploaded_at')
    search_fields = ('title', 'description', 'column_names')
    readonly_fields = ('file_size', 'row_count', 'column_count', 'column_names', 'uploaded_at', 'updated_at')
