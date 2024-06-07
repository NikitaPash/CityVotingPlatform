from django.urls import path
from . import views

urlpatterns = [
    path('', views.admin_panel, name='admin_panel'),
    path('reported_projects/', views.show_reported_projects, name='reported_projects'),
    path('reported_comments/', views.show_reported_comments, name='reported_comments'),
    path('reported_projects/view_report/<int:project_id>', views.reported_project_management, name='reported_project_management'),
    path('reported_comments/view_report/<int:comment_id>', views.reported_comment_management, name='reported_comment_management'),
    path('analytic_dashboard/', views.dashboard, name='analytic_dashboard'),
    path('show_requests/', views.show_requests, name='show_requests'),
]
