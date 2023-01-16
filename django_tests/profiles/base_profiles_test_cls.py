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
from string import capwords
from typing import Tuple

from django_countries import countries

from django_tests.user.base_user_test_cls import BaseUserTest
from profiles.models import Address


class BaseProfilesTest(BaseUserTest):
    """
    Base profiles test class
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """
    addresses: dict[str, list[Address]]

    country_list = list(countries)

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        BaseUserTest.setUpTestData()

        cls.addresses = {}

        idx = 1
        for name, user in cls.users.items():
            addresses = []
            for num in range(2):
                first_name = capwords(user.first_name)
                last_name = capwords(user.last_name)
                code, _ = BaseProfilesTest.get_country_code_name(idx)
                info = {
                    f'{Address.USER_FIELD}': user,
                    f'{Address.COUNTRY_FIELD}': code,
                    f'{Address.STREET_FIELD}': f'{idx} {first_name} St.',
                    f'{Address.STREET2_FIELD}': f'{first_name} Ville',
                    f'{Address.CITY_FIELD}': f'{last_name} City',
                    f'{Address.STATE_FIELD}': f'{last_name} State',
                    f'{Address.POSTCODE_FIELD}': f'{last_name.upper()}{idx}',
                    f'{Address.IS_DEFAULT_FIELD}': num == 0,
                }
                addresses.append(
                    Address.objects.create(**info)
                )
                idx += 1

            cls.addresses[name] = addresses

    @classmethod
    def get_addresses_by_key(cls, key: str) -> list[Address]:
        """
        Get addresses for test user by user key
        :param key: key
        :return: list of addresses
        """
        return cls.addresses[key]

    @classmethod
    def get_addresses_by_index(cls, index: int) -> tuple[list[Address], str]:
        """
        Get addresses for test user by key index
        :param index: key index
        :return: tuple of addresses and user key
        """
        key = cls.get_user_key(index)
        return cls.get_addresses_by_key(key), key

    @classmethod
    def get_country_code_name(cls, index: int) -> Tuple[str, str]:
        """
        Get the country code and name for a country
        :param index: index of country
        :return: tuple of code and name
        """
        code, name = BaseProfilesTest.country_list[
            index % len(BaseProfilesTest.country_list)]
        return code, name

    @classmethod
    def num_countries(cls) -> int:
        """
        Get the number of countries
        :return: country count
        """
        return len(BaseProfilesTest.country_list)

    @classmethod
    def get_country_name(cls, code: str) -> Tuple[str, str]:
        """
        Get a country name
        :param code: two letter country code for the country
        :return: name
        """
        return dict(countries)[code]
