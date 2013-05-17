__author__ = 'biyanbing'

from django import forms

import cn_key
from models import User


class UserRegisterForm(forms.Form):
    email = forms.EmailField(label=cn_key._email, required=True)
    password = forms.CharField(label=cn_key._password, max_length=16, min_length=6, required=True,
                               widget=forms.PasswordInput)
    password_repeat = forms.CharField(label=cn_key._password_repeat, max_length=16, min_length=6, required=True,
                                      widget=forms.PasswordInput)

    def clean_password_repeat(self):
        password = self.cleaned_data.get('password')
        password_repeat = self.cleaned_data.get('password_repeat')
        if password and password_repeat and password.strip() != password_repeat.strip():
            raise forms.ValidationError(cn_key._password_not_match)
        return password_repeat.strip()

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            return password.strip()
        return password

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip()
            try:
                User.objects.get(uid=email)
                raise forms.ValidationError(cn_key._email_exists)
            except User.DoesNotExist:
                pass
            try:
                User.objects.get(email=email)
                raise forms.ValidationError(cn_key._email_exists)
            except User.DoesNotExist:
                pass
        return email

