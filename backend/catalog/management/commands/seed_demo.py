"""Fills the database with demo data covering every feature, in English and Georgian.

Pictures are generated placeholders. Each section is skipped when its table already has rows, so the
command is safe to re-run; use --reset to wipe the demo content first (users and orders are kept
unless they are the demo ones).
"""
import io
import math
import random
from decimal import Decimal

from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.db import transaction
from PIL import Image, ImageDraw, ImageFilter, ImageFont

from accounts.models import Address, User
from catalog import models
from content.models import Blog, ContactMessage, Page, Partner, Slide
from orders.models import Order, OrderItem

DEMO_EMAIL = 'demo@didostati.example'
DEMO_PASSWORD = 'demo12345'

# (name, name_ka, hex)
COLORS = [
    ('Black', 'შავი', '#1f1f1f'), ('White', 'თეთრი', '#f5f5f5'), ('Red', 'წითელი', '#d64045'),
    ('Blue', 'ლურჯი', '#3a6ea5'), ('Green', 'მწვანე', '#4f8a5b'), ('Purple', 'იასამნისფერი', '#863362'),
]

# category: (name, name_ka, description, description_ka, [(name, name_ka, base price, sizes)])
# sizes: [(name, name_ka, price or None)]; None price inherits the product price.
CATEGORIES = [
    ('Tablecloths', 'სუფრები',
     'Linen and cotton <strong>tablecloths</strong> for every occasion.',
     'სელისა და ბამბის <strong>სუფრები</strong> ყველა შემთხვევისთვის.',
     [('Linen tablecloth', 'სელის სუფრა', 49.99, [('140x180 cm', '140x180 სმ', None), ('140x240 cm', '140x240 სმ', 64.99), ('160x300 cm', '160x300 სმ', 84.99)]),
      ('Cotton tablecloth', 'ბამბის სუფრა', 35.99, [('140x180 cm', '140x180 სმ', None), ('140x240 cm', '140x240 სმ', 45.99)]),
      ('Embroidered runner', 'ნაქარგი ბილიკი', 19.99, []),
      ('Festive tablecloth', 'სადღესასწაულო სუფრა', 79.99, [('Round 150 cm', 'მრგვალი 150 სმ', None), ('Long 140x300 cm', 'გრძელი 140x300 სმ', 109.99)]),
      ('Napkin set', 'ხელსახოცების ნაკრები', 12.99, [])]),
    ('Plates', 'თეფშები',
     'Hand-glazed <strong>plates</strong> that are made to last.',
     'ხელით მოჭიქული <strong>თეფშები</strong>, რომლებიც დიდხანს გაგრძელდება.',
     [('Dinner plate', 'სადილის თეფში', 24.99, [('Small 20 cm', 'პატარა 20 სმ', 17.99), ('Medium 24 cm', 'საშუალო 24 სმ', None), ('Large 28 cm', 'დიდი 28 სმ', 31.99)]),
      ('Soup bowl', 'წვნიანის თეფში', 19.99, []),
      ('Serving platter', 'სასერვისო ლანგარი', 49.99, [('35 cm', '35 სმ', None), ('45 cm', '45 სმ', 69.99)]),
      ('Dessert plate', 'სადესერტო თეფში', 14.99, []),
      ('Ceramic salad bowl', 'კერამიკული სალათის თასი', 35.99, [])]),
    ('Cups', 'ჭიქები',
     'Cups, mugs and glasses for your morning coffee or evening wine.',
     'ჭიქები და ფინჯნები დილის ყავისთვის ან საღამოს ღვინისთვის.',
     [('Coffee cup', 'ყავის ფინჯანი', 12.99, [('Espresso 90 ml', 'ესპრესო 90 მლ', 9.99), ('Regular 250 ml', 'ჩვეულებრივი 250 მლ', None)]),
      ('Tea mug', 'ჩაის ჭიქა', 14.99, []),
      ('Wine glass', 'ღვინის ჭიქა', 19.99, [('Small', 'პატარა', None), ('Large', 'დიდი', 24.99)]),
      ('Water glass', 'წყლის ჭიქა', 8.99, []),
      ('Travel mug', 'სამგზავრო ჭიქა', 24.99, [])]),
]

