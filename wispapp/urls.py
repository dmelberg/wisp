from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import MovementViewSet, MemberViewSet, CategoryViewSet, DistributionTypeViewSet, SalaryViewSet, PeriodViewSet, RegisterView
from django.conf import settings
from django.conf.urls.static import static

router = DefaultRouter()
router.register(r'movements', MovementViewSet)
router.register(r'members', MemberViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'distribution-types', DistributionTypeViewSet)
router.register(r'salary', SalaryViewSet)
router.register(r'periods', PeriodViewSet)

urlpatterns = [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),  
    path('', include(router.urls)),
]

from django.urls import get_resolver

for url in get_resolver().reverse_dict.keys():
    print(url)


