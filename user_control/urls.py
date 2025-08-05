from django.urls import path, include
from .views import RegisterAdminView, LogoutView, CreateUserByAdminView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),


    # path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register-admin/', RegisterAdminView.as_view(), name='register-admin'),
    path('admin/create-user/', CreateUserByAdminView.as_view(), name='admin-create-user'),
]
