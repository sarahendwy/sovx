from typing import Any
from .models import Order
from django import forms

class OrderForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Order
        exclude = ['user', 'status', 'order_total', 'created_at', 'updated_at', 'products', 'quanitites', 'payment_account', 'payment_method', 'payment_proof', 'delivered_at']
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
            "name": forms.TextInput(
                attrs={
                    "class": "form-control order-form-control",
                    "placeholder": "اكتب اسمك",
                    "dir": "rtl",
                }
            ),
            "store_name": forms.TextInput(
                attrs={
                    "class": "form-control order-form-control",
                    "placeholder": "اكتب اسم المحل",
                    "dir": "rtl",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "class": "form-control order-form-control",
                    "placeholder": "اكتب البريد الإلكتروني",
                    "dir": "rtl",
                }
            ),
            "phone": forms.TextInput(
                attrs={
                    "class": "form-control order-form-control",
                    "placeholder": "000-000-000-00",
                    "dir": "ltr",
                }
            ),
            "governorate": forms.Select(
                attrs={
                    "class": "form-select order-form-control",
                    "dir": "rtl",
                }
            ),
            "city": forms.Select(
                attrs={
                    "class": "form-select order-form-control",
                    "dir": "rtl",
                }
            ),
            "address": forms.TextInput(
                attrs={
                    "class": "form-control order-form-control",
                    "placeholder": "اكتب العنوان بالتفصيل",
                    "dir": "rtl",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "class": "form-control order-form-control",
                    "placeholder": "نحن هنا لنسمع رأيكم",
                    "rows": 4,
                    "dir": "rtl",
                }
            ),
        }


    def clean_quanitites(self):
        quanitites = self.cleaned_data.get('quanitites')
        if not quanitites:
            raise forms.ValidationError("Please add products to your cart")
        
        return quanitites