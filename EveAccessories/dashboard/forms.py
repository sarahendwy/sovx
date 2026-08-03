from typing import Any
from django import forms
from django.core.validators import validate_image_file_extension

from accessories.models import Product
from .models import Setting, ProductList, Section, SellWithUsCard

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True
    
class MultipleFileField(forms.FileField):
    default_validators = [validate_image_file_extension]
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = single_file_clean(data, initial)
        return result

class ProductForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.fields.BooleanField):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        if self.instance.id and self.instance.images.exists():
            self.fields['clear_old_images'].widget = forms.CheckboxInput()
        else:
            del self.fields['clear_old_images']
        
    # images = MultipleFileField(
    #     widget=MultipleFileInput(attrs={'multiple': True, 'accept': "image/*"}),
    #     required=False,
    #     help_text="Upload one or more image files for this product.",
    # )
    clear_old_images = forms.BooleanField(
        required=False,
        label="Clear old images?",
        help_text="Check this box to clear all old images before saving new ones.",
    )

    class Meta:
        model = Product
        fields = '__all__'

class SettingsForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Setting
        fields = '__all__'

class ProductListForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.fields.BooleanField):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

        if self.instance.pk and not self.instance.product_ids.exists():
            self.fields['select_all_products'].initial = True

        self.fields['limit'].widget.attrs.update({'min': 4, 'max': 16})
        self.order_fields(['name', 'limit', 'select_all_products', 'product_ids', 'sort_by', 'sort_direction'])

    select_all_products = forms.BooleanField(
        required=False,
        label="Select all products?",
        help_text="Check this box to include all products instead of picking specific ones below.",
    )

    class Meta:
        model = ProductList
        fields = '__all__'

class SectionForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Section
        fields = '__all__'

class SellWithUsCardForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.fields.BooleanField):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = SellWithUsCard
        fields = '__all__'