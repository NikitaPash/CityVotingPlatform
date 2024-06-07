from django.urls import path
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions

from swagger.views import get_project_info, get_user_info, get_all_projects, get_all_districts

schema_view = get_schema_view(
    openapi.Info(
        title="City Voting Platform API",
        default_version='v4.20',
        description="Swagger for my people",
        terms_of_service="https://www.google.com/policies/terms/",
        contact=openapi.Contact(email="pashchuknik@gmail.com"),
        license=openapi.License(name="BSD License"),
    ),
    public=True,
    permission_classes=([permissions.IsAuthenticated]),
)

urlpatterns = [
    path('', schema_view.with_ui('swagger', cache_timeout=0), name='schema-swagger-ui'),
    path('all_projects/', get_all_projects, name='get_all_projects'),
    path('all_districts/', get_all_districts, name='get_all_districts'),
    path('<int:project_id>/', get_project_info, name='get_project_info'),
    path('<str:username>/', get_user_info, name='get_user_info'),
]
