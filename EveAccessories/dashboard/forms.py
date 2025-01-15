from django import forms
from accessories.models import Category, Product
from typing import Any

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
    
class ProductForm(forms.ModelForm):
    images = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'allow_multiple_selected': True}))

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = Product
        fields = '__all__'
