from django.urls import path, include
from rest_framework import routers
from .views import UserView

router = routers.DefaultRouter()
router.register(r'users', UserView, basename='users')

urlpatterns = [
    path('user/', include(router.urls)),
]