# Collections are ordinary products listing other products: (name, name_ka, description, description_ka,
# price, discount, [(category index, product index, quantity)])
COLLECTIONS = [
    ('Dinner for four', 'ვახშამი ოთხისთვის',
     'Everything for a table of four: tablecloth, napkins, plates and glasses.',
     'ყველაფერი ოთხკაციანი სუფრისთვის: სუფრა, ხელსახოცები, თეფშები და ჭიქები.',
     129.99, 15, [(0, 1, 1), (0, 4, 1), (1, 0, 4), (2, 3, 4)]),
    ('Morning coffee set', 'დილის ყავის ნაკრები',
     'A cosy start to the day: cups, a dessert plate and a runner.',
     'დღის მყუდრო დასაწყისი: ფინჯნები, სადესერტო თეფში და ბილიკი.',
     44.99, 0, [(2, 0, 2), (1, 3, 2), (0, 2, 1)]),
    ('Festive table', 'სადღესასწაულო სუფრა',
     'Impress your guests with this complete festive table set.',
     'დაატყვეთ შთაბეჭდილება სტუმრებს სადღესასწაულო სუფრის სრული ნაკრებით.',
     219.99, 20, [(0, 3, 1), (1, 2, 1), (1, 0, 6), (2, 2, 6)]),
]

SLIDES = [
    ('New autumn collection', 'ახალი შემოდგომის კოლექცია', 'Warm tones for your table', 'თბილი ტონები თქვენი სუფრისთვის', '/shop',
     ['#c8553d', '#f28f3b', '#6d597a']),
    ('Handpicked plates & cups', 'ხელით შერჩეული თეფშები და ჭიქები', 'Made to last and easy to love', 'გაგრძელებისთვის და საყვარელი', '/shop',
     ['#588b8b', '#3a6ea5', '#4f8a5b']),
    ('Read our blog', 'წაიკითხეთ ჩვენი ბლოგი', 'Ideas for styling your home', 'იდეები თქვენი სახლის გასაფორმებლად', '/blog',
     ['#863362', '#d64045', '#f28f3b']),
]

PAGES = [
    ('about', 'About us', 'ჩვენ შესახებ',
     '<h2>Welcome to Didostati</h2><p>We bring warmth to your table with carefully chosen linens, ceramics and glassware. '
     'Edit this page from the admin panel (Pages &rarr; About us); you can add pictures and resize them freely.</p>',
     '<h2>კეთილი იყოს თქვენი მობრძანება Didostati-ში</h2><p>ჩვენ თქვენს სუფრას სითბოს ვმატებთ საგულდაგულოდ შერჩეული სელის ნაწარმით, '
     'კერამიკითა და მინის ჭურჭლით. ამ გვერდის რედაქტირება შეგიძლიათ ადმინისტრატორის პანელიდან (გვერდები &rarr; ჩვენ შესახებ).</p>'),
    ('contact', 'Contact', 'კონტაქტი',
     '<h2>Get in touch</h2><p>Email: hello@didostati.example<br>Phone: +995 000 000 000</p>'
     '<p>Edit this text in the admin panel (Pages &rarr; Contact).</p>',
     '<h2>დაგვიკავშირდით</h2><p>ელფოსტა: hello@didostati.example<br>ტელეფონი: +995 000 000 000</p>'
     '<p>ეს ტექსტი შეგიძლიათ შეცვალოთ ადმინისტრატორის პანელიდან (გვერდები &rarr; კონტაქტი).</p>'),
]

# (name, name_ka, link, hex)
PARTNERS = [
    ('Linen & Co', 'სელი და კომპანია', 'https://example.com/linen', '#c8553d'),
    ('Ceramica Studio', 'კერამიკის სტუდია', 'https://example.com/ceramica', '#588b8b'),
    ('Glass Works', 'მინის სახელოსნო', 'https://example.com/glass', '#3a6ea5'),
    ('Tbilisi Crafts', 'თბილისის ხელოსნები', '', '#6d597a'),
]

