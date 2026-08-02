import os
from io import BytesIO

from PIL import Image

from django.conf import settings
from django.core.files import File
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand

from accessories.models import Product, ProductImage
from dashboard.models import (
    ProductList,
    ProductSortField,
    Section,
    SectionType,
    SellWithUsCard,
    SellWithUsColor,
    SellWithUsIcon,
    Setting,
    SortDirection,
)

SAMPLE_PRODUCTS = [
    {"title": "مكسرات مشكلة فاخرة", "description": "تشكيلة فاخرة من أجود أنواع المكسرات المحمصة الطازجة.", "price": 350, "stock": 25, "discount": 10, "rating": 5},
    {"title": "لوز محمص", "description": "لوز محمص ومملح بعناية للحصول على قرمشة مثالية.", "price": 420, "stock": 18, "discount": 0, "rating": 4},
    {"title": "كاجو محمص", "description": "كاجو فاخر محمص طازج بدون إضافات صناعية.", "price": 480, "stock": 30, "discount": 15, "rating": 5},
    {"title": "فستق حلبي", "description": "فستق حلبي أصلي مقرمش ذو نكهة غنية.", "price": 550, "stock": 12, "discount": 5, "rating": 4},
    {"title": "عين جمل", "description": "عين جمل طازج غني بالفوائد الصحية والطعم الغني.", "price": 400, "stock": 40, "discount": 0, "rating": 5},
    {"title": "بندق محمص", "description": "بندق محمص فاخر يتميز بطعمه الغني ورائحته المميزة.", "price": 380, "stock": 20, "discount": 20, "rating": 4},
    {"title": "فول سوداني محمص", "description": "فول سوداني محمص ومملح، وجبة خفيفة مثالية.", "price": 150, "stock": 35, "discount": 0, "rating": 3},
    {"title": "لب سوري محمص", "description": "لب سوري محمص بالملح بنكهة مميزة.", "price": 140, "stock": 45, "discount": 10, "rating": 5},
    {"title": "لب أبيض", "description": "بذر قرع محمص ومملح غني بالبروتين.", "price": 160, "stock": 22, "discount": 0, "rating": 4},
    {"title": "حمص أبيض محمص", "description": "حمص محمص مقرمش، وجبة خفيفة شعبية ولذيذة.", "price": 120, "stock": 28, "discount": 25, "rating": 4},
    {"title": "ذرة محمصة", "description": "ذرة محمصة مقرمشة بنكهة مميزة.", "price": 100, "stock": 24, "discount": 0, "rating": 5},
    {"title": "زبيب مجفف", "description": "زبيب طبيعي مجفف بدون سكر مضاف.", "price": 180, "stock": 33, "discount": 10, "rating": 4},
    {"title": "تمر بالمكسرات", "description": "تمر فاخر محشو بمزيج من المكسرات المختارة.", "price": 320, "stock": 15, "discount": 0, "rating": 3},
    {"title": "مشكل فواكه مجففة ومكسرات", "description": "خليط متوازن من الفواكه المجففة والمكسرات الفاخرة.", "price": 450, "stock": 16, "discount": 15, "rating": 4},
    {"title": "صنوبر فاخر", "description": "صنوبر فاخر نقي بطعم غني ورائحة مميزة.", "price": 600, "stock": 10, "discount": 0, "rating": 5},
]

# Product List sections require a banner (see Section.clean). Real banner artwork is uploaded
# later via the dashboard; seeding generates a solid-color placeholder instead of depending on
# a file living under MEDIA_ROOT, since dashboard/sections/ has no date subfolder and any file
# placed there directly is indistinguishable from a real upload to django-cleanup's delete signal.
SAMPLE_SECTIONS = [
    {"name": "وصل حديثاً", "type": SectionType.PRODUCT_LIST, "banner_color": (222, 184, 135), "list": "وصل حديثاً"},
    {"name": "الأفضل مبيعاً", "type": SectionType.PRODUCT_LIST, "banner_color": (205, 133, 63), "list": "الأفضل مبيعاً"},
    {"name": "ليه تختارنا", "type": SectionType.WHY_CHOOSE_US, "banner_color": None, "list": None},
    {"name": "مختارة 1", "type": SectionType.PRODUCT_LIST, "banner_color": (160, 82, 45), "list": "مختارة"},
    {"name": "مختارة 2", "type": SectionType.PRODUCT_LIST, "banner_color": (160, 82, 45), "list": "مختارة"},
    {"name": "تقييمات", "type": SectionType.REVIEWS, "banner_color": None, "list": None},
    {"name": "شاركنا", "type": SectionType.SELL_WITH_US, "banner_color": None, "list": None},
]

