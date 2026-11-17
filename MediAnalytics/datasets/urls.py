from django.urls import path
from . import views

app_name = 'datasets'

urlpatterns = [
    path('', views.dataset_list, name='list'),
    path('', views.dataset_list, name='dataset_list'),
    path('upload/', views.dataset_upload, name='upload'),
    path('upload/', views.dataset_upload, name='dataset_upload'),
    path('<int:pk>/explore/', views.dataset_explore, name='explore'),
    path('<int:pk>/explore/', views.dataset_explore, name='dataset_explore'),
    path('<int:pk>/download/', views.dataset_download, name='download'),
    path('<int:pk>/download/', views.dataset_download, name='dataset_download'),
    path('<int:pk>/delete/', views.dataset_delete, name='delete'),
    path('<int:pk>/delete/', views.dataset_delete, name='dataset_delete'),
]
