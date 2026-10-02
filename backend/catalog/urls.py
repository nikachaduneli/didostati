from django.urls import path

from . import views

urlpatterns = [
    path('categories/', views.CategoryList.as_view()),
    path('products/', views.ProductList.as_view()),
    path('products/<slug:slug>/', views.ProductDetail.as_view()),
]
