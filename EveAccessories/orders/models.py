from django.db import models

orders_states = [
    ('Pending Confirmation', 'Pending Confirmation'),
    ('Confirmed', 'Confirmed'),
    ('Cancelled', 'Cancelled'),
    ('In Delivery', 'In Delivery'),
    ('Delivered', 'Delivered')
]

payment_methods = [
    ('Cash on Delivery', 'Cash on Delivery'),
    ('Wallet', 'Wallet'),
]

class Order(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    governorate = models.CharField(choices=[("Cairo", "Cairo")], max_length=25)
    city = models.CharField(max_length=55)
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
        if self.governorate == "Cairo":
            return 70
        else:
            return 70

    def __str__(self):
        return f"Order id: {self.id} - {self.name}"

class OrderEntry(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="entries")
    product = models.ForeignKey("accessories.Product", on_delete=models.CASCADE)
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
    governorate = models.CharField(choices=[("Cairo", "Cairo")], max_length=25, verbose_name="المحافظة", help_text="اختر المحافظة")
    city = models.CharField(max_length=55, verbose_name="المدينة", help_text="اكتب المدينة")
    address = models.CharField(max_length=500, verbose_name="العنوان بالتفصيل", help_text="اكتب العنوان بالتفصيل")
    message = models.TextField(blank=True, verbose_name="رسالتك", help_text="نحن هنا لنسمع رأيكم")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sell With Us Request id: {self.id} - {self.name}"