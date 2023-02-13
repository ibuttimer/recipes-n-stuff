#  MIT License
#
#  Copyright (c) 2022-2023 Ian Buttimer
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
from datetime import datetime, timezone, timedelta
from typing import Optional

from django.test import TestCase

from subscription.models import (
    Subscription, UserSubscription, SubscriptionStatus
)
from user.models import User
from user.permissions import add_to_registered


class BaseUserTest(TestCase):
    """
    Base user test class
    https://docs.djangoproject.com/en/4.1/topics/testing/tools/
    """
    fixtures = [
        'currencies.json', 'subscription_feature_test.json',
        'subscription_test.json'
    ]

    USER_INFO = {
        user[0].lower(): {
            User.FIRST_NAME_FIELD: user[0],
            User.LAST_NAME_FIELD: user[1],
            User.USERNAME_FIELD: user[2],
            User.PASSWORD_FIELD: user[3],
            User.EMAIL_FIELD: user[4],
            User.AVATAR_FIELD: user[5],
            User.BIO_FIELD: user[6],
        } for user in [
            ("Joe", "Cherry", "joe.cherry",
             "more-than-8-not-like-user", "ask.joe@fruits.com",
             "flattering-pic.jpg", "The man in the know"),
            ("Ana", "Banana", "ana.banana",
             "more-than-8-on-a-plate", "ask.ana@fruits.com",
             "nice-pic.jpg", "The woman to ask"),
            ("Julius", "Caesar", "julius.caesar",
             "more-than-VII", "ask.caesar@rome.com",
             "majestic-pic.jpg", "Man could burn water"),
            ("Georges Auguste", "Escoffier", "georges.auguste",
             "8+-tyne-fork", "ask.georges@cooking.com",
             "serious-pic.jpg", "king of chefs and chef of kings"),
        ]
    }

    users: dict[str, User]
    registered: dict[str, User]

    @staticmethod
    def create_users() -> dict:
        """
        Create test users
        :return: dict of test users
        """
        return {
            key: User.objects.create(**BaseUserTest.USER_INFO[key])
            for key in BaseUserTest.USER_INFO
        }

    @classmethod
    def setUpTestData(cls):
        """ Set up data for the whole TestCase """
        cls.users = BaseUserTest.create_users()
        cls.registered = {}
        for user in cls.users.values():
            add_to_registered(user)
            cls.registered.update(**{
                user.username: user
            })

    def setUp(self):
        """ Set up test """
        self.user_config(add_subs=True)

    def user_config(self, add_subs: bool = True):
        """ Configure test users """
        self.subscriptions = list(Subscription.objects.all())
        if add_subs:
            # give all users a subscription
            now = datetime.now(tz=timezone.utc)
            start = now - timedelta(minutes=1)
            end = now + timedelta(days=1)
            for idx, user_item in enumerate(self.users.items()):
                sub = UserSubscription.objects.create(**{
                    f'{UserSubscription.SUBSCRIPTION_FIELD}':
                        self.subscriptions[idx % len(self.subscriptions)],
                    f'{UserSubscription.USER_FIELD}': user_item[1],
                    f'{UserSubscription.START_DATE_FIELD}': start,
                    f'{UserSubscription.END_DATE_FIELD}': end,
                    f'{UserSubscription.STATUS_FIELD}':
                        SubscriptionStatus.ACTIVE.choice
                })
                self.assertIsNotNone(sub)

    @classmethod
    def get_user_by_index(cls, index: int) -> tuple[User, str]:
        """
        Get a test user by key index
        :param index: key index
        :return: tuple of user and key
        """
        key = cls.get_user_key(index)
        return cls.users[key], key

    @classmethod
    def get_user_key(cls, index: int) -> str:
        """
        Get a test user key by index
        :param index: key index
        :return: key for user
        """
        return list(
            BaseUserTest.USER_INFO.keys()
        )[index % len(BaseUserTest.USER_INFO)]

    @classmethod
    def get_other_user(cls, not_this_user: User, moderator: bool = False):
        """
        Get a user other than the specified user
        :param not_this_user: user to not get
        :param moderator: is moderator flag; default False
        :return: another user
        """
        for user_idx in range(len(cls.users)):
            user, _ = cls.get_user_by_index(user_idx)
            if user != not_this_user:
                break
        else:
            raise ValueError(
                f'{"Moderator" if moderator else "User"} other than '
                f'{not_this_user} not found')
        return user

    @classmethod
    def num_users(cls):
        """ Get number of users """
        return len(cls.users)

    @staticmethod
    def login_user(test_instance: TestCase, user: User) -> User:
        """
        Login user
        :param test_instance: instance of user test case
        :param user: user to login
        :returns logged-in user
        """
        test_instance.assertIsNotNone(user)
        test_instance.client.force_login(user)
        return user

    @staticmethod
    def login_user_by_key(
            test_instance: TestCase, name: Optional[str] = None) -> User:
        """
        Login user
        :param test_instance: instance of user test case
        :param name: name of user to login; default first user in list
        :returns logged-in user
        """
        if name is None:
            name = BaseUserTest.get_user_key(0)
        user = test_instance.users[name.lower()]
        return test_instance.login_user(test_instance, user)

    @staticmethod
    def login_user_by_id(test_instance, pk: int) -> User:
        """
        Login user
        :param test_instance: instance of user test case
        :param pk: id of user to login
        :returns logged-in user
        """
        users = list(
            filter(lambda u: u.id == pk, test_instance.users.values())
        )
        test_instance.assertEqual(len(users), 1)
        user = users[0]
        return BaseUserTest.login_user(test_instance, user)