SAMPLE_SELL_WITH_US_CARDS = [
    {
        "title": "حتى لو مكانك بعيد عننا؟",
        "svg": SellWithUsIcon.GLOBE,
        "bg_color": SellWithUsColor.YELLOW,
        "span": 1,
    },
    {
        "title": "وتعلي إيراداتك من غير تعب زيادة؟",
        "svg": SellWithUsIcon.REVENUE_GROWTH,
        "bg_color": SellWithUsColor.GREEN,
        "span": 1,
    },
    {
        "title": "عايز تزود ربحك من بيع المكسرات؟",
        "svg": SellWithUsIcon.COINS_HAND,
        "bg_color": SellWithUsColor.YELLOW,
        "span": 1,
    },
    {
        "title": "تاجر مع سوفكس",
        "svg": SellWithUsIcon.NUTS_BAG,
        "bg_color": SellWithUsColor.PINK,
        "span": 2,
        "description": "مكسرات بجودة عالية وأسعار تنافسية توصلّك لحد عندك وفي معادها.",
        "cta_text": "اطلب من سوفكس الآن",
        "cta_url": "#",
    },
    {
        "title": "ومحتاج طلبيات توصلك في مواعيد ثابتة؟",
        "svg": SellWithUsIcon.PAYMENT_PLAN,
        "bg_color": SellWithUsColor.GREEN,
        "span": 1,
    },
]


class Command(BaseCommand):
    help = "Seed the database with sample data for local development"

    def handle(self, *args, **options):
        self.seed_settings()
        products = self.seed_products()
        product_lists = self.seed_product_lists(products)
        self.seed_sections(product_lists)
        self.seed_sell_with_us_cards()

    def seed_products(self):
        Product.objects.all().delete()

        image_path = os.path.join(settings.MEDIA_ROOT, "products", "images", "nuts.png")

        products = []
        for data in SAMPLE_PRODUCTS:
            product = Product.objects.create(**data)
            with open(image_path, "rb") as image_file:
                product_image = ProductImage(product=product)
                product_image.image.save("nuts.png", File(image_file), save=True)
            products.append(product)

        self.stdout.write(self.style.SUCCESS(f"Created {len(products)} sample products"))
        return products

    def seed_settings(self):
        setting = Setting.objects.first()
        offer_banner_text = "اطلب قبل 18 ديسمبر علشان توصلك الأوردرات قبل الكريسماس 🎄🎁"

        if setting is None:
            setting = Setting.objects.create(offer_banner_text=offer_banner_text)
            self.stdout.write(self.style.SUCCESS("Created site settings"))
        else:
            setting.offer_banner_text = offer_banner_text
            setting.save()
            self.stdout.write(self.style.SUCCESS("Updated site settings"))

    def seed_product_lists(self, products):
        ProductList.objects.all().delete()

        recent = ProductList.objects.create(
            name="وصل حديثاً",
            limit=6,
            sort_by=ProductSortField.CREATED_AT,
            sort_direction=SortDirection.DESC,
        )

        best_selling = ProductList.objects.create(
            name="الأفضل مبيعاً",
            limit=5,
            sort_by=ProductSortField.CREATED_AT,
            sort_direction=SortDirection.DESC,
        )
        best_selling.product_ids.set(products[6:11])

        featured = ProductList.objects.create(
            name="مختارة",
            limit=6,
            sort_by=ProductSortField.CREATED_AT,
            sort_direction=SortDirection.DESC,
        )
        featured.product_ids.set(products[1:11])

        product_lists = {"وصل حديثاً": recent, "الأفضل مبيعاً": best_selling, "مختارة": featured}
        self.stdout.write(self.style.SUCCESS(f"Created {len(product_lists)} product lists"))
        return product_lists

    def seed_sections(self, product_lists):
        Section.objects.all().delete()

        for order, data in enumerate(SAMPLE_SECTIONS, start=1):
            section = Section(
                name=data["name"],
                type=data["type"],
                order=order,
                product_list=product_lists.get(data["list"]),
            )
            section.save()

            if data["banner_color"]:
                section.banner.save(f"placeholder_{order}.png", self._placeholder_banner(data["banner_color"]), save=True)

        self.stdout.write(self.style.SUCCESS(f"Created {len(SAMPLE_SECTIONS)} sections"))

    def seed_sell_with_us_cards(self):
        SellWithUsCard.objects.all().delete()

        for order, data in enumerate(SAMPLE_SELL_WITH_US_CARDS, start=1):
            SellWithUsCard.objects.create(order=order, **data)

        self.stdout.write(self.style.SUCCESS(f"Created {len(SAMPLE_SELL_WITH_US_CARDS)} sell with us cards"))

    def _placeholder_banner(self, color, size=(1200, 300)):
        buffer = BytesIO()
        Image.new("RGB", size, color=color).save(buffer, format="PNG")
        return ContentFile(buffer.getvalue())
