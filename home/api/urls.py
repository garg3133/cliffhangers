from django.urls import path
from . import views

urlpatterns = [
    path('create_road/', views.create_road, name='api_create_road'),
    path('update_road_image/', views.update_road_image, name='api_update_road_image'),
    path('update_road_pci/', views.update_road_pci, name='api_update_road_pci'),
]