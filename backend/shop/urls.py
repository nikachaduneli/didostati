from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('blogs', views.BlogViewSet, basename='blog')
router.register('orders', views.OrderViewSet, basename='order')
router.register('addresses', views.AddressViewSet, basename='address')

urlpatterns = [
    path('categories/', views.CategoryList.as_view()),
    path('products/', views.ProductList.as_view()),
    path('products/<slug:slug>/', views.ProductDetail.as_view()),
    path('pages/<slug:slug>/', views.PageDetail.as_view()),
    path('contact/', views.ContactCreate.as_view()),
    path('cart/price/', views.CartPrice.as_view()),
    path('auth/register/', views.Register.as_view()),
    path('auth/login/', views.Login.as_view()),
    path('auth/me/', views.Me.as_view()),
    path('', include(router.urls)),
]
