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
#
from allauth.socialaccount.models import SocialLogin
from django.contrib import messages
from django.dispatch import receiver
from allauth.account.signals import (
    user_logged_in, user_logged_out, user_signed_up
)
from allauth.socialaccount.signals import (
    pre_social_login, social_account_added, social_account_updated,
    social_account_removed
)
from django.http import HttpRequest
from django.template.loader import render_to_string

from utils import app_template_path
from .constants import USER_CTX, THIS_APP
from .models import User
from .permissions import add_to_registered


NEW_USER_TEMPLATE = app_template_path(
    THIS_APP, "snippet", "new_user_notification.html")


# Logging in with Google means logged in straight away as allauth can get
# email from the requested scopes.
# https://django-allauth.readthedocs.io/en/latest/providers.html#google
# As Twitter doesn't include the scopes, the user must manually add an email.
# https://django-allauth.readthedocs.io/en/latest/providers.html#twitter


@receiver(user_logged_in)
def user_logged_in_callback(sender, **kwargs):
    """ Process signal sent when a user logs in """
    # by the time this signal is received the 'last_login' field in
    # AbstractBaseUser has already been updated to the current login
    user: User = kwargs.get('user', None)
    if user:
        # have to do add to group here as can't do socials in
        # pre_social_login_callback
        add_to_registered(user)


@receiver(user_logged_out)
def user_logged_out_callback(sender, **kwargs):
    """ Process signal sent when a user logs out """
    user: User = kwargs.get('user', None)
    if user:
        # update previous login
        user.previous_login = user.last_login
        user.save(update_fields=[User.PREVIOUS_LOGIN_FIELD])


@receiver(user_signed_up)
def user_signed_up_callback(sender, **kwargs):
    """ Process signal sent when a user registers """
    user: User = kwargs.get('user', None)
    if user:
        add_to_registered(user)
        process_register_new_user(kwargs.get('request', None), user)


@receiver(pre_social_login)
def pre_social_login_callback(sender, **kwargs):
    """ Process signal sent when a user begins a social login """
    social: SocialLogin = kwargs.get('sociallogin', None)
    if social:
        # user in sociallogin has not yet been committed to database so can't
        # add to groups here
        pass


@receiver(social_account_added)
def social_account_added_callback(sender, **kwargs):
    """ Process signal sent when a user begins a social account is added """


@receiver(social_account_updated)
def social_account_updated_callback(sender, **kwargs):
    """ Process signal sent when a user begins a social account is updated """


@receiver(social_account_removed)
def social_account_removed_callback(sender, **kwargs):
    """ Process signal sent when a user begins a social account is removed """


def process_register_new_user(request: HttpRequest, user: User):
    """
    Process registration of a new user
    :param user: user which logged in
    :param request: http request
    """
    if user:
        messages.info(
            request, render_to_string(NEW_USER_TEMPLATE, context={
                USER_CTX: user,
            })
        )
