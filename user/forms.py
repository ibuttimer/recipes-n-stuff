#  MIT License
#
#  Copyright (c) 2023 Ian Buttimer
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM,OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.
from dataclasses import dataclass
from typing import List, Union, Tuple, Optional

from allauth.account import app_settings
from cloudinary.forms import CloudinaryFileField
from django import forms
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from allauth.account.forms import (
    SignupForm, LoginForm, PasswordField, AddEmailForm, ResetPasswordForm,
    ChangePasswordForm
)
from allauth.socialaccount.forms import SignupForm as SocialSignupForm
from django_summernote.fields import SummernoteTextField
from django_summernote.widgets import SummernoteWidget
from django.contrib.auth.models import Group

from recipesnstuff import (
    IMAGE_FILE_TYPES, DEVELOPMENT, DEV_IMAGE_FILE_TYPES, MIN_PASSWORD_LEN
)
from recipesnstuff.settings import SUMMERNOTE_CONFIG
from utils import update_field_widgets, error_messages, ErrorMsgs
from .models import User
from .constants import (
    FIRST_NAME, LAST_NAME, EMAIL, EMAIL_CONFIRM, USERNAME,
    PASSWORD, PASSWORD_CONFIRM, BIO, AVATAR, GROUPS, OLD_PASSWORD
)


class UserFormMixin:
    """ Mixin to provide custom form utility functions """

    def add_bootstrap(
            self, fields: Union[List[str], Tuple[str], str],
            exclude: Optional[List[str]] = None):
        """
        Add bootstrap classes
        :param fields:  list of names of fields to update, or use
                '__all__' to update all fields
        :param exclude: list of names of fields to exclude
        """
        if exclude is None:
            exclude = []
        update_field_widgets(
            self,
            # exclude non-bootstrap fields
            [field for field in fields if field not in exclude],
            {'class': 'form-control'})


