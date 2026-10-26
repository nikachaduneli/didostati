"""Search engine support for the Vue app: per-page <head> tags, real 404s, sitemap.xml and robots.txt.

English pages have no prefix, Georgian ones live under /ka (see frontend/src/i18n.js). The SPA is a
blank page until its JavaScript runs, so the tags crawlers and link previews rely on are added here.
"""
import json
import re
import xml.etree.ElementTree as ET
from html import unescape

from django.templatetags.static import static
from django.utils import translation
from django.utils.html import escape, strip_tags
from django.utils.text import Truncator

from catalog.models import Category, Product
from content.models import Blog, Page
from core import config

LANGS = ('en', 'ka')
PREFIX = re.compile(r'^/ka(?=/|$)')
# Pages worth listing in search results, and their titles (None: the site name alone).
STATIC_PAGES = {'/': None, '/shop': {'en': 'Shop', 'ka': 'მაღაზია'}, '/blog': {'en': 'Blog', 'ka': 'ბლოგი'}}
# Pages that exist but must stay out of search results.
PRIVATE_PAGES = {'/cart', '/checkout', '/payment/return', '/order/done', '/login', '/register', '/account'}
SITE_NAME = {'en': 'Didostati', 'ka': 'დიდოსტატი'}


def site_url(request):
    return (config.get('SITE_URL') or request.build_absolute_uri('/')).rstrip('/')


def split_lang(path):
    """'/ka/shop' -> ('ka', '/shop'); '/shop/' -> ('en', '/shop')."""
    path = '/' + path.strip('/')
    if PREFIX.match(path):
        return 'ka', PREFIX.sub('', path) or '/'
    return 'en', path


def lang_path(path, lang):
    if lang != 'ka':
        return path
    return '/ka' if path == '/' else '/ka' + path


def plain(html, length=160):
    text = re.sub(r'\s+', ' ', unescape(strip_tags(html or ''))).strip()
    return Truncator(text).chars(length)


class Meta:
    def __init__(self, title=None, description='', image='', kind='website', data=(), index=True, found=True):
        self.title, self.description, self.image, self.kind = title, description, image, kind
        self.data, self.index, self.found = list(data), index, found


def page_meta(path, lang, base):
    """What the <head> of `path` (without language prefix) should say. Runs with `lang` active."""
    absolute = lambda url: url if url.startswith('http') else base + url
    home = base + lang_path('/', lang)
    crumbs = lambda *items: {
        '@context': 'https://schema.org', '@type': 'BreadcrumbList',
        'itemListElement': [{'@type': 'ListItem', 'position': n, 'name': name, 'item': url}
                            for n, (name, url) in enumerate([(SITE_NAME[lang], home), *items], 1)],
    }

    if path in STATIC_PAGES:
        meta = Meta(STATIC_PAGES[path] and STATIC_PAGES[path][lang])
        if path == '/':
            meta.data.append({
                '@context': 'https://schema.org', '@type': 'Organization', 'name': SITE_NAME[lang], 'url': home,
                'logo': absolute(static('icon-512.png')),
                'sameAs': [u for u in (config.get('FB_DIDOSTATI'), config.get('IG_DIDOSTATI')) if u],
            })
        return meta
    if path in PRIVATE_PAGES:
        return Meta(index=False)

    kind, _, slug = path.strip('/').partition('/')
    if kind in Page.SHORT_SLUGS and not slug:
        page = Page.objects.filter(slug=kind).first()
        return Meta(page.tr('title'), plain(page.tr('content'))) if page else Meta(kind.title())
    if not slug or '/' in slug:
        return Meta(index=False, found=False)

    if kind == 'product':
        p = (Product.objects.filter(slug=slug, is_active=True).select_related('category').prefetch_related('images', 'sizes').first())
        if not p:
            return Meta(index=False, found=False)
        url = base + lang_path(path, lang)
        images = [absolute(i.image.url) for i in p.images.all()]
        prices = sorted({s.final_price for s in p.sizes.all()} or {p.final_price})
        offer = {'priceCurrency': 'GEL', 'availability': 'https://schema.org/InStock', 'url': url}
        if len(prices) > 1:
            offer.update({'@type': 'AggregateOffer', 'lowPrice': str(prices[0]), 'highPrice': str(prices[-1]),
                          'offerCount': len(prices)})
        else:
            offer.update({'@type': 'Offer', 'price': str(prices[0])})
        description = plain(p.tr('description')) or p.tr('name')
        category = p.category
        return Meta(
            f'{p.tr("name")} – {prices[0]} ₾', description, images[0] if images else '', 'product', [
                {'@context': 'https://schema.org', '@type': 'Product', 'name': p.tr('name'), 'url': url,
                 'description': description, 'image': images, 'brand': {'@type': 'Brand', 'name': 'Didostati'},
                 'category': category.tr('name'), 'offers': offer},
                crumbs((category.tr('name'), base + lang_path(f'/category/{category.slug}', lang)), (p.tr('name'), url)),
            ])

    if kind == 'page':
        page = Page.objects.filter(slug=slug).exclude(slug__in=Page.SHORT_SLUGS).first()
        if not page:
            return Meta(index=False, found=False)
        return Meta(page.tr('title'), plain(page.tr('content')))

    if kind == 'category':
        c = Category.objects.filter(slug=slug).first()
        if not c:
            return Meta(index=False, found=False)
        url = base + lang_path(path, lang)
        return Meta(c.tr('name'), plain(c.tr('description')), absolute(c.image.url) if c.image else '',
                    data=[crumbs((c.tr('name'), url))])

    if kind == 'blog':
        b = Blog.objects.filter(slug=slug, is_published=True).first()
        if not b:
            return Meta(index=False, found=False)
        url = base + lang_path(path, lang)
        image = absolute(b.cover_image.url) if b.cover_image else ''
        description = b.tr('excerpt') or plain(b.tr('content'))
        return Meta(b.tr('title'), description, image, 'article', [
            {'@context': 'https://schema.org', '@type': 'BlogPosting', 'headline': b.tr('title'), 'url': url,
             'description': description, 'image': [image] if image else [],
             'datePublished': b.created_at.isoformat(), 'author': {'@type': 'Organization', 'name': 'Didostati'}},
            crumbs((STATIC_PAGES['/blog'][lang], base + lang_path('/blog', lang)), (b.tr('title'), url)),
        ])

    return Meta(index=False, found=False)


