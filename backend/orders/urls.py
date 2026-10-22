from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('cart/price/', views.CartPrice.as_view()),
    path('payments/methods/', views.PaymentMethods.as_view()),
    path('payments/<slug:provider>/callback/', views.PaymentCallback.as_view()),
    path('orders/status/<str:token>/', views.OrderPaymentStatus.as_view()),
] + router.urls
