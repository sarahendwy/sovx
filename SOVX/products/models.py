from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Product(models.Model):
    title = models.CharField(verbose_name="الاسم", max_length=150)
    description = models.TextField(verbose_name="الوصف")
    rating = models.PositiveIntegerField(
        verbose_name="التقييم", default=5, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    image = models.ImageField(verbose_name="الصورة", upload_to="products/images/%Y/%m/%d/", blank=True, null=True)

    class Meta:
        verbose_name = "المنتج"
        verbose_name_plural = "المنتجات"

    @property
    def default_buying_option(self):
        return self.buying_options.filter(is_default=True).first() or self.buying_options.first()

    @property
    def price(self):
        default_option = self.default_buying_option
        return default_option.price if default_option else 0

    @property
    def thumbnail(self):
        return self.image.url if self.image else ""

    @property
    def empty_stars(self):
        return 5 - self.rating

    def __str__(self):
        return self.title


class ProductBuyingOption(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="buying_options")
    name = models.CharField(verbose_name="الاسم", max_length=100)
    amount = models.PositiveIntegerField(verbose_name="الكمية", default=1, validators=[MinValueValidator(1)])
    unit = models.CharField(
        verbose_name="الوحدة",
        max_length=50,
        default="piece",
        choices=[("piece", "قطعة"), ("kg", "كيلوجرام"), ("g", "جرام"), ("liter", "لتر")],
    )
    price = models.PositiveIntegerField(verbose_name="السعر", default=0)
    stock = models.PositiveIntegerField(verbose_name="المخزون", default=1, validators=[MinValueValidator(0)])
    is_default = models.BooleanField(verbose_name="الخيار الافتراضي", default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "خيار شراء"
        verbose_name_plural = "خيارات الشراء"

    @property
    def unit_label(self):
        """Arabic display label for `unit` (e.g. "piece" -> "قطعة")."""
        return self.get_unit_display()

    def __str__(self):
        return f"{self.product.title} - {self.name}"

class NutritionalValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="nutritional_values")
    name = models.CharField(verbose_name="الاسم", max_length=50, help_text="الطاقة:")
    description = models.CharField(verbose_name="القيمة", max_length=100, help_text="2502 كيلوجول / 597 سعر حراري")

    class Meta:
        verbose_name = "قيمة غذائية"
        verbose_name_plural = "القيم الغذائية"
