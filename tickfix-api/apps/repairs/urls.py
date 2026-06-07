from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ServiceItemViewSet, RepairOrderViewSet, StatusHistoryViewSet

router = DefaultRouter()
router.register(r'service-items', ServiceItemViewSet)
router.register(r'orders', RepairOrderViewSet)
router.register(r'status-history', StatusHistoryViewSet)

urlpatterns = [
    path('', include(router.urls)),
]
