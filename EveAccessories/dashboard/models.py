from django.db import models
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator

from accessories.models import Product

egypt_governorates = [
    ("Cairo", "Cairo"),
    ("Alexandria", "Alexandria"),
    ("Giza", "Giza"),
    ("Qalyubia", "Qalyubia"),
    ("Port Said", "Port Said"),
    ("Suez", "Suez"),
    ("Dakahlia", "Dakahlia"),
    ("Sharkia", "Sharkia"),
    ("Monufia", "Monufia"),
    ("Gharbia", "Gharbia"),
    ("Kafr El Sheikh", "Kafr El Sheikh"),
    ("Beheira", "Beheira"),
    ("Ismailia", "Ismailia"),
    ("Beni Suef", "Beni Suef"),
    ("Fayoum", "Fayoum"),
    ("Minya", "Minya"),
    ("Assiut", "Assiut"),
    ("Sohag", "Sohag"),
    ("Qena", "Qena"),
    ("Luxor", "Luxor"),
    ("Aswan", "Aswan"),
    ("Red Sea", "Red Sea"),
    ("New Valley", "New Valley"),
    ("Matruh", "Matruh"),
    ("North Sinai", "North Sinai"),
    ("South Sinai", "South Sinai"),
]


class Setting(models.Model):
    offer_banner_text = models.CharField(
        help_text="The offer text at the top of the landing page",
        default="",
        max_length=250,
    )
    payment_image = models.ImageField(upload_to="dashboard/settings/", blank=True)
    hero_image = models.ImageField(upload_to="dashboard/settings/", blank=True)

    cairo_shipping = models.PositiveIntegerField(default=0)
    alexandria_shipping = models.PositiveIntegerField(default=0)
    giza_shipping = models.PositiveIntegerField(default=0)
    qalyubia_shipping = models.PositiveIntegerField(default=0)
    port_said_shipping = models.PositiveIntegerField(default=0)
    suez_shipping = models.PositiveIntegerField(default=0)
    dakahlia_shipping = models.PositiveIntegerField(default=0)
    sharkia_shipping = models.PositiveIntegerField(default=0)
    monufia_shipping = models.PositiveIntegerField(default=0)
    gharbia_shipping = models.PositiveIntegerField(default=0)
    kafr_sheikh_shipping = models.PositiveIntegerField(default=0)
    beheira_shipping = models.PositiveIntegerField(default=0)
    ismailia_shipping = models.PositiveIntegerField(default=0)
    benisuef_shipping = models.PositiveIntegerField(default=0)
    fayoum_shipping = models.PositiveIntegerField(default=0)
    minya_shipping = models.PositiveIntegerField(default=0)
    assiut_shipping = models.PositiveIntegerField(default=0)
    sohag_shipping = models.PositiveIntegerField(default=0)
    qena_shipping = models.PositiveIntegerField(default=0)
    luxor_shipping = models.PositiveIntegerField(default=0)
    aswan_shipping = models.PositiveIntegerField(default=0)
    red_sea_shipping = models.PositiveIntegerField(default=0)
    new_valley_shipping = models.PositiveIntegerField(default=0)
    matruh_shipping = models.PositiveIntegerField(default=0)
    north_sinai_shipping = models.PositiveIntegerField(default=0)
    south_sinai_shipping = models.PositiveIntegerField(default=0)


class ProductSortField(models.TextChoices):
    PRICE = "price", "Price"
    STOCK = "stock", "Stock"
    DISCOUNT = "discount", "Discount"
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
