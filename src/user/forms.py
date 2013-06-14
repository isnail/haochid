__author__ = 'biyanbing'

from django import forms

import cn_key
from models import User
from utils import check_email


class UserRegisterForm(forms.Form):
    email = forms.CharField(label=cn_key._email, required=False, max_length=75)
    password = forms.CharField(label=cn_key._password,
                               widget=forms.PasswordInput, required=False)
    password_repeat = forms.CharField(label=cn_key._password_repeat,
                                      widget=forms.PasswordInput, required=False)

    def clean_password_repeat(self):
        password = self.cleaned_data.get('password')
        password_repeat = self.cleaned_data.get('password_repeat')
        if password and password_repeat and password.strip() != password_repeat.strip():
            raise forms.ValidationError(cn_key._password_not_match)
        return password_repeat.strip()

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if password:
            if len(password) < 6:
                raise forms.ValidationError(cn_key._password_length_limit)
            return password
        else:
            raise forms.ValidationError(cn_key._password_required)

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            email = email.strip()
            if not check_email(email):
                raise forms.ValidationError(cn_key._email_error)
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
        else:
            raise forms.ValidationError(cn_key._email_required)
        return email

