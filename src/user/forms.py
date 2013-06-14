__author__ = 'biyanbing'

from django import forms
from django.utils.translation import ugettext, ugettext_lazy as _
from django.contrib.auth.forms import ReadOnlyPasswordHashField

import cn_key
from models import User
from utils import check_email


class UserAccountForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('nick_name', 'gender', 'avatar', 'location', 'email', )
        widgets = {
            'gender': forms.RadioSelect(),
            'avatar': forms.FileInput()
        }

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


class UserCreationForm(forms.ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and
    password.
    """
    error_messages = {
        'duplicate_username': "A user with that username already exists.",
        'password_mismatch': "The two password fields didn't match.",
    }
    uid = forms.RegexField(label=_("uid"), max_length=30,
        regex=r'^[\w.@+-]+$',
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password1 = forms.CharField(label=_("Password"),
        widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password confirmation"),
        widget=forms.PasswordInput,
        help_text=_("Enter the same password as above, for verification."))

    class Meta:
        model = User
        fields = ("uid",)

    def clean_username(self):
        # Since User.username is unique, this check is redundant,
        # but it sets a nicer error message than the ORM. See #13147.
        uid = self.cleaned_data["uid"]
        try:
            User._default_manager.get(uid=uid)
        except User.DoesNotExist:
            return uid
        raise forms.ValidationError(self.error_messages['duplicate_username'])

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")
        if password1 and password2 and password1 != password2:
            raise forms.ValidationError(
                self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user


class UserChangeForm(forms.ModelForm):
    uid = forms.RegexField(
        label=_("uid"), max_length=30, regex=r"^[\w.@+-]+$",
        help_text=_("Required. 30 characters or fewer. Letters, digits and "
                      "@/./+/-/_ only."),
        error_messages={
            'invalid': _("This value may contain only letters, numbers and "
                         "@/./+/-/_ characters.")})
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = User

    def __init__(self, *args, **kwargs):
        super(UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]

class AdminPasswordChangeForm(forms.Form):
    """
    A form used to change the password of a user in the admin interface.
    """
    error_messages = {
        'password_mismatch': _("The two password fields didn't match."),
    }
    password1 = forms.CharField(label=_("Password"),
                                widget=forms.PasswordInput)
    password2 = forms.CharField(label=_("Password (again)"),
                                widget=forms.PasswordInput)

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(AdminPasswordChangeForm, self).__init__(*args, **kwargs)

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')
        password2 = self.cleaned_data.get('password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'])
        return password2

    def save(self, commit=True):
        """
        Saves the new password.
        """
        self.user.set_password(self.cleaned_data["password1"])
        if commit:
            self.user.save()
        return self.user
