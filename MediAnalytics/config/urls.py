"""
MediAnalytics URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls', namespace='dashboard')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('patients/', include('patients.urls', namespace='patients')),
    path('medical-records/', include('medical_records.urls', namespace='medical_records')),
    path('datasets/', include('datasets.urls', namespace='datasets')),
    path('analytics/', include('analytics.urls', namespace='analytics')),
    path('reports/', include('reports.urls', namespace='reports')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
