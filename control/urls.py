from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BusinessView, BranchView, ProductView, MovementView, 
    StockView, DocumentView, CategoryView, DashboardDataView, 
    SupplierView
)

router = DefaultRouter()
router.register(r'businesses', BusinessView, basename='business')
router.register(r'branches', BranchView, basename='branch')
router.register(r'products', ProductView, basename='product')
router.register(r'movements', MovementView, basename='movement')
router.register(r'stocks', StockView, basename='stock')
router.register(r'documents', DocumentView, basename='document')
router.register(r'categories', CategoryView, basename='category')
router.register(r'suppliers', SupplierView, basename='supplier')


urlpatterns = [
    path('', include(router.urls)),
    path('dashboard-data/', DashboardDataView.as_view(), name='dashboard-data'),
    path('', include(router.urls)),
]