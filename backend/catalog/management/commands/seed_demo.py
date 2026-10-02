"""Fills the shop with demo categories/products/blogs with generated placeholder pictures."""
import io
import math
import random

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from catalog import models
from content.models import Blog, Page, Slide

CATEGORIES = {
    'TableCloth, სუფრა': [
        'TableCloth_1, სუფრა_1',
        'TableCloth_2, სუფრა_2',
        'TableCloth_3, სუფრა_3',
        'TableCloth_4, სუფრა_4',
        'TableCloth_5, სუფრა_5',
    ],
    'Plates, თეფშები': [
        'Plates_1, თეფშები_1',
        'Plates_2, თეფშები_2',
        'Plates_3, თეფშები_3',
        'Plates_4, თეფშები_4',
        'Plates_5, თეფშები_5',
    ],
    'Cups, ჭიქები': [
        'Cups_1, ჭიქები_1',
        'Cups_2, ჭიქები_2',
        'Cups_3, ჭიქები_3',
        'Cups_4, ჭიქები_4',
        'Cups_5, ჭიქები_5',
    ],
    'Collections, კოლექციები': [
        'Collections_1, კოლექციები_1',
        'Collections_2, კოლექციები_2',
        'Collections_3, კოლექციები_3',
        'Collections_4, კოლექციები_4',
        'Collections_5, კოლექციები_5',
    ]
}
COLORS = {'Black,შავი': '#1f1f1f', 'White,თეთრი': '#f5f5f5', 'Red,წითელი': '#d64045', 'Blue,ლურჯი': '#3a6ea5',
          'Green,მწვანე': '#4f8a5b', 'Purple,იასამნისფერი': '#863362'}


