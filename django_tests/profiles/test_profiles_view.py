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
from http import HTTPStatus
from typing import Union, List, Tuple
from unittest import skip
from urllib.parse import urlencode

from bs4 import BeautifulSoup, Tag
from django.http import HttpResponse

from django_tests.soup_mixin import SoupMixin
from profiles.constants import (
    ADDRESSES_ROUTE_NAME, ADDRESS_ID_ROUTE_NAME,
    ADDRESSES_ID_DEFAULT_ROUTE_NAME, ADDRESS_NEW_ROUTE_NAME
)
from profiles.dto import AddressDto
from profiles.forms import AddressForm
from profiles.models import Address
from recipesnstuff import PROFILES_APP_NAME
from user.models import User
from utils import reverse_q, namespaced_url, USER_QUERY, Crud
from .base_profiles_test_cls import BaseProfilesTest

ADDRESS_LIST_TEMPLATE = f'{PROFILES_APP_NAME}/address_list.html'
ADDRESS_LIST_CONTENT_TEMPLATE = \
    f'{PROFILES_APP_NAME}/address_list_content.html'
ADDRESS_DTO_TEMPLATE = f'{PROFILES_APP_NAME}/address_dto.html'


class TestProfilesView(SoupMixin, BaseProfilesTest):
    """
    Test profiles page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        super().setUpTestData()

    def setUp(self):
        """ Set up test """
        # need 1 user for each Crud operation
        self.assertGreaterEqual(self.num_users(), len(Crud))
        self.create_idx = 0
        self.read_idx = 1
        self.update_idx = 2
        self.delete_idx = 3
        # give all users a subscription
        super().setUp()

    def login_user_by_key(self, name: str | None = None) -> User:
        """
        Login a user
        :param name: name of user to login; default first user in list
        :returns logged-in user
        """
        return BaseProfilesTest.login_user_by_key(self, name)

    def get_profile_addresses(self, user: User) -> HttpResponse:
        """
        Get the profile addresses page
        :param user: user to get profile for
        """
        self.assertIsNotNone(user)
        return self.client.get(
            reverse_q(
                namespaced_url(
                    PROFILES_APP_NAME, ADDRESSES_ROUTE_NAME
                ),
                query_kwargs={
                    USER_QUERY: user.username
                }
            )
        )

    def test_not_logged_in_access_addresses(self):
        """ Test must be logged in to access addresses """
        user, _ = TestProfilesView.get_user_by_index(self.read_idx)
        response = self.get_profile_addresses(user)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_addresses(self):
        """ Test addresses page uses correct template """
        user = self.login_user_by_key()
        response = self.get_profile_addresses(user)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for template in [
            ADDRESS_LIST_TEMPLATE, ADDRESS_LIST_CONTENT_TEMPLATE,
            ADDRESS_DTO_TEMPLATE
        ]:
            self.assertTemplateUsed(response, template)

    def test_own_addresses_content(self):
        """ Test addresses page content for logged-in user """
        _, key = TestProfilesView.get_user_by_index(self.read_idx)
        user = self.login_user_by_key(key)
        response = self.get_profile_addresses(user)
        self.verify_addresses_content(self.addresses[key], response)

    def test_other_addresses_content(self):
        """ Test addresses page content for not logged-in user """
        _, key = TestProfilesView.get_user_by_index(self.read_idx)
        logged_in_user = self.login_user_by_key(key)

        user, key = TestProfilesView.get_user_by_index(self.create_idx)

        self.assertNotEqual(logged_in_user, user)
        response = self.get_profile_addresses(user)
        self.assertEqual(response.status_code, HTTPStatus.FORBIDDEN)

    def test_added_address_in_list(self):
        """ Test addresses page content after adding a new address """
        _, key = TestProfilesView.get_user_by_index(self.create_idx)
        user = self.login_user_by_key(key)

        code, _ = BaseProfilesTest.get_country_code_name(0)
        data = {
            AddressForm.COUNTRY_FIELD_FF: code,
            AddressForm.STREET_FIELD_FF: "1 New St.",
            AddressForm.STREET2_FIELD_FF: "NewVille",
            AddressForm.CITY_FIELD_FF: "JustMinted",
            AddressForm.STATE_FIELD_FF: "New State",
            AddressForm.POSTCODE_FIELD_FF: "ABC-1",
        }

        response, new_addr = self.add_address(data)

        addresses = self.addresses[key].copy()
        addresses.append(new_addr)

        self.verify_addresses_content(addresses, response)

    def add_address(self, data: dict) -> Tuple[HttpResponse, Address]:
        """
        Add a new address
        :param data: address details
        :return: tuple of http response and new address model
        """
        response = self.client.post(reverse_q(
            namespaced_url(PROFILES_APP_NAME, ADDRESS_NEW_ROUTE_NAME)
        ), urlencode(data), content_type="application/x-www-form-urlencoded",
            follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        query = Address.objects.filter(**data)
        self.assertTrue(query.exists())
        new_addr = Address.objects.filter(**data).first()

        return response, new_addr

    def test_edited_address_in_list(self):
        """ Test addresses page content after editing an address """
        _, key = TestProfilesView.get_user_by_index(self.update_idx)
        user = self.login_user_by_key(key)

        # add address to edit
        code, _ = BaseProfilesTest.get_country_code_name(0)
        data = {
            AddressForm.COUNTRY_FIELD_FF: code,
            AddressForm.STREET_FIELD_FF: "1 Edit St.",
            AddressForm.STREET2_FIELD_FF: "ChangeVille",
            AddressForm.CITY_FIELD_FF: "Metamorphosis",
            AddressForm.STATE_FIELD_FF: "Edit State",
            AddressForm.POSTCODE_FIELD_FF: "XYZ-1",
        }

        response, new_addr = self.add_address(data)

        addresses = self.addresses[key].copy()
        addresses.append(new_addr)

        self.verify_addresses_content(addresses, response)

        # edit address
        code, _ = BaseProfilesTest.get_country_code_name(1)
        updated_data = {
            AddressForm.COUNTRY_FIELD_FF: code,
            AddressForm.STREET_FIELD_FF: "1 Edited St.",
            AddressForm.STREET2_FIELD_FF: "ChangedVille",
            AddressForm.CITY_FIELD_FF: "Metamorphosed",
            AddressForm.STATE_FIELD_FF: "Edited State",
            AddressForm.POSTCODE_FIELD_FF: "XYZ-1-ABC",
        }
        response, updated_addr = self.edit_address(new_addr.id, updated_data)

        addresses[-1] = updated_addr

        self.verify_addresses_content(addresses, response)

    def edit_address(
            self, pk: int, data: dict) -> Tuple[HttpResponse, Address]:
        """
        Edit an address
        :param pk: id of address to edit
        :param data: address details
        :return: tuple of http response and new address model
        """
        response = self.client.post(
            self.address_by_id_url(pk), urlencode(data),
            content_type="application/x-www-form-urlencoded", follow=True)

        self.assertEqual(response.status_code, HTTPStatus.OK)

        query = Address.objects.filter(**{
            f'{Address.id_field()}': pk
        })
        self.assertTrue(query.exists())
        addr = Address.objects.filter(**data).first()

        return response, addr

    def test_deleted_address_not_in_list(self):
        """ Test addresses page content after deleting an address """
        _, key = TestProfilesView.get_user_by_index(self.delete_idx)
        user = self.login_user_by_key(key)

        # add address to delete
        code, _ = BaseProfilesTest.get_country_code_name(-1)
        data = {
            AddressForm.COUNTRY_FIELD_FF: code,
            AddressForm.STREET_FIELD_FF: "1 Delete St.",
            AddressForm.STREET2_FIELD_FF: "GoneVille",
            AddressForm.CITY_FIELD_FF: "Tumbleweed Junction",
            AddressForm.STATE_FIELD_FF: "Old State",
            AddressForm.POSTCODE_FIELD_FF: "BYE-1",
        }

        response, new_addr = self.add_address(data)

        addresses = self.addresses[key].copy()
        addresses.append(new_addr)

        self.verify_addresses_content(addresses, response)

        # delete address
        self.delete_address(new_addr.id)

    def delete_address(self, pk: int) -> Tuple[HttpResponse, Address]:
        """
        Delete an address
        :param pk: id of address to delete
        :return: http response
        """
        response = self.client.delete(
            self.address_by_id_url(pk)
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

        return response

    def test_change_default_address(self):
        """ Test addresses page content after changing default """
        _, key = TestProfilesView.get_user_by_index(self.update_idx)
        user = self.login_user_by_key(key)

        addresses = list(
            map(AddressDto.from_model, self.addresses[key])
        )

        response = self.get_profile_addresses(user)
        self.verify_addresses_content(addresses, response)

        initial_default = [
            idx for idx, addr in enumerate(addresses) if addr.is_default
        ]
        self.assertEqual(len(initial_default), 1)
        initial_non_default = [
            idx for idx, addr in enumerate(addresses) if not addr.is_default
        ]
        self.assertGreaterEqual(len(initial_non_default), 1)

        # change default and then restore original state
        addr1 = addresses[initial_default[0]]
        addr2 = addresses[initial_non_default[0]]
        for idx in range(2):
            with self.subTest(idx=idx):
                addr1.is_default = not addr1.is_default
                addr2.is_default = not addr2.is_default

                response = self.client.patch(
                    self.address_default_url(
                        addr2.id if addr2.is_default else addr1.id
                    ), follow=True
                )
                self.assertEqual(response.status_code, HTTPStatus.OK)

                # verify new default in list
                response = self.get_profile_addresses(user)
                self.verify_addresses_content(addresses, response)

    def verify_addresses_content(
        self, expected: List[Union[Address, AddressDto]],
        response: HttpResponse
    ):
        """
        Verify addresses page content for user
        :param expected: list of expected addresses
        :param response: profile response
        """
        self.assertEqual(response.status_code, HTTPStatus.OK)

        soup = BeautifulSoup(
            response.content.decode("utf-8", errors="ignore"), features="lxml"
        )

        for address in expected:
            with self.subTest(address=address):
                # check address card
                cards = soup.find_all(id=f"id--address-{address.id}")
                self.assertEqual(len(cards), 1)

                dto = AddressDto.from_model(address) \
                    if isinstance(address, Address) else address

                matched = set()
                addr_line_count = sum(
                    map(lambda ln: 1 if ln else 0, dto.display_order)
                )
                country = getattr(dto, Address.COUNTRY_FIELD).code
                country = BaseProfilesTest.get_country_name(country)

                is_default = False      # is default address
                make_default = False    # can make default address
                can_delete = False      # can delete address
                for child in cards[0].descendants:
                    if isinstance(child, Tag):
                        if self.in_tag_attr(child, "class",
                                            "h6--default-addr"):
                            # default address
                            is_default = True
                        elif child.name == 'a':
                            if self.in_tag_attr(child, "class",
                                                "a--addr-edit"):
                                # edit link
                                self.assertTrue(
                                    SoupMixin.in_tag_attr(
                                        child, 'href',
                                        self.address_by_id_url(dto.id)),
                                    msg="edit url not found"
                                )
                            elif self.in_tag_attr(child, "class",
                                                  "a--addr-del"):
                                # make default link
                                self.assertTrue(
                                    SoupMixin.in_tag_attr(
                                        child, 'href',
                                        self.address_by_id_url(dto.id)),
                                    msg="delete url not found"
                                )
                                can_delete = True
                            elif self.in_tag_attr(child, "class",
                                                  "a--addr-dflt"):
                                # make default link
                                self.assertTrue(
                                    SoupMixin.in_tag_attr(
                                        child, 'href',
                                        self.address_default_url(dto.id)),
                                    msg="make default url not found"
                                )
                                make_default = True
                        elif child.name == 'p':
                            for line in dto.display_order_ex_country:
                                if not line:
                                    continue
                                if child.string == line:
                                    matched.add(child.string)
                                    break
                            else:
                                if child.string == country:
                                    matched.add(child.string)

                if dto.is_default:
                    self.assertTrue(is_default,
                                    msg="default address not marked")
                    self.assertFalse(make_default,
                                     msg="default address can make default")
                    self.assertFalse(can_delete,
                                     msg="default address can delete")
                else:
                    self.assertFalse(is_default,
                                     msg="non-default address marked")
                    self.assertTrue(
                        make_default,
                        msg="non-default address can't make default")
                    self.assertTrue(
                        can_delete,
                        msg="non-default address can't delete")

                self.assertEqual(
                    addr_line_count, len(matched),
                    msg=f"not all {dto.display_order} address lines "
                        f"matched {matched}")

    @staticmethod
    def address_by_id_url(address_id: int):
        """
        Generate an address by id url
        :param address_id: address id
        :return: url
        """
        return reverse_q(
            namespaced_url(PROFILES_APP_NAME, ADDRESS_ID_ROUTE_NAME),
            args=[address_id]
        )

    @staticmethod
    def address_default_url(address_id: int):
        """
        Generate an address default url
        :param address_id: address id
        :return: url
        """
        return reverse_q(
            namespaced_url(
                PROFILES_APP_NAME, ADDRESSES_ID_DEFAULT_ROUTE_NAME),
            args=[address_id]
        )
