from django.urls import path
from .views import CreateBookView, CreateLibraryUserView, BorrowRequestsView, UserBorrowHistoryView, BooksView, PersonalBorrowHistoryView, DownloadBorrowHistoryView



# =====================================================



from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework.permissions import AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

# Define the Authorization header for JWT token input
swagger_jwt_auth = openapi.Parameter(
    'Authorization',
    openapi.IN_HEADER,
    description="JWT Authorization header using Bearer token",
    type=openapi.TYPE_STRING,
)

# Swagger Configuration
schema_view = get_schema_view(
    openapi.Info(
        title="Library Management System API",
        default_version='v1',
        description="API documentation for the Library Management System",
        contact=openapi.Contact(email="example@example.com"),
        security=[{
            "Bearer": {
                "type": "apiKey",
                "name": "Authorization",
                "in": "header"
            }
        }],
    ),
    public=True,
    permission_classes=(AllowAny,),
)




# =====================================================
urlpatterns = [
    # API endpoints
    path('user/books/', BooksView.as_view(), name='books'),
    path('user/borrow-history/', PersonalBorrowHistoryView.as_view(), name='personal-borrow-history'),

    path('librarian/create-user/', CreateLibraryUserView.as_view(), name='create-user'),
    path('librarian/create-book/', CreateBookView.as_view(), name='create_book'),
    path('librarian/borrow-requests/', BorrowRequestsView.as_view(), name='borrow-requests'),
    path('librarian/borrow-requests/<int:pk>/', BorrowRequestsView.as_view(), name='update-borrow-request'),
    path('librarian/user-history/<int:user_id>/', UserBorrowHistoryView.as_view(), name='user-borrow-history'),
    
    path('user/download-history/', DownloadBorrowHistoryView.as_view(), name='download-borrow-history'),


# Swagger UI
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0), name='swagger-ui'),]
