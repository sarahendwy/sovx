import json
from typing import Any
from .models import Order, SellWithUsRequest, ContactUsRequest
from django import forms

from dashboard.forms import GovernorateCityFormMixin


class FormControlMixin:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            is_select = isinstance(field.widget, forms.Select)
            field.widget.attrs.update({
                "class": "form-select" if is_select else "form-control",
                "dir": "rtl",
                "placeholder": field.help_text
            })

class OrderForm(GovernorateCityFormMixin, FormControlMixin, forms.ModelForm):
    class Meta:
        model = Order
        exclude = [
            "user", "status", "order_total", "created_at", "updated_at",
            "products", "quanitites", "payment_account", "payment_method",
            "payment_proof", "delivered_at",
        ]

    def clean_quanitites(self):
        quanitites = self.cleaned_data.get('quanitites')
        if not quanitites:
            raise forms.ValidationError("Please add products to your cart")
        return quanitites

FIELDS_ICONS = {
    "name": "images/icons/user.svg",
    "store_name": "images/icons/store.svg",
    "phone": "images/icons/phone.svg",
    "governorate": "images/icons/location.svg",
    "city": "images/icons/location.svg",
    "address": "images/icons/navigator.svg",
    "email": "images/icons/email.svg",
    "building_number": "images/icons/building.svg",
    "appartment_number": "images/icons/appartment.svg",
}

class SellWithUsForm(GovernorateCityFormMixin, FormControlMixin, forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field_icon = FIELDS_ICONS.get(field_name)
            if field_icon:
                field.widget.icon = field_icon

    class Meta:
        model = SellWithUsRequest
        exclude = ["created_at"]

class ContactUsForm(SellWithUsForm):
    class Meta:
        model = ContactUsRequest
        exclude = ["created_at"]

    
class OrderForm(SellWithUsForm):
    # Not a model field - holds a JSON snapshot of the client-side cart
    # (window.Cart.getItems(), see static/js/cart.js), kept in sync by the
    # inline script in orders/create.html and read in CreateOrder.form_valid
    # to build the order's OrderEntry rows.
    user_cart = forms.CharField(widget=forms.HiddenInput(), required=True)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Marks these two selects (only, not SellWithUsForm's/ContactUsForm's
        # own governorate+city) as the ones whose changes should refresh the
        # cart panel's shipping-fee estimate - see locations.js's
        # updateShippingFeeDisplay().
        for field_name in ("governorate", "city"):
            field = self.fields.get(field_name)
            if field:
                field.widget.attrs["data-updates-cart-shipping"] = ""

    def clean_user_cart(self):
        raw = self.cleaned_data.get("user_cart", "")
        try:
            items = json.loads(raw)
        except (TypeError, ValueError):
            raise forms.ValidationError("سلة المشتريات غير صالحة.")
        if not isinstance(items, list) or not items:
            raise forms.ValidationError("سلتك فارغة. من فضلك أضف منتجات قبل إرسال الطلب.")
        return items

    class Meta:
        model = Order
        exclude = ["created_at", "updated_at", "status", "delivered_at", "order_total"]
