from django.urls import path
from . import views

urlpatterns = [
    path('update_road_image/', views.update_road_image, name='api_update_road_image'),
    path('update_road_pci/', views.update_road_pci, name='api_update_road_pci'),
]