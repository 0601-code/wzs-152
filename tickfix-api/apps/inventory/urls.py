from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PartCategoryViewSet, PartViewSet, StockRecordViewSet

router = DefaultRouter()
router.register(r'categories', PartCategoryViewSet)
router.register(r'parts', PartViewSet)
router.register(r'stock-records', StockRecordViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
