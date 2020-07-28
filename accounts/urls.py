from django.contrib.auth import views as auth_views
from django.urls import path

from . import views

app_name = 'accounts'
urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    path('complete_profile/', views.complete_profile, name='complete_profile'),
    path('logout/', views.logout_view, name='logout'),
]