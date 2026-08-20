from django.db import models

from dashboard.models import City, Governorate, ShippingFee

orders_states = [
    ('Pending Confirmation', 'قيد التأكيد'),
    ('Confirmed', 'تم التأكيد'),
    ('Cancelled', 'ملغي'),
    ('In Delivery', 'قيد التوصيل'),
    ('Delivered', 'تم التوصيل'),
]

payment_methods = [
    ('Cash on Delivery', 'الدفع عند الاستلام'),
    ('Wallet', 'محفظة إلكترونية'),
]

class Order(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    # null=True keeps this column migration-safe for any pre-existing rows;
    # forms still require a selection since blank=False (the Django default).
    governorate = models.ForeignKey(Governorate, on_delete=models.PROTECT, null=True, related_name="orders")
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, related_name="orders")
    address = models.CharField(max_length=500)
    status = models.CharField(choices=orders_states, max_length=25, default="Pending Confirmation")

    delivered_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(choices=payment_methods, max_length=25, default="Cash on Delivery")
    payment_account = models.CharField(max_length=255, null=True, blank=True)
    payment_proof = models.ImageField(upload_to="orders/images/%Y/%m/%d/%h/%M/%S/", null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    order_total = models.PositiveIntegerField(default=0)

    @property
    def shipping_fees(self):
        return ShippingFee.get_fee(self.governorate_id, self.city_id) or 0

    def __str__(self):
        return f"Order id: {self.id} - {self.name}"

class OrderEntry(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="entries")
    product = models.ForeignKey("products.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    variant = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.order} - {self.product.title} - {self.quantity}"

class OrderLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="logs")
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order} - {self.content}"

class SellWithUsRequest(models.Model):
    name = models.CharField(max_length=255, verbose_name="الاسم", help_text="اكتب اسمك")
    store_name = models.CharField(max_length=255, verbose_name="اسم المحل", help_text="اكتب اسم المحل")
    phone = models.CharField(max_length=20, verbose_name="رقم التليفون", help_text="000-000-000-00")
    # null=True keeps this column migration-safe for any pre-existing rows;
    # forms still require a selection since blank=False (the Django default).
    governorate = models.ForeignKey(
        Governorate, on_delete=models.PROTECT, null=True, related_name="sell_with_us_requests",
        verbose_name="المحافظة", help_text="اختر المحافظة",
    )
    city = models.ForeignKey(
        City, on_delete=models.PROTECT, null=True, related_name="sell_with_us_requests",
        verbose_name="المدينة", help_text="اختر المدينة",
    )
    address = models.CharField(max_length=500, verbose_name="العنوان بالتفصيل", help_text="اكتب العنوان بالتفصيل")
    message = models.TextField(blank=True, verbose_name="رسالتك", help_text="نحن هنا لنستمع إليكم")


    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sell With Us Request id: {self.id} - {self.name}"

class ContactUsRequest(models.Model):
    name = models.CharField(max_length=255, verbose_name="الاسم", help_text="اكتب اسمك")
    email = models.CharField(max_length=255, verbose_name="البريد الإلكتروني  (اختياري)", help_text="hello@kkesh.sa.com")
    phone = models.CharField(max_length=20, verbose_name="رقم التليفون", help_text="000-000-000-00")
    # null=True keeps this column migration-safe for any pre-existing rows;
    # forms still require a selection since blank=False (the Django default).
    message = models.TextField(blank=True, verbose_name="رسالتك", help_text="نحن هنا لنستمع إليكم")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact Us Request id: {self.id} - {self.name}"