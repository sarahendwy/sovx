from typing import Any
from .models import Order
from django import forms


class OrderForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            is_select = isinstance(field.widget, forms.Select)
            field.widget.attrs.update({
                "class": "form-select" if is_select else "form-control",
                "dir": "rtl",
            })

    class Meta:
        model = Order
        exclude = [
            "user", "status", "order_total", "created_at", "updated_at",
            "products", "quanitites", "payment_account", "payment_method",
            "payment_proof", "delivered_at",
        ]
        labels = {
            "name": "الاسم",
            "store_name": "اسم المحل",
            "email": "البريد الإلكتروني",
            "phone": "رقم التليفون",
            "governorate": "المحافظة",
            "city": "المدينة",
            "address": "العنوان بالتفصيل",
            "message": "رسالتك",
        }
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "اكتب اسمك"}),
            "store_name": forms.TextInput(attrs={"placeholder": "اكتب اسم المحل"}),
            "email": forms.EmailInput(attrs={"placeholder": "اكتب البريد الإلكتروني"}),
            "phone": forms.TextInput(attrs={
                "placeholder": "000-000-000-00",
                "inputmode": "tel",
                "autocomplete": "tel",
            }),
            "governorate": forms.Select(),
            "city": forms.Select(),
            "address": forms.TextInput(attrs={"placeholder": "اكتب العنوان بالتفصيل"}),
            "message": forms.Textarea(attrs={
                "placeholder": "نحن هنا لنسمع رأيكم",
                "rows": 4,
            }),
        }

    def clean_quanitites(self):
        quanitites = self.cleaned_data.get('quanitites')
        if not quanitites:
            raise forms.ValidationError("Please add products to your cart")
        return quanitites