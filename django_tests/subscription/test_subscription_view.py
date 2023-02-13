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
from typing import Union, List

from bs4 import BeautifulSoup, Tag
from django.http import HttpResponse

from profiles.constants import ADDRESSES_ROUTE_NAME
from recipesnstuff import SUBSCRIPTION_APP_NAME, PROFILES_APP_NAME, \
    USER_APP_NAME
from subscription.constants import SUBSCRIPTION_CHOICE_ROUTE_NAME
from subscription.views.dto import SubscriptionDto
from subscription.models import Subscription
from user import USER_ID_ROUTE_NAME
from user.models import User
from utils import reverse_q, namespaced_url, Crud, USER_QUERY
from django_tests.soup_mixin import SoupMixin

from django_tests.profiles.base_profiles_test_cls import BaseProfilesTest

SUBSCRIPTION_LIST_TEMPLATE = f'{SUBSCRIPTION_APP_NAME}/subscription_list.html'
SUBSCRIPTION_LIST_CONTENT_TEMPLATE = \
    f'{SUBSCRIPTION_APP_NAME}/subscription_list_content.html'
SUBSCRIPTION_DTO_TEMPLATE = f'{SUBSCRIPTION_APP_NAME}/subscription_dto.html'
SUBSCRIPTION_SELECT_TEMPLATE = \
    f'{SUBSCRIPTION_APP_NAME}/select_subscription.html'


class TestSubscriptionView(SoupMixin, BaseProfilesTest):
    """
    Test profiles page view
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """
    fixtures = [
        'currencies.json', 'subscription_feature_test.json',
        'subscription_test.json'
    ]

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
        # no subscriptions for users
        self.user_config(add_subs=False)

    def login_user_by_key(self, name: str | None = None) -> User:
        """
        Login a user
        :param name: name of user to login; default first user in list
        :returns logged-in user
        """
        return BaseProfilesTest.login_user_by_key(self, name)

    def get_subscriptions(self, user: User,
                          follow: bool = False) -> HttpResponse:
        """
        Get the subscriptions page
        :param user: user to get subscriptions for
        :param follow: follow redirect flag; default False
        """
        self.assertIsNotNone(user)
        return self.client.get(
            reverse_q(
                namespaced_url(
                    SUBSCRIPTION_APP_NAME, SUBSCRIPTION_CHOICE_ROUTE_NAME
                )
            ), follow=follow
        )

    def test_not_logged_in_access_subscription(self):
        """ Test must be logged in to access subscriptions """
        user, _ = TestSubscriptionView.get_user_by_index(self.read_idx)
        response = self.get_subscriptions(user)
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_get_subscriptions(self):
        """ Test subscriptions page uses correct template """
        user = self.login_user_by_key()
        response = self.get_subscriptions(user, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)
        for template in [
            SUBSCRIPTION_SELECT_TEMPLATE
        ]:
            self.assertTemplateUsed(response, template)

    def test_subscription_sandbox(self):
        """ Test in subscription sandbox """
        user = self.login_user_by_key()
        response = self.get_subscriptions(user, follow=True)
        self.assertEqual(response.status_code, HTTPStatus.OK)

        self.verify_subscriptions_content(self.subscriptions, response)

        for route in [
            reverse_q(
                namespaced_url(PROFILES_APP_NAME, ADDRESSES_ROUTE_NAME),
                query_kwargs={
                    USER_QUERY: user.username
                }
            ),
            reverse_q(
                namespaced_url(USER_APP_NAME, USER_ID_ROUTE_NAME),
                args=[user.id]
            ),
        ]:
            with self.subTest(route=route):
                response = self.client.get(route, follow=True)
                # verify redirected to subscriptions
                self.verify_subscriptions_content(self.subscriptions, response)

    # TODO test subscription selection

    def verify_subscriptions_content(
        self, expected: List[Union[Subscription, SubscriptionDto]],
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

        TestSubscriptionView.find_tag(
            self, soup.find_all('h3'),
            check_func=lambda tag: 'Subscription Choice' in tag.text)

        for subscription in expected:
            with self.subTest(address=subscription):
                # check address card
                cards = soup.find_all(id=f"id--subscription-{subscription.id}")
                self.assertEqual(len(cards), 1)

                dto = SubscriptionDto.from_model(subscription) \
                    if isinstance(subscription, Subscription) else subscription

                for child in cards[0].descendants:
                    if isinstance(child, Tag):
                        if self.in_tag_attr(child, "class", "card-header"):
                            # subscription cost
                            self.assertIn(dto.name, child.text,
                                          msg="name not found")
                        elif self.in_tag_attr(child, "class", "card-title"):
                            # subscription cost
                            self.assertIn(str(dto.amount), child.text,
                                          msg="amount not found")
