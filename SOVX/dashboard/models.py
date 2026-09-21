import random

from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from products.models import Product

class Setting(models.Model):
    whatsapp_number = models.CharField(
       max_length=20,
       blank=True,
       help_text="WhatsApp number with country code, without + or spaces"
    )
    
    offer_banner_text = models.CharField(
        verbose_name="نص شريط العروض",
        help_text="النص الذي يظهر في الشريط العلوي للصفحة الرئيسية",
        default="",
        max_length=250,
    )
    facebook_link = models.CharField(verbose_name="رابط فيسبوك", default="", max_length=50, blank=True)
    instgram_link = models.CharField(verbose_name="رابط إنستجرام", default="", max_length=50, blank=True)
    email = models.EmailField(verbose_name="البريد الإلكتروني", blank=True)
    whatsapp_number = models.CharField(
        verbose_name="رقم واتساب",
        default="",
        max_length=20,
        blank=True,
        help_text="رقم واتساب لروابط التواصل. أرقام فقط مع كود الدولة، بدون + أو مسافات (مثال: 201550204045).",
    )

    phone_number = models.CharField(
        verbose_name="رقم الهاتف",
        default="",
        max_length=20,
        blank=True,
        help_text="رقم الهاتف لروابط التواصل. أرقام فقط مع كود الدولة، بدون + أو مسافات (مثال: 201550204045).",
    )

    location_text = models.CharField(
        verbose_name="نص الموقع", default="", help_text="دمياط الجديدة، محافظة دمياط، مصر", max_length=100
    )
    location_url = models.URLField(
        verbose_name="رابط الموقع على الخريطة", default="", help_text="https://maps.app.goo.gl/i4M9Uff18EWoceR68"
    )

    workdays = models.CharField(verbose_name="أيام العمل", default="الأحد - الخميس", help_text="أيام العمل", max_length=50)
    workhours = models.CharField(
        verbose_name="ساعات العمل", default="9:00 صباحًا - 5:00 مساءً", help_text="ساعات العمل", max_length=50
    )

    default_shipping_fees = models.PositiveIntegerField(
        verbose_name="رسوم الشحن الافتراضية",
        default=0,
        help_text="رسوم الشحن الافتراضية المعروضة قبل معرفة المدينة (مثلاً في سلة المشتريات)، تُستخدم لحين تحديد رسوم فعلية للمحافظة/المدينة.",
    )

    notify_on_order = models.BooleanField(
        verbose_name="إشعار عند إنشاء طلب جديد",
        default=True,
        help_text="إرسال بريد إلكتروني إلى البريد الإلكتروني أعلاه عند إنشاء طلب جديد.",
    )
    notify_on_order_status_change = models.BooleanField(
        verbose_name="إشعار عند تغيير حالة الطلب",
        default=True,
        help_text="إرسال بريد إلكتروني إلى البريد الإلكتروني أعلاه عند تغيّر حالة أي طلب.",
    )
    notify_on_contact_us = models.BooleanField(
        verbose_name="إشعار عند رسالة تواصل معنا",
        default=True,
        help_text="إرسال بريد إلكتروني إلى البريد الإلكتروني أعلاه عند إرسال نموذج تواصل معنا.",
    )
    notify_on_sell_with_us = models.BooleanField(
        verbose_name="إشعار عند طلب بيع معنا",
        default=True,
        help_text="إرسال بريد إلكتروني إلى البريد الإلكتروني أعلاه عند إرسال نموذج بيع معنا.",
    )

    class Meta:
        verbose_name = "الإعدادات"
        verbose_name_plural = "الإعدادات"


class Governorate(models.Model):
    name_ar = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)

    class Meta:
        ordering = ["name_en"]
        verbose_name = "المحافظة"
        verbose_name_plural = "المحافظات"

    def __str__(self):
        return self.name_ar


class City(models.Model):
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name="cities")
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)

    class Meta:
        ordering = ["name_en"]
        verbose_name = "المدينة"
        verbose_name_plural = "المدن"

    def __str__(self):
        return f"{self.name_ar} ({self.governorate.name_ar})"


