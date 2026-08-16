import os

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from products.models import Product, ProductBuyingOption, NutritionalValue
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

# Product no longer carries its own price/stock (see ProductBuyingOption) -
# "price" below is only a seeding reference used to derive each buying option's
# price and is never passed to Product.objects.create().
SAMPLE_PRODUCTS = [
    {"title": "مكسرات مشكلة فاخرة", "description": "تشكيلة فاخرة من أجود أنواع المكسرات المحمصة الطازجة.", "price": 350, "stock": 25, "rating": 5},
    {"title": "لوز محمص", "description": "لوز محمص ومملح بعناية للحصول على قرمشة مثالية.", "price": 420, "stock": 18, "rating": 4},
    {"title": "كاجو محمص", "description": "كاجو فاخر محمص طازج بدون إضافات صناعية.", "price": 480, "stock": 30, "rating": 5},
    {"title": "فستق حلبي", "description": "فستق حلبي أصلي مقرمش ذو نكهة غنية.", "price": 550, "stock": 12, "rating": 4},
    {"title": "عين جمل", "description": "عين جمل طازج غني بالفوائد الصحية والطعم الغني.", "price": 400, "stock": 40, "rating": 5},
    {"title": "بندق محمص", "description": "بندق محمص فاخر يتميز بطعمه الغني ورائحته المميزة.", "price": 380, "stock": 20, "rating": 4},
    {"title": "فول سوداني محمص", "description": "فول سوداني محمص ومملح، وجبة خفيفة مثالية.", "price": 150, "stock": 35, "rating": 3},
    {"title": "لب سوري محمص", "description": "لب سوري محمص بالملح بنكهة مميزة.", "price": 140, "stock": 45, "rating": 5},
    {"title": "لب أبيض", "description": "بذر قرع محمص ومملح غني بالبروتين.", "price": 160, "stock": 22, "rating": 4},
    {"title": "حمص أبيض محمص", "description": "حمص محمص مقرمش، وجبة خفيفة شعبية ولذيذة.", "price": 120, "stock": 28, "rating": 4},
    {"title": "ذرة محمصة", "description": "ذرة محمصة مقرمشة بنكهة مميزة.", "price": 100, "stock": 24, "rating": 5},
    {"title": "زبيب مجفف", "description": "زبيب طبيعي مجفف بدون سكر مضاف.", "price": 180, "stock": 33, "rating": 4},
    {"title": "تمر بالمكسرات", "description": "تمر فاخر محشو بمزيج من المكسرات المختارة.", "price": 320, "stock": 15, "rating": 3},
    {"title": "مشكل فواكه مجففة ومكسرات", "description": "خليط متوازن من الفواكه المجففة والمكسرات الفاخرة.", "price": 450, "stock": 16, "rating": 4},
    {"title": "صنوبر فاخر", "description": "صنوبر فاخر نقي بطعم غني ورائحة مميزة.", "price": 600, "stock": 10, "rating": 5},
]

# Every product must have at least one buying option (see ProductForm's inline
# formset, which requires >= 1). Seeding gives each product these three sizes,
# priced as a fraction of the product's reference price above. "كيلو كامل" is
# flagged as the default option, so product.price resolves to the same value
# the old flat Product.price field used to hold.
BUYING_OPTION_TEMPLATES = [
    {"name": "ربع كيلو", "amount": 250, "unit": "g", "price_factor": 0.25, "is_default": False},
    {"name": "نص كيلو", "amount": 500, "unit": "g", "price_factor": 0.5, "is_default": False},
    {"name": "كيلو كامل", "amount": 1, "unit": "kg", "price_factor": 1, "is_default": True},
]

# Every product gets this same reference nutritional label (per 100g) for seeding purposes.
NUTRITIONAL_VALUE_TEMPLATES = [
    {"name": "الطاقة", "description": "2502 كيلوجول / 597 سعر حراري"},
    {"name": "الدهون", "description": "47 جرام"},
    {"name": "الكربوهيدرات", "description": "22 جرام"},
    {"name": "البروتين", "description": "21 جرام"},
]

