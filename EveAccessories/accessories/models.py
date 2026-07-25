from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Product(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField()
    price = models.PositiveIntegerField(default=0)
    stock = models.PositiveIntegerField(default=1, validators=[MinValueValidator(0)])
    discount = models.PositiveIntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    rating = models.PositiveIntegerField(default=5, validators=[MinValueValidator(0), MaxValueValidator(5)])
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

    @property
    def url(self):
        return self.image.url if self.image else ""