class ShippingFee(models.Model):
    governorate = models.ForeignKey(
        Governorate, on_delete=models.CASCADE, related_name="shipping_fees", verbose_name="المحافظة"
    )
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="shipping_fees",
        null=True,
        blank=True,
        verbose_name="المدينة",
        help_text="اتركه فارغًا لتطبيق هذه الرسوم على كل مدن المحافظة التي ليس لها رسوم خاصة بها.",
    )
    cost = models.PositiveIntegerField(verbose_name="التكلفة (جنيه)", default=0)

    class Meta:
        # Blocks two rows for the same (governorate, city) pair. It doesn't
        # cover two governorate-wide rows (city=NULL) for the same
        # governorate - NULL is never "equal" to NULL in a unique index -
        # so that case is enforced in clean() below instead.
        unique_together = [("governorate", "city")]
        ordering = ["governorate__name_en", "city__name_en"]
        verbose_name = "رسوم الشحن"
        verbose_name_plural = "رسوم الشحن"

    def clean(self):
        super().clean()

        if self.city_id and self.governorate_id and self.city.governorate_id != self.governorate_id:
            raise ValidationError({"city": "هذه المدينة لا تنتمي إلى المحافظة المختارة."})

        duplicates = ShippingFee.objects.filter(governorate_id=self.governorate_id, city_id=self.city_id)
        if self.pk:
            duplicates = duplicates.exclude(pk=self.pk)
        if duplicates.exists():
            scope = str(self.city) if self.city_id else "كل المدن (على مستوى المحافظة)"
            raise ValidationError(f"رسوم شحن لـ {scope} في {self.governorate} موجودة بالفعل.")

    def __str__(self):
        scope = self.city.name_en if self.city_id else "All cities"
        return f"{self.governorate.name_en} - {scope}: {self.cost} EGP"

    @classmethod
    def get_fee(cls, governorate_id, city_id=None):
        """Resolve the shipping cost for a governorate/city pair.

        Prefers a fee configured for that exact city, falling back to the
        governorate-wide fee (city=None). Returns None if neither exists.
        """
        if not governorate_id:
            return None

        if city_id:
            fee = (
                cls.objects.filter(governorate_id=governorate_id, city_id=city_id)
                .values_list("cost", flat=True)
                .first()
            )
            if fee is not None:
                return fee

        return (
            cls.objects.filter(governorate_id=governorate_id, city__isnull=True)
            .values_list("cost", flat=True)
            .first()
        )


class ProductSortField(models.TextChoices):
    RATING = "rating", "التقييم"
    CREATED_AT = "created_at", "تاريخ الإضافة"


class SortDirection(models.TextChoices):
    ASC = "asc", "تصاعدي"
    DESC = "desc", "تنازلي"


class ProductList(models.Model):
    name = models.CharField(verbose_name="الاسم", max_length=150)
    limit = models.PositiveIntegerField(
        verbose_name="عدد المنتجات",
        validators=[MinValueValidator(4), MaxValueValidator(16)],
        help_text="عدد المنتجات المعروضة (من 4 إلى 16)",
    )
    product_ids = models.ManyToManyField(
        Product, blank=True, verbose_name="المنتجات", help_text="اتركه فارغًا لتضمين كل المنتجات"
    )
    sort_by = models.CharField(
        verbose_name="ترتيب حسب", max_length=20, choices=ProductSortField.choices, default=ProductSortField.CREATED_AT
    )
    sort_direction = models.CharField(
        verbose_name="اتجاه الترتيب", max_length=4, choices=SortDirection.choices, default=SortDirection.DESC
    )

    class Meta:
        verbose_name = "قائمة المنتجات"
        verbose_name_plural = "قوائم المنتجات"

    def get_products(self):
        queryset = self.product_ids.all() if self.product_ids.exists() else Product.objects.all()
        order_field = self.sort_by if self.sort_direction == SortDirection.ASC else f"-{self.sort_by}"
        return queryset.order_by(order_field)[: self.limit]

    def __str__(self):
        return self.name


class SectionType(models.TextChoices):
    PRODUCT_LIST = "product_list", "قائمة منتجات"
    REVIEWS = "reviews", "التقييمات"
    WHY_CHOOSE_US = "why_choose_us", "ليه تختارنا"
    SELL_WITH_US = "sell_with_us", "تاجر معنا"
    HERO_CAROUSEL = "hero_carousel", "سلايدر الصور"
    CATEGORY_LINKS = "category_links", "روابط الأقسام"


class Section(models.Model):
    name = models.CharField(verbose_name="الاسم", max_length=150)
    type = models.CharField(verbose_name="النوع", max_length=20, choices=SectionType.choices)
    order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)
    show_link = models.BooleanField(
        verbose_name="إظهار الرابط",
        default=True,
        help_text="إظهار هذا القسم في القائمة العلوية وقسم روابط الأقسام",
    )
    banner = models.ImageField(verbose_name="صورة الغلاف", upload_to="dashboard/sections/", blank=True)
    product_list = models.ForeignKey(
        ProductList,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="sections",
        verbose_name="قائمة المنتجات",
    )

    class Meta:
        ordering = ["order"]
        verbose_name = "القسم"
        verbose_name_plural = "الأقسام"

    def clean(self):
        super().clean()
        if self.type == SectionType.PRODUCT_LIST and not self.banner:
            raise ValidationError({"banner": "صورة الغلاف مطلوبة لأقسام قائمة المنتجات."})

    def __str__(self):
        return self.name


class HeroSlide(models.Model):
    image = models.ImageField(verbose_name="الصورة", upload_to="dashboard/hero/")
    alt_text = models.CharField(verbose_name="النص البديل", max_length=150, blank=True)
    disabled = models.BooleanField(verbose_name="معطل", default=False, help_text="إخفاء هذه الصورة من السلايدر")
    order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "صورة سلايدر"
        verbose_name_plural = "صور السلايدر"

    def __str__(self):
        return self.alt_text or f"صورة {self.pk}"


