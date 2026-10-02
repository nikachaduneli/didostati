from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('orders', views.OrderViewSet, basename='order')

urlpatterns = [
    path('cart/price/', views.CartPrice.as_view()),
] + router.urls
