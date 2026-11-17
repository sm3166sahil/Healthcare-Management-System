from django.contrib import admin
from .models import CleaningHistory, AnalysisHistory


@admin.register(CleaningHistory)
class CleaningHistoryAdmin(admin.ModelAdmin):
    list_display = ('dataset', 'cleaning_action', 'rows_before', 'rows_after', 'cleaned_by', 'created_at')
    list_filter = ('cleaning_action', 'created_at')
    search_fields = ('dataset__title', 'cleaning_action', 'description')
    readonly_fields = ('created_at',)


@admin.register(AnalysisHistory)
class AnalysisHistoryAdmin(admin.ModelAdmin):
    list_display = ('analysis_type', 'dataset', 'generated_by', 'created_at')
    list_filter = ('analysis_type', 'created_at')
    search_fields = ('analysis_type', 'dataset__title', 'results_summary')
    readonly_fields = ('created_at',)
