from django.urls import path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('blogs', views.BlogViewSet, basename='blog')

urlpatterns = [
    path('pages/<slug:slug>/', views.PageDetail.as_view()),
    path('contact/', views.ContactCreate.as_view()),
] + router.urls
