from django.conf import settings
from django.utils import translation


class ApiLanguageMiddleware:
    """The SPA sends `X-Lang: ka|en`; activate it so API responses come back in that language.

    Must come after LocaleMiddleware (which would otherwise pick the language from the admin cookie).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        code = request.headers.get('X-Lang')
        if code in dict(settings.LANGUAGES):
            translation.activate(code)
            request.LANGUAGE_CODE = code
        return self.get_response(request)


class ApiNoIndexMiddleware:
    """robots.txt lets crawlers fetch /api/ (the SPA needs it to render); this keeps the JSON itself out of results."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/api/'):
            response['X-Robots-Tag'] = 'noindex'
        return response
