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
from enum import Enum, auto
from typing import Union, List
from django.conf import settings

from django.core.mail import send_mail
from django.template.loader import render_to_string

from utils import ensure_list


class EmailOpt(Enum):
    """ Enum representing email options """
    PLAIN_TEXT = auto()
    SUBJECT_TEMPLATE = auto()
    BODY_TEMPLATE = auto()
    ALL_TEMPLATE = auto()


def send_email(subject: str, body: str, recipient: Union[str, List[str]],
               opt: EmailOpt = EmailOpt.PLAIN_TEXT, context: dict = None,
               sender: str = None):
    """
    Send an email
    :param subject: subject text or template path
    :param body: body text or template path
    :param recipient: recipient email or list thereof
    :param opt: email options; default EmailOpt.PLAIN_TEXT
    :param context: context to use for rendering templates; default None
    :param sender: sender email address; default `DEFAULT_SEND_EMAIL` from
                    settings
    """
    if not sender:
        sender = settings.DEFAULT_SEND_EMAIL

    if opt in [EmailOpt.SUBJECT_TEMPLATE, EmailOpt.ALL_TEMPLATE]:
        subject = render_to_string(subject, context=context)
    if opt in [EmailOpt.BODY_TEMPLATE, EmailOpt.ALL_TEMPLATE]:
        body = render_to_string(body, context=context)

    send_mail(subject, body, sender, ensure_list(recipient))
