from typing import Any
from django import forms
from django.core.validators import validate_image_file_extension

from accessories.models import Category, Product

class CategoryForm(forms.ModelForm):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Category
        fields = '__all__'

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
        


    images = MultipleFileField(widget=MultipleFileInput(attrs={'multiple': True, 'accept': "image/*"}),required=False)
    clear_old_images = forms.BooleanField(required=False, label="Clear old images?", help_text="Check this box to clear all old images")

    class Meta:
        model = Product
        fields = '__all__'

