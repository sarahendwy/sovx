from typing import Any
from .models import Order, SellWithUsRequest
from django import forms


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

class OrderForm(FormControlMixin, forms.ModelForm):
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

SELL_WITH_US_FIELDS_ICONS = {
    "name": "images/icons/user.svg",
    "store_name": "images/icons/store.svg",
    "phone": "images/icons/phone.svg",
    "governorate": "images/icons/location.svg",
    "city": "images/icons/location.svg",
    "address": "images/icons/navigator.svg",
}

class SellWithUsForm(FormControlMixin, forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field_name, field in self.fields.items():
            field_icon = SELL_WITH_US_FIELDS_ICONS.get(field_name)
            print(f"x Field: {field_name} - Icon: {field_icon}")
            if field_icon:
                field.widget.icon = field_icon

    class Meta:
        model = SellWithUsRequest
        exclude = ["created_at"]

    