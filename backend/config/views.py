from django.conf import settings
from django.http import Http404, HttpResponse

from . import seo


def spa(request, path=''):
    """Serve the built Vue app (run `npm run build` in /frontend), with this page's search engine tags."""
    index = settings.BASE_DIR.parent / 'frontend' / 'dist' / 'index.html'
    if not index.exists():
        raise Http404('Frontend not built. Run "npm run dev" in /frontend, or "npm run build".')
    html, status = seo.render_index(index.read_text(encoding='utf-8'), request, request.path)
    return HttpResponse(html, status=status)


def sitemap(request):
    return HttpResponse(seo.sitemap_xml(request), content_type='application/xml')


def robots(request):
    return HttpResponse(seo.robots_txt(request), content_type='text/plain')
