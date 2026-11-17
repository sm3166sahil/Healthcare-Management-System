from django.urls import path
from . import views

app_name = 'medical_records'

urlpatterns = [
    path('', views.record_list, name='list'),
    path('', views.record_list, name='record_list'),
    path('add/', views.record_add, name='create'),
    path('add/', views.record_add, name='record_add'),
    path('<int:pk>/', views.record_detail, name='detail'),
    path('<int:pk>/', views.record_detail, name='record_detail'),
    path('<int:pk>/edit/', views.record_edit, name='update'),
    path('<int:pk>/edit/', views.record_edit, name='record_edit'),
    path('<int:pk>/delete/', views.record_delete, name='delete'),
    path('<int:pk>/delete/', views.record_delete, name='record_delete'),
]
