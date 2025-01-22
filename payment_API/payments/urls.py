from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import PaymentViewSet, PaymentHistoryViewSet, PaymentRefundViewSet, PaymentChargeViewSet

router = DefaultRouter()
router.register(r'payments', PaymentViewSet, basename='payment')
router.register(r'payment-history', PaymentHistoryViewSet, basename='payment-history')
router.register(r'payment-refunds', PaymentRefundViewSet, basename='payment-refund')
router.register(r'payment-charges', PaymentChargeViewSet, basename='payment-charge')

urlpatterns = [
   
    path('api/v1/', include([
        path('', include(router.urls)),
        path('webhook/paystack/', 
            PaymentViewSet.as_view({'post': 'paystack_webhook'}),
            name='paystack-webhook'),
    ])),
]