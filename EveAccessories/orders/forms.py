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
        exclude = ['user', 'status', 'order_total', 'created_at', 'updated_at', 'products', 'quanitites', 'instapay_account', 'instapay_image', 'delivered_at']

    def clean_quanitites(self):
        quanitites = self.cleaned_data.get('quanitites')
        if not quanitites:
            raise forms.ValidationError("Please add products to your cart")
        
        return quanitites