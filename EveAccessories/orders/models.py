from django.db import models
from accounts.models import egypt_governorates

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
    governorate = models.CharField(choices=egypt_governorates, max_length=25)
    city = models.CharField(max_length=55)
    address = models.CharField(max_length=500)
    status = models.CharField(choices=orders_states, max_length=25, default="Pending Confirmation")

    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="orders", null=True)
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