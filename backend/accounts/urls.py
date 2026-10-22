from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('addresses', views.AddressViewSet, basename='address')

urlpatterns = [
    path('auth/register/', views.Register.as_view()),
    path('auth/login/', views.Login.as_view()),
    path('auth/me/', views.Me.as_view()),
    path('auth/admin-session/', views.AdminSession.as_view()),
] + router.urls
