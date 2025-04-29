from django.urls import path, include 
from rest_framework import routers
from control import views
from rest_framework.routers import DefaultRouter
from .views import MovementView


router = routers.DefaultRouter()
router.register(r'bussines', views.BusinessView, basename='bussines')
router.register(r'products', views.ProductView, basename='products')
router.register(r'categories', views.CategoryView, basename='categories')
router.register(r'supplier', views.SupplierView, basename='supplier')
router.register(r'movements', views.MovementView, basename='movements')


urlpatterns = [
    path('control/model/', include(router.urls))
]