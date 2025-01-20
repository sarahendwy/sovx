from django.db import models
from accounts.models import egypt_governorates

orders_states = [
    ('Pending Confirmation', 'Pending Confirmation'),
    ('Confirmed', 'Confirmed'),
    ('Cancelled', 'Cancelled'),
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
    status = models.CharField(choices=orders_states, max_length=25, default="Pending Confirmation")

    user = models.ForeignKey("accounts.User", on_delete=models.PROTECT, related_name="orders")
    delivered_at = models.DateTimeField(null=True, blank=True)

    instapay_account = models.CharField(max_length=255)
    instapay_image = models.ImageField(upload_to="orders/images/%Y/%m/%d/%h/%M/%S/")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def shipping_fees(self):
        if self.governorate == "Cairo":
            return 30
        else:
            return 50

    @property
    def order_total(self):
        return self.shipping_fees + sum([entry.price for entry in self.entries.all()])

    def __str__(self):
        return f"Order id: {self.id} - {self.name}"

class OrderEntry(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="entries")
    product = models.ForeignKey("accessories.Product", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order} - {self.product.title} - {self.quantity}"

class OrderLog(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="logs")
    content = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.order} - {self.content}"