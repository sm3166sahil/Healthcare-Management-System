from django.urls import path
from . import views

app_name = 'analytics'

urlpatterns = [
    path('cleaning/', views.cleaning_view, name='cleaning'),
    path('numpy/', views.numpy_view, name='numpy'),
    path('pandas/', views.pandas_view, name='pandas'),
    path('statistics/', views.statistics_view, name='statistics'),
    path('visualization/', views.visualization_view, name='visualization'),
    path('json-regex/', views.json_regex_view, name='json_regex'),
    path('fds-coverage/', views.fds_coverage_view, name='fds_coverage'),
]
