from django.conf import settings
from rest_framework import generics, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from core.cache import CachedResponseMixin

from . import models, serializers as s


class PageDetail(CachedResponseMixin, generics.RetrieveAPIView):
    serializer_class = s.PageSerializer
    lookup_field = 'slug'
    queryset = models.Page.objects.all()


class BlogViewSet(CachedResponseMixin, viewsets.ReadOnlyModelViewSet):
    lookup_field = 'slug'
    queryset = models.Blog.objects.filter(is_published=True)

    def get_serializer_class(self):
        return s.BlogDetailSerializer if self.action == 'retrieve' else s.BlogListSerializer

    def paginate_queryset(self, queryset):
        if self.request.query_params.get('limit'):
            return None
        return super().paginate_queryset(queryset)

    def filter_queryset(self, queryset):
        limit = self.request.query_params.get('limit')
        return queryset[:int(limit)] if limit and limit.isdigit() else queryset


class ContactCreate(generics.CreateAPIView):
    serializer_class = s.ContactMessageSerializer


class SlideList(CachedResponseMixin, generics.ListAPIView):
    serializer_class = s.SlideSerializer
    queryset = models.Slide.objects.filter(is_active=True)
    pagination_class = None


class PartnerList(CachedResponseMixin, generics.ListAPIView):
    serializer_class = s.PartnerSerializer
    queryset = models.Partner.objects.filter(is_active=True)
    pagination_class = None


class SocialLinks(APIView):
    def get(self, request):
        return Response({'facebook': settings.FB_DIDOSTATI, 'instagram': settings.IG_DIDOSTATI})
