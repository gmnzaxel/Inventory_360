from django.urls import path, include
from .views import RegisterAdminView, LoginView, LogoutView, CreateUserByAdminView, UserView
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'users', UserView, basename='user')

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register-admin/', RegisterAdminView.as_view(), name='register-admin'),
    path('admin/create-user/', CreateUserByAdminView.as_view(), name='admin-create-user'),
    path('', include(router.urls)),
]