class UserSignupForm(UserFormMixin, SignupForm):
    """ Custom user sign up form """

    FIRST_NAME_FF = FIRST_NAME
    LAST_NAME_FF = LAST_NAME
    EMAIL_FF = EMAIL
    EMAIL_CONFIRM_FF = EMAIL_CONFIRM
    USERNAME_FF = USERNAME
    PASSWORD_FF = PASSWORD
    PASSWORD_CONFIRM_FF = PASSWORD_CONFIRM

    @dataclass
    class Meta:
        """ Form metadata """
        model = User
        fields = [
            FIRST_NAME, LAST_NAME, EMAIL, EMAIL_CONFIRM, USERNAME,
            PASSWORD, PASSWORD_CONFIRM
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields[UserSignupForm.PASSWORD_FF] = PasswordField(
            label=_("Password"), autocomplete="new-password",
            min_length=MIN_PASSWORD_LEN
        )
        if app_settings.SIGNUP_PASSWORD_ENTER_TWICE:
            self.fields[UserSignupForm.PASSWORD_CONFIRM_FF] = PasswordField(
                label=_("Confirm password"), autocomplete="new-password",
                min_length=MIN_PASSWORD_LEN
            )

        # add first & last name fields
        self.fields[UserSignupForm.FIRST_NAME_FF] = forms.CharField(
            label=_("First name"),
            max_length=User.USER_ATTRIB_FIRST_NAME_MAX_LEN,
            widget=forms.TextInput(attrs={
                "placeholder": _("User first name")
            }),
        )
        self.fields[UserSignupForm.LAST_NAME_FF] = forms.CharField(
            label=_("Last name"),
            max_length=User.USER_ATTRIB_LAST_NAME_MAX_LEN,
            widget=forms.TextInput(attrs={
                "placeholder": _("User last name")
            }),
        )

        # reorder fields so first & last name appear at start
        self.fields.move_to_end(UserSignupForm.LAST_NAME_FF, last=False)
        self.fields.move_to_end(UserSignupForm.FIRST_NAME_FF, last=False)

        # add the bootstrap class to the widget
        self.add_bootstrap(UserSignupForm.Meta.fields)

    def signup(self, request: HttpRequest, user: User) -> None:
        """
        Perform custom signup actions
        :param request:
        :param user: user object
        """
        pass


class UserLoginForm(UserFormMixin, LoginForm):
    """ Custom user login form """

    LOGIN_FF = "login"
    PASSWORD_FF = "password"

    @dataclass
    class Meta:
        """ Form metadata """
        fields = ["login", "password"]

    password = PasswordField(
        label=_("Password"), autocomplete="current-password",
        min_length=MIN_PASSWORD_LEN
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the bootstrap class to the widget
        self.add_bootstrap(UserLoginForm.Meta.fields)


class NoCurrentClearableFileInput(forms.ClearableFileInput):
    """ Customised ClearableFileInput form with different template """
    template_name = "widgets/clearable_file_input.html"

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context["widget"].update(
            {
                "file_input_id": f"id_{name}",
            }
        )
        return context


class UserForm(UserFormMixin, forms.ModelForm):
    """
    Form to update a user.
    """

    FIRST_NAME_FF = FIRST_NAME
    LAST_NAME_FF = LAST_NAME
    EMAIL_FF = EMAIL
    BIO_FF = BIO
    AVATAR_FF = AVATAR
    GROUPS_FF = GROUPS

    first_name = forms.CharField(
        label=_("First name"),
        max_length=User.USER_ATTRIB_FIRST_NAME_MAX_LEN,
        required=False)
    last_name = forms.CharField(
        label=_("Last name"),
        max_length=User.USER_ATTRIB_LAST_NAME_MAX_LEN,
        required=False)
    email = forms.EmailField(
        label=_("Email"),
        widget=forms.TextInput(
            attrs={
                "type": "email",
                "placeholder": _("E-mail address"),
                "autocomplete": "email",
            }
        ),
        required=False
    )

    bio = SummernoteTextField(blank=False)

    avatar_args = {
        "label": _("Avatar"),
        "required": False,
        "widget": NoCurrentClearableFileInput(attrs={
            # not all image types supported by Pillow which is used by
            # ImageField in dev mode
            "accept": ", ".join(
                DEV_IMAGE_FILE_TYPES if DEVELOPMENT else IMAGE_FILE_TYPES)
        })
    }
    # ImageField for local dev, CloudinaryFileField for production
    avatar = forms.ImageField(
            **avatar_args
        ) if DEVELOPMENT else CloudinaryFileField(
            options={
                'folder': User.avatar.field.options['folder'],
            },
            **avatar_args
        )

    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(), required=False
    )

    @dataclass
    class Meta:
        """ Form metadata """
        model = User
        fields = [
            FIRST_NAME, LAST_NAME, EMAIL, BIO, AVATAR, GROUPS
        ]
        non_bootstrap_fields = [BIO, AVATAR]
        help_texts = {
            FIRST_NAME: 'User first name.',
            LAST_NAME: 'User last name.',
            EMAIL: 'Email address of user.',
            BIO: 'Biography of user.',
            AVATAR: 'User avatar',
        }
        error_messages = error_messages(
            model.model_name_caps(),
            *[ErrorMsgs(field, max_length=True)
              for field in (FIRST_NAME, LAST_NAME)]
        )

        summernote_attr = SUMMERNOTE_CONFIG.copy()
        summernote_attr['summernote']['height'] = '240'

        widgets = {
            BIO: SummernoteWidget(attrs=summernote_attr),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # add the bootstrap class to the widget
        self.add_bootstrap(
            UserForm.Meta.fields, exclude=UserForm.Meta.non_bootstrap_fields)


class UserResetPasswordForm(UserFormMixin, ResetPasswordForm):
    """ Custom user password reset form """

    EMAIL_FF = EMAIL

    @dataclass
    class Meta:
        """ Form metadata """
        fields = [EMAIL]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add the bootstrap class to the widget
        self.add_bootstrap(UserResetPasswordForm.Meta.fields)


class UserChangePasswordForm(UserFormMixin, ChangePasswordForm):
    """ Custom user password change form """

    OLD_PASSWORD_FF = OLD_PASSWORD
    PASSWORD_FF = PASSWORD
    PASSWORD_CONFIRM_FF = PASSWORD_CONFIRM

    @dataclass
    class Meta:
        """ Form metadata """
        fields = [OLD_PASSWORD, PASSWORD, PASSWORD_CONFIRM]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add the bootstrap class to the widget
        self.add_bootstrap(UserChangePasswordForm.Meta.fields)


class UserSocialSignupForm(UserFormMixin, SocialSignupForm):
    """ Custom user social sign up form """

    EMAIL_FF = EMAIL
    EMAIL_CONFIRM_FF = EMAIL_CONFIRM
    USERNAME_FF = USERNAME

    @dataclass
    class Meta:
        """ Form metadata """
        fields = [
            EMAIL, EMAIL_CONFIRM, USERNAME
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # add the bootstrap class to the widget
        self.add_bootstrap(self, UserSocialSignupForm.Meta.fields)
