from django.contrib import admin
from .models import GeneratedReport


@admin.register(GeneratedReport)
class GeneratedReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'report_type', 'dataset', 'generated_by', 'generated_at')
    list_filter = ('report_type', 'generated_at')
    search_fields = ('title', 'summary', 'dataset__title')
    readonly_fields = ('generated_at',)
