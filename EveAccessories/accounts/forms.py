import re
from typing import Any
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserChangeForm, UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from django.forms.widgets import NumberInput

from django import forms
from .models import User


class CreateUserForm(UserCreationForm):
    usable_password = None

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fields['first_name'].required = True
        self.fields['last_name'].required = True
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'phone', 'governorate',
                  'city', 'address']

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        re.compile('^01[0125]{1}[0-9]{8}$')
        if re.fullmatch('^01[0125]{1}[0-9]{8}$', phone):
            return phone
        else:
            self._update_errors(ValidationError({"phone": "Phone must match Egyptian format"}))

    def clean_email(self):
        email = self.cleaned_data.get("email")
        if self._meta.model.objects.filter(email__iexact=email).exists():
            self._update_errors(ValidationError({"email": "A user with this email already exists"}))
        else:
            return email


class LoginForm(AuthenticationForm):
    class Meta:
        fields = ['email', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

    def clean(self):
        email = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if email is not None and password:
            self.user_cache = authenticate(self.request, email=email, password=password)
            if self.user_cache is None:
                try:
                    user_temp = User.objects.get(email=email)
                except:
                    raise self.get_invalid_login_error()
                if not user_temp.is_active:
                    raise forms.ValidationError("verify-" + email)
            else:
                self.confirm_login_allowed(self.user_cache)

            return self.cleaned_data


class FullUserForm(UserChangeForm):
    password = None
    email = forms.EmailField(disabled=True, required=False)
    birthdate = forms.DateTimeField(widget=NumberInput(attrs={'type': 'date'}), required=False)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'phone', 'birthdate', 'governorate', 'city',
                  'address']

    def clean_email(self):
        return self.instance.email

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        re.compile('^01[0125]{1}[0-9]{8}$')
        if phone and not re.fullmatch('^01[0125]{1}[0-9]{8}$', phone):
            self._update_errors(ValidationError({"phone": "Phone must match Egyptian format"}))

        return phone
