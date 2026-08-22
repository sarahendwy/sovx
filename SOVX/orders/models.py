from django.db import models

from dashboard.models import City, Governorate, ShippingFee

orders_states = [
    ('Pending Confirmation', 'قيد التأكيد'),
    ('Preparing', 'قيد التجهيز'),
    ('Cancelled', 'ملغي'),
    ('Rejected', 'مرفوض'),
    ('Ready', 'جاهز'),
    ('In Delivery', 'قيد التوصيل'),
    ('Completed', 'مكتمل'),
    ('Returned', 'مرتجع'),
]

payment_methods = [
    ('COD', 'كاش عند الاستلام'),
    ('Pickup', 'الإستلام من الفرع')
]

# Short, URL-friendly slugs for ?status=<slug> filtering (see dashboard's
# OrdersView) - stored status values have spaces/mixed case, not fit for a
# query string.
ORDER_STATUS_SLUGS = {
    "pending": "Pending Confirmation",
    "preparing": "Preparing",
    "cancelled": "Cancelled",
    "rejected": "Rejected",
    "ready": "Ready",
    "delivery": "In Delivery",
    "completed": "Completed",
    "returned": "Returned",
}
ORDER_STATUS_VALUE_TO_SLUG = {value: slug for slug, value in ORDER_STATUS_SLUGS.items()}

# The order status workflow (see dashboard's change_order_status view):
#
#   Pending Confirmation -> Rejected, Cancelled, Preparing
#   Preparing            -> Cancelled, Rejected, Ready
#   Cancelled            -> Pending Confirmation
#   Rejected             -> Pending Confirmation
#   Ready                -> In Delivery (if COD) / Completed (if Pickup),
#                            Cancelled, Rejected, Returned
#   In Delivery          -> Completed, Cancelled, Returned, Rejected
#   Completed, Returned  -> (terminal, no further transitions)
ORDER_STATUS_TRANSITIONS = {
    "Pending Confirmation": ["Rejected", "Cancelled", "Preparing"],
    "Preparing": ["Cancelled", "Rejected", "Ready"],
    "Cancelled": ["Pending Confirmation"],
    "Rejected": ["Pending Confirmation"],
    "In Delivery": ["Completed", "Cancelled", "Returned", "Rejected"],
    "Completed": [],
    "Returned": [],
}

# Landing on one of these releases the order's reserved stock back to each
# line's ProductBuyingOption; leaving one of these (only possible by
# returning to "Pending Confirmation") re-reserves it. See
# dashboard.views.change_order_status.
ORDER_STOCK_RELEASING_STATUSES = {"Cancelled", "Rejected", "Returned"}

# Action-phrased button labels for status-change buttons (orders list +
# order details pages) - keyed by target status, since the action reads the
# same regardless of which status it's coming from. Falls back to the plain
# status label (orders_states) for anything not listed here.
ORDER_STATUS_ACTION_LABELS = {
    "Pending Confirmation": "إعادة تفعيل الطلب",
    "Preparing": "بدء التجهيز",
    "Ready": "الطلب جاهز",
    "In Delivery": "بدء التوصيل",
    "Completed": "تأكيد التسليم",
    "Cancelled": "إلغاء الطلب",
    "Rejected": "رفض الطلب",
    "Returned": "تسجيل كمرتجع",
}

class Order(models.Model):
    name = models.CharField(max_length=255, verbose_name="الإسم", help_text="اكتب اسمك")
    phone = models.CharField(max_length=20, verbose_name="رقم التليفون", help_text="000-000-000-00")

    governorate = models.ForeignKey(Governorate, on_delete=models.PROTECT, null=True, related_name="orders", verbose_name="المحافظة", help_text="اختار المحافظة")
    city = models.ForeignKey(City, on_delete=models.PROTECT, null=True, related_name="orders", verbose_name="المدينة", help_text="اختار المدينة")
    address = models.CharField(max_length=500, verbose_name="العنوان", help_text="اكتب العنوان بالتفصيل")
    building_number = models.CharField(max_length=50, null=True, help_text="اكتب رقم العمارة", verbose_name="رقم العمارة")
    appartment_number = models.CharField(max_length=50, null=True, help_text="اكتب رقم العمارة", verbose_name="رقم الشقة أو الدور")

    status = models.CharField(choices=orders_states, max_length=25, default="Pending Confirmation")
    delivered_at = models.DateTimeField(null=True, blank=True)
    payment_method = models.CharField(choices=payment_methods, max_length=25, default="COD")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    order_total = models.PositiveIntegerField(default=0)

    @property
    def shipping_fees(self):
        return ShippingFee.get_fee(self.governorate_id, self.city_id) or 0

    def get_available_status_transitions(self):
        """(value, action_label) pairs for the statuses this order can move
        to next from its current status - see ORDER_STATUS_TRANSITIONS
        above. "Ready" branches on payment_method: COD orders go out for
        delivery, Pickup orders are handed over directly. Labels are
        action-phrased ("بدء التجهيز") rather than the plain status name, for
        use directly as button text."""
        if self.status == "Ready":
            next_values = ["In Delivery" if self.payment_method == "COD" else "Completed"]
            next_values += ["Cancelled", "Rejected", "Returned"]
        else:
            next_values = ORDER_STATUS_TRANSITIONS.get(self.status, [])

        status_labels = dict(orders_states)
        return [(value, ORDER_STATUS_ACTION_LABELS.get(value, status_labels.get(value, value))) for value in next_values]

    def __str__(self):
        return f"Order id: {self.id} - {self.name} - {self.order_total}"

class OrderEntry(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="entries")
    product_option = models.ForeignKey("products.ProductBuyingOption", on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.order}: {self.quantity} x {self.product_option}"

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
    email = models.CharField(max_length=255, verbose_name="البريد الإلكتروني  (اختياري)", help_text="example@mail.com")
    phone = models.CharField(max_length=20, verbose_name="رقم التليفون", help_text="000-000-000-00")
    message = models.TextField(blank=True, verbose_name="رسالتك", help_text="نحن هنا لنستمع إليكم")

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Contact Us Request id: {self.id} - {self.name}"