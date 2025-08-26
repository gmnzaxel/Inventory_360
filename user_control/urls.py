from django.urls import path, include
from .views import RegisterAdminView, LoginView, LogoutView, CreateUserByAdminView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register-admin/', RegisterAdminView.as_view(), name='register-admin'),
    path('admin/create-user/', CreateUserByAdminView.as_view(), name='admin-create-user'),
]