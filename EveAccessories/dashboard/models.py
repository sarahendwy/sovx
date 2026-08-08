from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from accessories.models import Product

class Setting(models.Model):
    offer_banner_text = models.CharField(
        help_text="The offer text at the top of the landing page",
        default="",
        max_length=250,
    )
    facebook_link = models.CharField(default="",max_length=50, blank=True)
    instgram_link = models.CharField(default="",max_length=50, blank=True)

    default_shipping_fees = models.PositiveIntegerField(
        default=0,
        help_text="Fallback shipping fee shown before a city is known (e.g. in the cart panel), used until ShippingFee resolves a real governorate/city rate.",
    )


class Governorate(models.Model):
    name_ar = models.CharField(max_length=100)
    name_en = models.CharField(max_length=100)

    class Meta:
        ordering = ["name_en"]

    def __str__(self):
        return self.name_ar


class City(models.Model):
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name="cities")
    name_ar = models.CharField(max_length=200)
    name_en = models.CharField(max_length=200)

    class Meta:
        ordering = ["name_en"]
        verbose_name_plural = "Cities"

    def __str__(self):
        return f"{self.name_ar} ({self.governorate.name_ar})"


class ShippingFee(models.Model):
    governorate = models.ForeignKey(Governorate, on_delete=models.CASCADE, related_name="shipping_fees")
    city = models.ForeignKey(
        City,
        on_delete=models.CASCADE,
        related_name="shipping_fees",
        null=True,
        blank=True,
        help_text="Leave empty to use this fee for every city in the governorate that doesn't have its own fee.",
    )
    cost = models.PositiveIntegerField(default=0)

    class Meta:
        # Blocks two rows for the same (governorate, city) pair. It doesn't
        # cover two governorate-wide rows (city=NULL) for the same
        # governorate - NULL is never "equal" to NULL in a unique index -
        # so that case is enforced in clean() below instead.
        unique_together = [("governorate", "city")]
        ordering = ["governorate__name_en", "city__name_en"]

    def clean(self):
        super().clean()

        if self.city_id and self.governorate_id and self.city.governorate_id != self.governorate_id:
            raise ValidationError({"city": "This city does not belong to the selected governorate."})

        duplicates = ShippingFee.objects.filter(governorate_id=self.governorate_id, city_id=self.city_id)
        if self.pk:
            duplicates = duplicates.exclude(pk=self.pk)
        if duplicates.exists():
            scope = str(self.city) if self.city_id else "all cities (governorate-wide)"
            raise ValidationError(f"A shipping fee for {scope} in {self.governorate} already exists.")

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
    RATING = "rating", "Rating"
    CREATED_AT = "created_at", "Date Added"


class SortDirection(models.TextChoices):
    ASC = "asc", "Ascending"
    DESC = "desc", "Descending"


class ProductList(models.Model):
    name = models.CharField(max_length=150)
    limit = models.PositiveIntegerField(
        validators=[MinValueValidator(4), MaxValueValidator(16)],
        help_text="Number of products to display (4-16)",
    )
    product_ids = models.ManyToManyField(Product, blank=True, help_text="Leave empty to include all products")
    sort_by = models.CharField(max_length=20, choices=ProductSortField.choices, default=ProductSortField.CREATED_AT)
    sort_direction = models.CharField(max_length=4, choices=SortDirection.choices, default=SortDirection.DESC)

    def get_products(self):
        queryset = self.product_ids.all() if self.product_ids.exists() else Product.objects.all()
        order_field = self.sort_by if self.sort_direction == SortDirection.ASC else f"-{self.sort_by}"
        return queryset.order_by(order_field)[: self.limit]

    def __str__(self):
        return self.name


class SectionType(models.TextChoices):
    PRODUCT_LIST = "product_list", "Product List"
    REVIEWS = "reviews", "Reviews"
    WHY_CHOOSE_US = "why_choose_us", "Why Choose Us"
    SELL_WITH_US = "sell_with_us", "Sell With Us"


class Section(models.Model):
    name = models.CharField(max_length=150)
    type = models.CharField(max_length=20, choices=SectionType.choices)
    order = models.PositiveIntegerField(default=0)
    banner = models.ImageField(upload_to="dashboard/sections/", blank=True)
    product_list = models.ForeignKey(
        ProductList, on_delete=models.SET_NULL, null=True, blank=True, related_name="sections"
    )

    class Meta:
        ordering = ["order"]

    def clean(self):
        super().clean()
        if self.type == SectionType.PRODUCT_LIST and not self.banner:
            raise ValidationError({"banner": "Banner is required for Product List sections."})

    def __str__(self):
        return self.name


class SellWithUsIcon(models.TextChoices):
    GLOBE = "globe", "Globe"
    REVENUE_GROWTH = "revenue_growth", "Revenue Growth"
    COINS_HAND = "coins_hand", "Coins In Hand"
    PAYMENT_PLAN = "payment_plan", "Payment Plan"
    NUTS_BAG = "nuts_bag", "Nuts Bag"


SELL_WITH_US_ICON_FILES = {
    SellWithUsIcon.GLOBE: "globe.svg",
    SellWithUsIcon.REVENUE_GROWTH: "revenue-growth.svg",
    SellWithUsIcon.COINS_HAND: "coins-hand.svg",
    SellWithUsIcon.PAYMENT_PLAN: "payment-plan.png",
    SellWithUsIcon.NUTS_BAG: "nuts-bag.png",
}


class SellWithUsColor(models.TextChoices):
    YELLOW = "#fffcdd", "Yellow"
    GREEN = "#e7ffdc", "Green"
    PINK = "#ffecee", "Pink"


class SellWithUsCardSpan(models.IntegerChoices):
    SINGLE = 1, "1 Column"
    DOUBLE = 2, "2 Columns"


class SellWithUsCard(models.Model):
    title = models.CharField(max_length=150)
    svg = models.CharField(max_length=20, choices=SellWithUsIcon.choices)
    bg_color = models.CharField(max_length=7, choices=SellWithUsColor.choices, default=SellWithUsColor.YELLOW)
    description = models.TextField(blank=True, help_text="Optional supporting text shown below the title")
    cta_text = models.CharField(max_length=50, blank=True, help_text="Optional call-to-action button label")
    disabled = models.BooleanField(default=False, help_text="Hide this card from the landing page")
    span = models.PositiveSmallIntegerField(choices=SellWithUsCardSpan.choices, default=SellWithUsCardSpan.SINGLE)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    @property
    def icon_path(self):
        return f"images/sections/sell-with-us/{SELL_WITH_US_ICON_FILES[self.svg]}"

    def __str__(self):
        return self.title
