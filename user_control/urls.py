from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RegisterAdminView, 
    LogoutView, 
    CreateUserByAdminView, 
    CurrentUserView, 
    UserView,
    DeleteUserView # <-- 1. Importa la nueva vista
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView
)

router = DefaultRouter()
router.register(r'users', UserView, basename='user')

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register-admin/', RegisterAdminView.as_view(), name='register-admin'),
    path('admin/create-user/', CreateUserByAdminView.as_view(), name='admin-create-user'),
    path('user/', CurrentUserView.as_view(), name='current-user'), 
    path('user/delete/', DeleteUserView.as_view(), name='delete-user'),

    path('', include(router.urls)),
]