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
from ..user.base_user_test_cls import BaseUserTest

from profiles.models import Address


class TestUserModel(BaseUserTest):
    """
    Test user model
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super().setUpTestData()

    def test_address_defaults(self):
        """ Test user model defaults """
        user = self.login_user(self, self.get_user_by_index(0)[0])

        address = Address.objects.create(**{
            f'{Address.USER_FIELD}': user
        })
        self.assertIsNotNone(address)
        for field in [
            Address.COUNTRY_FIELD, Address.STREET_FIELD,
            Address.STREET2_FIELD, Address.CITY_FIELD,
            Address.STATE_FIELD, Address.POSTCODE_FIELD
        ]:
            with self.subTest(field=field):
                self.assertEqual(address.get_field(field), '')

        self.assertEqual(address.get_field(Address.IS_DEFAULT_FIELD), False)
