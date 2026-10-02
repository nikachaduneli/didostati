from django.conf import settings
from django.http import FileResponse, Http404


def spa(request, path=''):
    """Serve the built Vue app (run `npm run build` in /frontend)."""
    index = settings.BASE_DIR.parent / 'frontend' / 'dist' / 'index.html'
    if not index.exists():
        raise Http404('Frontend not built. Run "npm run dev" in /frontend, or "npm run build".')
    return FileResponse(open(index, 'rb'), content_type='text/html')
