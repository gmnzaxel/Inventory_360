from django.urls import path, include 
from rest_framework import routers
from control import views


router = routers.DefaultRouter()
router.register(r'bussines', views.BussinesView, basename='bussines')

urlpatterns = [
    path('control/model/', include(router.urls))
]