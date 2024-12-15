from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import MovementViewSet, MemberViewSet, CategoryViewSet, DistributionTypeViewSet, SalaryViewSet, PeriodViewSet

router = DefaultRouter()
router.register(r'movements', MovementViewSet)
router.register(r'members', MemberViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'distribution-types', DistributionTypeViewSet)
router.register(r'salary', SalaryViewSet)
router.register(r'periods', PeriodViewSet)

urlpatterns = [
    path('', include(router.urls)),
]