# Product List sections require a banner (see Section.clean). Seeding copies the real artwork
# from media/dashboard/sections/ via ImageField.save() so it's stored like a normal upload
# (and picked up correctly by django-cleanup's delete signal).
SAMPLE_SECTIONS = [
    {"name": "وصل حديثاً", "type": SectionType.PRODUCT_LIST, "banner_file": "Newly_arrived.png", "list": "وصل حديثاً"},
    {"name": "الأفضل مبيعاً", "type": SectionType.PRODUCT_LIST, "banner_file": "Best_seller.png", "list": "الأفضل مبيعاً"},
    {"name": "ليه تختارنا؟", "type": SectionType.WHY_CHOOSE_US, "banner_file": None, "list": None},
    {"name": "أكياس سوفكس", "type": SectionType.PRODUCT_LIST, "banner_file": "Products.png", "list": "أكياس سوفكس"},
    {"name": "قسم ثاني", "type": SectionType.PRODUCT_LIST, "banner_file": "Products.png", "list": "قسم ثاني"},
    {"name": "قسم ثالث", "type": SectionType.PRODUCT_LIST, "banner_file": "Products.png", "list": "قسم ثالث"},
    {"name": "عروض رمضان", "type": SectionType.PRODUCT_LIST, "banner_file": "Products.png", "list": "عروض رمضان"},
    {"name": "آراء عملاءنا", "type": SectionType.REVIEWS, "banner_file": None, "list": None},
    {"name": "تاجر معانا", "type": SectionType.SELL_WITH_US, "banner_file": None, "list": None},
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
            product = Product.objects.create(
                title=data["title"],
                description=data["description"],
                rating=data["rating"],
            )
            with open(image_path, "rb") as image_file:
                product.image.save("nuts.png", File(image_file), save=True)

            for option in BUYING_OPTION_TEMPLATES:
                ProductBuyingOption.objects.create(
                    product=product,
                    name=option["name"],
                    amount=option["amount"],
                    unit=option["unit"],
                    price=round(data["price"] * option["price_factor"]),
                    stock=data["stock"],
                    is_default=option["is_default"],
                )

            for value in NUTRITIONAL_VALUE_TEMPLATES:
                NutritionalValue.objects.create(
                    product=product,
                    name=value["name"],
                    description=value["description"],
                )

            products.append(product)

        self.stdout.write(self.style.SUCCESS(f"Created {len(products)} sample products with buying options"))
        return products

    def seed_settings(self):
        setting = Setting.objects.first()
        offer_banner_text = "اطلب قبل 18 ديسمبر علشان توصلك الأوردرات قبل الكريسماس 🎄🎁"
        default_shipping_fees = 50

        if setting is None:
            setting = Setting.objects.create(
                offer_banner_text=offer_banner_text,
                default_shipping_fees=default_shipping_fees,
            )
            self.stdout.write(self.style.SUCCESS("Created site settings"))
        else:
            setting.offer_banner_text = offer_banner_text
            setting.default_shipping_fees = default_shipping_fees
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

        bags = ProductList.objects.create(
            name="أكياس سوفكس",
            limit=6,
            sort_by=ProductSortField.CREATED_AT,
            sort_direction=SortDirection.DESC,
        )
        bags.product_ids.set(products[0:8])

        second_section = ProductList.objects.create(
            name="قسم ثاني",
            limit=6,
            sort_by=ProductSortField.CREATED_AT,
            sort_direction=SortDirection.DESC,
        )
        second_section.product_ids.set(products[2:10])

        third_section = ProductList.objects.create(
            name="قسم ثالث",
            limit=6,
            sort_by=ProductSortField.CREATED_AT,
            sort_direction=SortDirection.DESC,
        )
        third_section.product_ids.set(products[4:12])

        ramadan_offers = ProductList.objects.create(
            name="عروض رمضان",
            limit=6,
            sort_by=ProductSortField.CREATED_AT,
            sort_direction=SortDirection.DESC,
        )
        ramadan_offers.product_ids.set(products[6:14])

        product_lists = {
            "وصل حديثاً": recent,
            "الأفضل مبيعاً": best_selling,
            "أكياس سوفكس": bags,
            "قسم ثاني": second_section,
            "قسم ثالث": third_section,
            "عروض رمضان": ramadan_offers,
        }
        self.stdout.write(self.style.SUCCESS(f"Created {len(product_lists)} product lists"))
        return product_lists

    def seed_sections(self, product_lists):
        Section.objects.all().delete()

        banners_dir = os.path.join(settings.MEDIA_ROOT, "dashboard", "sections")

        for order, data in enumerate(SAMPLE_SECTIONS, start=1):
            section = Section(
                name=data["name"],
                type=data["type"],
                order=order,
                product_list=product_lists.get(data["list"]),
            )
            section.save()

            banner_file = data["banner_file"]
            if banner_file:
                with open(os.path.join(banners_dir, banner_file), "rb") as image_file:
                    section.banner.save(banner_file, File(image_file), save=True)

        self.stdout.write(self.style.SUCCESS(f"Created {len(SAMPLE_SECTIONS)} sections"))

    def seed_sell_with_us_cards(self):
        SellWithUsCard.objects.all().delete()

        for order, data in enumerate(SAMPLE_SELL_WITH_US_CARDS, start=1):
            SellWithUsCard.objects.create(order=order, **data)

        self.stdout.write(self.style.SUCCESS(f"Created {len(SAMPLE_SELL_WITH_US_CARDS)} sell with us cards"))