def head_tags(meta, path, lang, base):
    name = SITE_NAME[lang]
    title = f'{meta.title} · {name}' if meta.title else name
    description = meta.description or config.get('SITE_DESCRIPTION_KA' if lang == 'ka' else 'SITE_DESCRIPTION')
    tags = [f'<title>{escape(title)}</title>']
    if description:
        tags.append(f'<meta name="description" content="{escape(description)}" />')
    if not meta.index:
        tags.append('<meta name="robots" content="noindex" />')
        return tags
    url = base + lang_path(path, lang)
    tags.append(f'<link rel="canonical" href="{escape(url)}" />')
    for code in LANGS:
        tags.append(f'<link rel="alternate" hreflang="{code}" href="{escape(base + lang_path(path, code))}" />')
    tags.append(f'<link rel="alternate" hreflang="x-default" href="{escape(base + path)}" />')
    og = {'og:type': meta.kind, 'og:site_name': name, 'og:title': title,
          'og:description': description, 'og:url': url, 'og:image': meta.image,
          'og:locale': 'ka_GE' if lang == 'ka' else 'en_US'}
    tags += [f'<meta property="{k}" content="{escape(v)}" />' for k, v in og.items() if v]
    tags.append(f'<meta name="twitter:card" content="{"summary_large_image" if meta.image else "summary"}" />')
    for item in meta.data:
        # Escaped so a `</script>` inside a value cannot end the tag early.
        data = json.dumps(item, ensure_ascii=False).replace('<', '\\u003c')
        tags.append(f'<script type="application/ld+json">{data}</script>')
    return tags


def render_index(html, request, url_path):
    """Returns (index.html with this page's tags, HTTP status)."""
    lang, path = split_lang(url_path)
    base = site_url(request)
    with translation.override(lang):
        meta = page_meta(path, lang, base)
        tags = head_tags(meta, path, lang, base)
    html = html.replace('<html lang="en">', f'<html lang="{lang}">', 1)
    html = re.sub(r'<title>.*?</title>', lambda m: '\n    '.join(tags), html, count=1, flags=re.S)
    return html, 200 if meta.found else 404


def sitemap_entries():
    """Every indexable page (without language prefix): (path, last change or None, changefreq, priority, image urls)."""
    yield '/', None, 'daily', '1.0', [static('icon-512.png')]
    yield '/shop', None, 'daily', '0.9', []
    yield '/blog', None, 'weekly', '0.7', []
    for c in Category.objects.only('slug', 'image'):
        yield f'/category/{c.slug}', None, 'weekly', '0.8', [c.image.url] if c.image else []
    for p in Product.objects.filter(is_active=True).only('slug', 'created_at').prefetch_related('images'):
        yield f'/product/{p.slug}', p.created_at, 'weekly', '0.8', [i.image.url for i in p.images.all()]
    for b in Blog.objects.filter(is_published=True).only('slug', 'created_at', 'cover_image'):
        yield f'/blog/{b.slug}', b.created_at, 'monthly', '0.6', [b.cover_image.url] if b.cover_image else []
    for page in Page.objects.only('slug', 'updated_at'):
        yield page.path, page.updated_at, 'monthly', '0.5', []


SITEMAP_NS = {'': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
for prefix, uri in SITEMAP_NS.items():
    ET.register_namespace(prefix, uri)


def sitemap_xml(request):
    base = site_url(request)
    tag = lambda prefix, name: f'{{{SITEMAP_NS[prefix]}}}{name}'
    urlset = ET.Element(tag('', 'urlset'))
    for path, lastmod, changefreq, priority, images in sitemap_entries():
        for code in LANGS:
            url = ET.SubElement(urlset, tag('', 'url'))
            ET.SubElement(url, tag('', 'loc')).text = base + lang_path(path, code)
            if lastmod:
                ET.SubElement(url, tag('', 'lastmod')).text = f'{lastmod:%Y-%m-%d}'
            ET.SubElement(url, tag('', 'changefreq')).text = changefreq
            ET.SubElement(url, tag('', 'priority')).text = priority
    ET.indent(urlset)
    return ET.tostring(urlset, encoding='utf-8', xml_declaration=True)


def robots_txt(request):
    private = ['/cart', '/checkout', '/account', '/login', '/register', '/payment/', '/order/']
    # /api/ stays crawlable: Google renders the Vue app, which loads every page's content from it.
    # The API answers carry `X-Robots-Tag: noindex` (config.middleware) so they never show up themselves.
    lines = ['User-agent: *', 'Disallow: /admin/',
             *(f'Disallow: {prefix}{p}' for prefix in ('', '/ka') for p in private),
             '', f'Sitemap: {site_url(request)}/sitemap.xml', '']
    return '\n'.join(lines)
