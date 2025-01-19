from django.db import models
from accounts.models import egypt_governorates

orders_states = [
    ('Not Paid', 'Not Paid'),
    ('Pending Confirmation', 'Pending Confirmation'),
    ('Confirmed', 'Confirmed'),
    ('Rejected', 'Rejected'),
    ('In Delivery', 'In Delivery'),
    ('Delivered', 'Delivered')
]

class Order(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    governorate = models.CharField(choices=egypt_governorates, max_length=25)
    city = models.CharField(max_length=55)
    address = models.CharField(max_length=500)
    status = models.CharField(choices=orders_states, max_length=25, default="Not Paid")

    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="orders")
    order_total = models.DecimalField(max_digits=10, decimal_places=2)

    instapay_account = models.CharField(max_length=255, default="", blank=True)
    instapay_image = models.ImageField(upload_to="orders/images/%Y/%m/%d/%h/%M/%S/")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class OrderEntry(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="entries")
    product = models.ForeignKey("accessories.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order.name} - {self.product.name} - {self.quantity}"

class OrderLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="logs")
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order.name} - {self.content}"