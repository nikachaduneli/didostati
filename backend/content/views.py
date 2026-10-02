from rest_framework import generics, viewsets

from . import models, serializers as s


class PageDetail(generics.RetrieveAPIView):
    serializer_class = s.PageSerializer
    lookup_field = 'slug'
    queryset = models.Page.objects.all()


class BlogViewSet(viewsets.ReadOnlyModelViewSet):
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
