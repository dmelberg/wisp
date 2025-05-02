from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MovementViewSet, MemberViewSet, CategoryViewSet, DistributionTypeViewSet,
    SalaryViewSet, PeriodViewSet, UserCreate, HouseholdViewSet, JoinHouseholdView
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

router = DefaultRouter()
router.register(r'movements', MovementViewSet, basename='movement')
router.register(r'members', MemberViewSet, basename='member')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'distribution-types', DistributionTypeViewSet)
router.register(r'salaries', SalaryViewSet, basename='salary')
router.register(r'periods', PeriodViewSet)
router.register(r'households', HouseholdViewSet, basename='household')

urlpatterns = [
    path('register/', UserCreate.as_view(), name='user_register'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('households/join/', JoinHouseholdView.as_view(), name='join_household'),
    path('', include(router.urls)),
]




