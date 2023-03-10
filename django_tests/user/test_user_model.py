#  MIT License
#
#  Copyright (c) 2022 Ian Buttimer
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
from django.test import TestCase

from user.models import User


class TestUserModel(TestCase):
    """
    Test user model
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    def test_user_defaults(self):
        """ Test user model defaults """
        user = User.objects.create()
        self.assertIsNotNone(user)
        for field in [
            User.FIRST_NAME_FIELD, User.LAST_NAME_FIELD,
            User.PASSWORD_FIELD, User.EMAIL_FIELD,
            User.BIO_FIELD
        ]:
            with self.subTest(field=field):
                self.assertEqual(user.get_field(field), '')

        self.assertIn(User.AVATAR_FIELD, user.avatar.url)