def placeholder(text, hex_color, size=(800, 800)):
    base = tuple(int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    img = Image.new('RGB', size, base)
    d = ImageDraw.Draw(img)
    for i in range(0, size[1], 4):  # soft vertical gradient
        shade = int(40 * i / size[1])
        d.line([(0, i), (size[0], i)], fill=tuple(max(0, c - shade) for c in base))
    try:
        font = ImageFont.load_default(size=size[0] // 14)
    except TypeError:
        font = ImageFont.load_default()
    light = sum(base) < 380
    d.text((size[0] // 2, size[1] // 2), text, fill='white' if light else '#222', font=font, anchor='mm')
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=85)
    return ContentFile(buf.getvalue())


SLIDES = [
    ('New autumn collection', 'ახალი შემოდგომის კოლექცია', 'Warm tones for your table', 'თბილი ტონები თქვენი სუფრისთვის', '/shop',
     ['#c8553d', '#f28f3b', '#6d597a']),
    ('Handpicked plates & cups', 'ხელით შერჩეული თეფშები და ჭიქები', 'Made to last and easy to love', 'გაგრძელებისთვის და საყვარელი', '/shop',
     ['#588b8b', '#3a6ea5', '#4f8a5b']),
    ('Read our blog', 'წაიკითხეთ ჩვენი ბლოგი', 'Ideas for styling your home', 'იდეები თქვენი სახლის გასაფორმებლად', '/blog',
     ['#863362', '#d64045', '#f28f3b']),
]


def blob_image(colors, rnd, size=(1920, 700)):
    """Soft abstract background: a few big blurred organic blobs on a tinted gradient."""
    w, h = size
    base = tuple(int(colors[0][i:i + 2], 16) for i in (1, 3, 5))
    img = Image.new('RGB', size, tuple(min(255, c + 90) for c in base))
    for color in colors * 2:
        rgb = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
        cx, cy, r = rnd.randint(0, w), rnd.randint(0, h), rnd.randint(h // 3, h)
        phases = [rnd.uniform(0, 6.28) for _ in range(3)]
        pts = []
        for a in range(0, 360, 6):
            t = math.radians(a)
            rad = r * (1 + .25 * math.sin(2 * t + phases[0]) + .15 * math.sin(3 * t + phases[1]) + .1 * math.sin(5 * t + phases[2]))
            pts.append((cx + rad * math.cos(t) * 1.4, cy + rad * math.sin(t)))
        layer = Image.new('L', size, 0)
        ImageDraw.Draw(layer).polygon(pts, fill=200)
        layer = layer.filter(ImageFilter.GaussianBlur(12))
        img.paste(Image.new('RGB', size, rgb), (0, 0), layer)
    buf = io.BytesIO()
    img.save(buf, 'JPEG', quality=85)
    return ContentFile(buf.getvalue())


class Command(BaseCommand):
    help = 'Create demo data (safe to run once on an empty database).'

    def seed_slides(self):
        if Slide.objects.exists():
            return
        rnd = random.Random(11)
        for n, (title, title_ka, sub, sub_ka, link, colors) in enumerate(SLIDES):
            slide = Slide(title=title, title_ka=title_ka, subtitle=sub, subtitle_ka=sub_ka, link=link, order=n)
            slide.image.save(f'slide-{n}.jpg', blob_image(colors, rnd), save=False)
            slide.save()
        self.stdout.write(self.style.SUCCESS('Demo slides created.'))

    def handle(self, *args, **opts):
        self.seed_slides()
        if models.Product.objects.exists():
            self.stdout.write('Products already exist - skipping demo data.')
            return
        rnd = random.Random(7)
        colors = []
        for name, hex in COLORS.items():
            name_en, name_ka = name.split(',')
            colors.append(models.Color.objects.get_or_create(name=name_en, name_ka=name_ka, hex=hex)[0])
        tones = ['#c8553d', '#588b8b', '#f28f3b', '#6d597a']
        for i, (cat_name, products) in enumerate(CATEGORIES.items()):
            cat_name_en, cat_name_ka = cat_name.split(', ')
            cat = models.Category(name=cat_name_en, name_ka=cat_name_ka, order=i,
                                  description=f'<p>Our <strong>{cat_name_en.lower()}</strong> collection.</p>',
                                  description_ka=f'{cat_name_ka} კოლექცია'
                                  )
            cat.image.save(f'category-{i}.jpg', placeholder(cat_name_en, tones[i]), save=False)
            cat.save()
            for j, name in enumerate(products):
                name_en, name_ka = name.split(', ')
                product = models.Product.objects.create(
                    category=cat, name=name_en,name_ka=name_ka, price=rnd.choice([12, 19, 24, 35, 49, 79, 120]) + 0.99,
                    discount_percent=rnd.choice([0, 0, 0, 10, 20, 30]), is_popular=j < 2,
                    description=f'<p>A lovely {name_en.lower()} from the Didostati {cat_name_en.lower()} range.</p>'
                                '<p>Made to last and easy to love.</p>')
                chosen = rnd.sample(colors, 3)
                product.colors.set(chosen)
                for k, c in enumerate(chosen):
                    img = models.ProductImage(product=product, color=c, order=k)
                    img.image.save(f'{product.slug}-{c.name.lower()}.jpg', placeholder(name_en, c.hex), save=False)
                    img.save()
        for slug, title, body in [
            ('about', 'About us', '<h2>Welcome to Didostati</h2><p>Edit this page from the admin panel '
                                  '(Pages &rarr; About us). You can add pictures and resize them freely.</p>'),
            ('contact', 'Contact', '<h2>Get in touch</h2><p>Email: hello@didostati.example<br>Phone: +000 000 000</p>'
                                   '<p>Edit this text in the admin panel (Pages &rarr; Contact).</p>')]:
            Page.objects.get_or_create(slug=slug, defaults={'title': title, 'content': body})
        for n, title in enumerate(['Welcome to Didostati', 'How to care for linen', 'Styling your home this autumn']):
            b = Blog(title=title, excerpt='A short teaser for this post.',
                            content=f'<p>This is the blog post "{title}". Edit it in the admin panel; '
                                    'you can insert images anywhere and resize them.</p>')
            b.cover_image.save(f'blog{n}.jpg', placeholder(title, tones[n], (1000, 600)), save=False)
            b.save()
        self.stdout.write(self.style.SUCCESS('Demo data created.'))
