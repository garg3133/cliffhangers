from django.urls import path
from . import views

app_name = 'home'
urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('road_details/<str:slug>', views.road_details, name='road_details'),

    # AJAX
    path('ajax_state_changed/', views.ajax_state_changed, name='ajax_state_changed'),
    path('ajax_district_changed/', views.ajax_district_changed, name='ajax_district_changed'),
]