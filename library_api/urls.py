from django.urls import path
from rest_framework.routers import DefaultRouter
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from .views import UserView


schema_view = get_schema_view(
   openapi.Info(
      title="Library Management System API",
      default_version='v1',
      description="API documentation for the Library Management System",
      terms_of_service="https://www.google.com/policies/terms/",
      contact=openapi.Contact(email="prathish@fotoowl.ai"),
      license=openapi.License(name="BSD License"),
   ),
   public=True,
)

urlpatterns = [
    path('user/', UserView.as_view(), name='user-view'),  # Add your user view here
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),  # Add Swagger UI
]