BLOGS = [
    ('Welcome to Didostati', 'კეთილი იყოს თქვენი მობრძანება Didostati-ში',
     'Who we are and what you will find here.', 'ვინ ვართ და რას იპოვით აქ.',
     '<p>Welcome! Didostati is a small shop for people who love a well-set table.</p><p>Browse our collections and enjoy.</p>',
     '<p>მოგესალმებით! Didostati პატარა მაღაზიაა მათთვის, ვისაც კარგად გაწყობილი სუფრა უყვარს.</p><p>დაათვალიერეთ ჩვენი კოლექციები და ისიამოვნეთ.</p>'),
    ('How to care for linen', 'როგორ მოვუაროთ სელის ნაწარმს',
     'Simple habits that keep linen soft for years.', 'მარტივი ჩვევები, რომლებიც სელს წლების განმავლობაში რბილს ინარჩუნებს.',
     '<p>Wash linen at 40&deg;C, avoid bleach and iron it while still slightly damp.</p>',
     '<p>სელი დარეცხეთ 40&deg;C-ზე, მოერიდეთ გამათეთრებელს და გააუთოვეთ მცირედ ნესტიანი.</p>'),
    ('Styling your home this autumn', 'როგორ გავაფორმოთ სახლი ამ შემოდგომას',
     'Warm colours and natural textures for the season.', 'თბილი ფერები და ბუნებრივი ტექსტურები ამ სეზონისთვის.',
     '<p>Think terracotta, olive and mustard, paired with raw ceramics and natural linen.</p>',
     '<p>იფიქრეთ ტერაკოტაზე, ზეთისხილისფერსა და მდოგვისფერზე, შეუხამეთ უმი კერამიკა და ბუნებრივი სელი.</p>'),
]

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
    help = 'Create demo data for every feature (safe to re-run; --reset wipes the demo content first).'

    def add_arguments(self, parser):
        parser.add_argument('--reset', action='store_true', help='Delete existing demo content before seeding.')

    def handle(self, *args, **opts):
        if opts['reset']:
            self.reset()
        with transaction.atomic():
            self.seed_slides()
            colors = self.seed_colors()
            catalog = self.seed_catalog(colors)
            self.seed_collections(catalog, colors)
            self.seed_pages()
            self.seed_blogs()
            self.seed_partners()
            self.seed_user_and_orders()
        self.stdout.write(self.style.SUCCESS(
            f'Demo data ready. Sign in as {DEMO_EMAIL} / {DEMO_PASSWORD}.'))

    def reset(self):
        for model in (Order, Slide, Partner, Blog, Page, ContactMessage, models.Product, models.Category, models.Color):
            model.objects.all().delete()
        User.objects.filter(email=DEMO_EMAIL).delete()
        self.stdout.write('Existing demo content deleted.')

    def seed_slides(self):
        if Slide.objects.exists():
            return
        rnd = random.Random(11)
        for n, (title, title_ka, sub, sub_ka, link, colors) in enumerate(SLIDES):
            slide = Slide(title=title, title_ka=title_ka, subtitle=sub, subtitle_ka=sub_ka, link=link, order=n)
            slide.image.save(f'slide-{n}.jpg', blob_image(colors, rnd), save=False)
            slide.save()
        self.stdout.write('Slides created.')

    def seed_colors(self):
        return [models.Color.objects.get_or_create(name=n, defaults={'name_ka': ka, 'hex': hx})[0]
                for n, ka, hx in COLORS]

    def seed_catalog(self, colors):
        """Returns [[Product, ...] per category]; skipped when categories already exist."""
        if models.Category.objects.exists():
            return [list(c.products.order_by('id')) for c in models.Category.objects.order_by('order')]
        rnd = random.Random(7)
        tones = ['#c8553d', '#588b8b', '#f28f3b', '#6d597a']
        result = []
        for i, (name, name_ka, desc, desc_ka, products) in enumerate(CATEGORIES):
            cat = models.Category(name=name, name_ka=name_ka, order=i,
                                  description=f'<p>{desc}</p>', description_ka=f'<p>{desc_ka}</p>')
            cat.image.save(f'category-{i}.jpg', placeholder(name, tones[i % len(tones)]), save=False)
            cat.save()
            items = []
            for j, (pname, pname_ka, price, sizes) in enumerate(products):
                product = models.Product.objects.create(
                    category=cat, name=pname, name_ka=pname_ka, price=Decimal(str(price)),
                    discount_percent=rnd.choice([0, 0, 0, 10, 20, 30]), is_popular=j < 2,
                    description=f'<p>A lovely {pname.lower()} from the Didostati {name.lower()} range.</p>'
                                '<p>Made to last and easy to love.</p>',
                    description_ka=f'<p>მშვენიერი {pname_ka} Didostati-ს „{name_ka}“ ასორტიმენტიდან.</p>'
                                   '<p>გაგრძელებისთვის და საყვარელი.</p>')
                self.add_variants(product, rnd, colors, sizes)
                items.append(product)
            result.append(items)
        self.stdout.write('Categories and products created.')
        return result

    @staticmethod
    def add_variants(product, rnd, colors, sizes=()):
        chosen = rnd.sample(colors, 3)
        product.colors.set(chosen)
        for k, c in enumerate(chosen):
            img = models.ProductImage(product=product, color=c, order=k)
            img.image.save(f'{product.slug}-{c.name.lower()}.jpg', placeholder(product.name, c.hex), save=False)
            img.save()
        for k, (name, name_ka, price) in enumerate(sizes):
            models.ProductSize.objects.create(
                product=product, name=name, name_ka=name_ka, order=k,
                price=None if price is None else Decimal(str(price)))

    def seed_collections(self, catalog, colors):
        if models.CollectionItem.objects.exists() or not catalog:
            return
        cat = models.Category.objects.order_by('order').first()
        rnd = random.Random(21)
        for name, name_ka, desc, desc_ka, price, discount, contents in COLLECTIONS:
            coll = models.Product.objects.create(
                category=cat, name=name, name_ka=name_ka, price=Decimal(str(price)), discount_percent=discount,
                is_popular=True, description=f'<p>{desc}</p>', description_ka=f'<p>{desc_ka}</p>')
            # A collection's own pictures; its products' pictures are added to the gallery automatically.
            img = models.ProductImage(product=coll, order=0)
            img.image.save(f'{coll.slug}.jpg', placeholder(name, '#6d597a'), save=False)
            img.save()
            coll.colors.set(rnd.sample(colors, 2))
            for ci, pi, qty in contents:
                models.CollectionItem.objects.get_or_create(
                    collection=coll, product=catalog[ci][pi], defaults={'quantity': qty})
        self.stdout.write('Collections created.')

    def seed_pages(self):
        for slug, title, title_ka, body, body_ka in PAGES:
            Page.objects.get_or_create(slug=slug, defaults={
                'title': title, 'title_ka': title_ka, 'content': body, 'content_ka': body_ka})

    def seed_blogs(self):
        if Blog.objects.exists():
            return
        tones = ['#c8553d', '#588b8b', '#f28f3b']
        for n, (title, title_ka, ex, ex_ka, body, body_ka) in enumerate(BLOGS):
            b = Blog(title=title, title_ka=title_ka, excerpt=ex, excerpt_ka=ex_ka, content=body, content_ka=body_ka)
            b.cover_image.save(f'blog{n}.jpg', placeholder(title, tones[n % len(tones)], (1000, 600)), save=False)
            b.save()
        self.stdout.write('Blog posts created.')

    def seed_partners(self):
        if Partner.objects.exists():
            return
        for n, (name, name_ka, link, hx) in enumerate(PARTNERS):
            partner = Partner(name=name, name_ka=name_ka, link=link, order=n)
            partner.logo.save(f'partner-{n}.jpg', placeholder(name, hx, (400, 200)), save=False)
            partner.save()
        self.stdout.write('Partners created.')

    def seed_user_and_orders(self):
        user, created = User.objects.get_or_create(
            email=DEMO_EMAIL, defaults={'first_name': 'Demo', 'last_name': 'Customer'})
        if not created:
            return
        user.set_password(DEMO_PASSWORD)
        user.save()
        address = dict(full_name='Demo Customer', phone='+995 555 000 000', line1='Rustaveli Ave 1',
                       city='Tbilisi', postal_code='0108', country='Georgia')
        Address.objects.create(user=user, label='Home', is_default=True, **address)
        Address.objects.create(user=user, label='Work', **{**address, 'line1': 'Chavchavadze Ave 10'})
        products = list(models.Product.objects.filter(is_active=True).prefetch_related('sizes', 'colors')[:6])
        for status, picks in (('delivered', products[:2]), ('processing', products[2:4]), ('new', products[4:6])):
            order = Order.objects.create(user=user, email=user.email, status=status, note='Demo order',
                                         payment_provider='bog', payment_status='paid', payment_id=f'demo-{status}', **address)
            total = Decimal(0)
            for p in picks:
                size, color = p.sizes.first(), p.colors.first()
                unit = size.final_price if size else p.final_price
                OrderItem.objects.create(
                    order=order, product=p, product_name=p.name, color_name=color.name if color else '',
                    size_name=size.name if size else '', unit_price=unit, quantity=2)
                total += unit * 2
            order.total = total
            order.save(update_fields=['total'])
        ContactMessage.objects.create(name='Demo Customer', email=user.email,
                                      message='Hello! Do you ship tablecloths abroad?')
        self.stdout.write('Demo user, addresses, orders and a contact message created.')
