from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to="categories/images/%Y/%m/%d/")
    display_order = models.PositiveIntegerField(default=0, help_text="Lower numbers appear first on homepage")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['display_order', 'name']


class Product(models.Model):
    title = models.CharField(max_length=150)
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    description = models.TextField()
    price = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])
    discount = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    rating = models.PositiveIntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(5)])
    variants = models.PositiveIntegerField(default=1, validators=[MinValueValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def discounted_price(self):
        return self.price - self.price * self.discount / 100

    @property
    def empty_stars(self):
        return 5 - self.rating

    @property
    def thumbnail(self):
        first_image = self.images.first()
        return first_image.url if first_image else ""

    def __str__(self):
        return self.title


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/images/%Y/%m/%d/", blank=True, null=True)
    image_url = models.URLField(max_length=500, blank=True, null=True)

    @property
    def url(self):
        if self.image_url:
            return self.image_url
        if self.image:
            return self.image.url
        return ""
