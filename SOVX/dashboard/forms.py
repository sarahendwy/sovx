from typing import Any
from django import forms
from django.core.validators import validate_image_file_extension
from django.forms import inlineformset_factory

from products.models import Product, ProductBuyingOption, NutritionalValue
from .models import Setting, ProductList, Section, SellWithUsCard, Governorate, City, ShippingFee


class GovernorateCityFormMixin:
    """For forms with a `governorate` ForeignKey and a dependent `city`
    ForeignKey: restricts governorate to the real Governorate list, and
    scopes city's queryset to that governorate's cities so an invalid
    combination can't validate even with JS disabled.

    static/js/locations.js redoes this scoping client-side (see the
    `data-governorate-select` / `data-city-select` attrs set below) so
    picking a governorate repopulates the city choices without a reload.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        governorate_field = self.fields.get("governorate")
        city_field = self.fields.get("city")
        if governorate_field is None or city_field is None:
            return

        governorate_field.queryset = Governorate.objects.all()
        governorate_field.widget.attrs["data-governorate-select"] = ""
        city_field.widget.attrs["data-city-select"] = ""

        if self.is_bound:
            governorate_id = self.data.get(self.add_prefix("governorate"))
        else:
            governorate_id = getattr(self.instance, "governorate_id", None)

        city_field.queryset = (
            City.objects.filter(governorate_id=governorate_id) if governorate_id else City.objects.none()
        )

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

class FormControlMixin(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field, forms.fields.BooleanField):
                field.widget.attrs.update({'class': 'form-check-input'})
            else:
                field.widget.attrs.update({'class': 'form-control'})


class ProductForm(FormControlMixin):
    class Meta:
        model = Product
        fields = '__all__'

class ProductBuyingOptionForm(FormControlMixin):
    class Meta:
        model = ProductBuyingOption
        fields = ('name', 'amount', 'unit', 'price', 'stock', 'is_default')

class ProductNutritionsValueForm(FormControlMixin):
    class Meta:
        model = NutritionalValue
        fields = ('name', 'description')

# Every product must have at least one buying option, so the dashboard form requires
# at least one non-deleted, filled-in option (Django ignores untouched extra forms
# when checking min_num, so a lone blank row won't satisfy this).
ProductBuyingOptionFormSet = inlineformset_factory(
    Product,
    ProductBuyingOption,
    form=ProductBuyingOptionForm,
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

ProductNutritionsValueFormSet = inlineformset_factory(
    Product,
    NutritionalValue,
    form=ProductNutritionsValueForm,
    extra=0,
    can_delete=True,
    min_num=1,
    validate_min=True,
)

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

class ShippingFeeForm(GovernorateCityFormMixin, forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['city'].required = False
        self.fields['city'].empty_label = "All cities (governorate-wide fee)"
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = ShippingFee
        fields = '__all__'