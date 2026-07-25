import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from accessories.models import Product, ProductImage
from dashboard.models import Setting

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


class Command(BaseCommand):
    help = "Seed the database with sample data for local development"

    def handle(self, *args, **options):
        self.seed_settings()
        self.seed_products()

    def seed_products(self):
        Product.objects.all().delete()

        image_path = os.path.join(settings.MEDIA_ROOT, "products", "images", "nuts.png")

        for data in SAMPLE_PRODUCTS:
            product = Product.objects.create(**data)
            with open(image_path, "rb") as image_file:
                product_image = ProductImage(product=product)
                product_image.image.save("nuts.png", File(image_file), save=True)

        self.stdout.write(self.style.SUCCESS(f"Created {len(SAMPLE_PRODUCTS)} sample products"))

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
