from django.urls import path
from . import views

app_name = 'patients'

urlpatterns = [
    path('', views.patient_list, name='list'),
    path('', views.patient_list, name='patient_list'),
    path('add/', views.patient_add, name='create'),
    path('add/', views.patient_add, name='patient_add'),
    path('search/', views.patient_search, name='patient_search'),
    path('<int:pk>/', views.patient_detail, name='detail'),
    path('<int:pk>/', views.patient_detail, name='patient_detail'),
    path('<int:pk>/edit/', views.patient_edit, name='update'),
    path('<int:pk>/edit/', views.patient_edit, name='patient_edit'),
    path('<int:pk>/delete/', views.patient_delete, name='delete'),
    path('<int:pk>/delete/', views.patient_delete, name='patient_delete'),
]
