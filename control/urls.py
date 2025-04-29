from django.urls import path, include 
from rest_framework import routers
from control import views

router = routers.DefaultRouter()
router.register(r'business', views.BusinessView, basename='business')
router.register(r'branch', views.BranchView, basename='branch')
router.register(r'products', views.ProductView, basename='products')
router.register(r'movements', views.MovementView, basename='movements')
router.register(r'stocks', views.StockView, basename='stocks')

urlpatterns = [
    path('control/model/', include(router.urls))
]
