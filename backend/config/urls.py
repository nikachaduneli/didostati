from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path, re_path

from . import views

urlpatterns = [
    path('i18n/', include('django.conf.urls.i18n')),
    path('admin/', admin.site.urls),
    path('api/', include('catalog.urls')),
    path('api/', include('content.urls')),
    path('api/', include('accounts.urls')),
    path('api/', include('orders.urls')),
    path('ckeditor5/', include('django_ckeditor_5.urls')),
    path('sitemap.xml', views.sitemap),
    path('robots.txt', views.robots),
    path('favicon.ico', views.favicon),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) + [
    # Everything else is the Vue single-page app (only once built).
    re_path(r'^(?!api/|i18n/|admin/|media/|static/|ckeditor5/)(?P<path>.*)$', views.spa),
]