class SellWithUsIcon(models.TextChoices):
    GLOBE = "globe", "كرة أرضية"
    REVENUE_GROWTH = "revenue_growth", "نمو الإيرادات"
    COINS_HAND = "coins_hand", "عملات في اليد"
    PAYMENT_PLAN = "payment_plan", "خطة دفع"
    NUTS_BAG = "nuts_bag", "كيس مكسرات"


SELL_WITH_US_ICON_FILES = {
    SellWithUsIcon.GLOBE: "globe.svg",
    SellWithUsIcon.REVENUE_GROWTH: "revenue-growth.svg",
    SellWithUsIcon.COINS_HAND: "coins-hand.svg",
    SellWithUsIcon.PAYMENT_PLAN: "payment-plan.png",
    SellWithUsIcon.NUTS_BAG: "nuts-bag.png",
}


class SellWithUsColor(models.TextChoices):
    YELLOW = "#fffcdd", "أصفر"
    GREEN = "#e7ffdc", "أخضر"
    PINK = "#ffecee", "وردي"


class SellWithUsCardSpan(models.IntegerChoices):
    SINGLE = 1, "عمود واحد"
    DOUBLE = 2, "عمودان"


class SellWithUsCard(models.Model):
    title = models.CharField(verbose_name="العنوان", max_length=150)
    svg = models.CharField(verbose_name="الأيقونة", max_length=20, choices=SellWithUsIcon.choices)
    bg_color = models.CharField(
        verbose_name="لون الخلفية", max_length=7, choices=SellWithUsColor.choices, default=SellWithUsColor.YELLOW
    )
    description = models.TextField(
        verbose_name="الوصف", blank=True, help_text="نص اختياري يظهر أسفل العنوان"
    )
    cta_text = models.CharField(
        verbose_name="نص زر الإجراء", max_length=50, blank=True, help_text="نص زر الدعوة لاتخاذ إجراء (اختياري)"
    )
    disabled = models.BooleanField(verbose_name="معطل", default=False, help_text="إخفاء هذه البطاقة من الصفحة الرئيسية")
    span = models.PositiveSmallIntegerField(
        verbose_name="العرض", choices=SellWithUsCardSpan.choices, default=SellWithUsCardSpan.SINGLE
    )
    order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "بطاقة تاجر معنا"
        verbose_name_plural = "بطاقات تاجر معنا"

    @property
    def icon_path(self):
        return f"images/sections/sell-with-us/{SELL_WITH_US_ICON_FILES[self.svg]}"

    def __str__(self):
        return self.title


class ReviewType(models.TextChoices):
    MALE = "male", "ذكر"
    FEMALE = "female", "أنثى"


REVIEW_AVATAR_FILES = {
    ReviewType.MALE: ["male_1.png", "male_2.png"],
    ReviewType.FEMALE: ["female.png"],
}


class Review(models.Model):
    name = models.CharField(verbose_name="الاسم", max_length=150)
    date = models.DateField(verbose_name="التاريخ")
    type = models.CharField(verbose_name="النوع", max_length=10, choices=ReviewType.choices, default=ReviewType.MALE)
    description = models.TextField(verbose_name="نص التقييم")
    order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "تقييم"
        verbose_name_plural = "التقييمات"

    @property
    def avatar_path(self):
        # male reviews get one of two portraits at random each time it's read
        return f"images/icons/{random.choice(REVIEW_AVATAR_FILES[self.type])}"

    def __str__(self):
        return self.name


class Article(models.Model):
    title = models.CharField(verbose_name="العنوان", max_length=200)
    body = models.TextField(verbose_name="المحتوى")
    image = models.ImageField(verbose_name="الصورة", upload_to="dashboard/articles/")
    tags = models.CharField(
        verbose_name="الوسوم",
        max_length=255,
        blank=True,
        help_text="افصل بين الوسوم بفاصلة، مثال: مكسرات، عروض، وصفات",
    )
    created_at = models.DateTimeField(verbose_name="تاريخ الإنشاء", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "مقال"
        verbose_name_plural = "المقالات"

    @property
    def tag_list(self):
        # "مكسرات، عروض" / "nuts, offers" -> ["مكسرات", "عروض"] - splits on
        # either Arabic or Latin comma and drops empties from stray commas.
        return [tag.strip() for tag in self.tags.replace("،", ",").split(",") if tag.strip()]

    def __str__(self):
        return self.title


class AboutUsSection(models.Model):
    title = models.CharField(verbose_name="العنوان", max_length=150)
    body = models.TextField(verbose_name="المحتوى")
    order = models.PositiveIntegerField(verbose_name="الترتيب", default=0)

    class Meta:
        ordering = ["order"]
        verbose_name = "قسم صفحة من نحن"
        verbose_name_plural = "أقسام صفحة من نحن"

    def __str__(self):
        return self.title
