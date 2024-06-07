from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('profile/', views.profile, name='profile'),
    path('about/', views.about, name='about'),
    path('profile/update_username/', views.update_username, name='update_username'),
    path('profile/update_profile_picture/', views.update_profile_picture, name='update_profile_picture'),
    path('profile/update_notifications/', views.update_notification_settings, name='update_notification_settings'),
]
