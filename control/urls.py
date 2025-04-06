from django.urls import path, include 
from rest_framework import routers
from control import views


router = routers.DefaultRouter()
router.register(r'bussines', views.BussinesView, basename='bussines')
router.register(r'users', views.UserView, basename='users')
router.register(r'products', views.ProductView, basename='products')
router.register(r'categories', views.CategoryView, basename='categories')
router.register(r'supplier', views.SupplierView, basename='supplier')
router.register(r'movements', views.MovementView, basename='movements')


urlpatterns = [
    path('control/model/', include(router.urls))
]