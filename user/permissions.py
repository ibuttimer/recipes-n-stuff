
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

from collections import namedtuple
from typing import Union, List

from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.db.backends.base.schema import BaseDatabaseSchemaEditor
from django.db.migrations.state import StateApps
from django.contrib.auth.management import create_permissions
from django.db.models import Model

from profiles.models import Address
from recipesnstuff import PROFILES_APP_NAME
from recipesnstuff.constants import SUBSCRIPTION_APP_NAME
from subscription.models import Subscription
from utils import permission_name, Crud, ensure_list
from .constants import REGISTERED_GROUP
from .models import User

ADD = 'add'
REMOVE = 'remove'
PermSetting = namedtuple(
    'PermSetting',
    ['model', 'all', 'perms', 'app', 'action'],
    defaults=[None, False, [], '', ADD]
)


def create_registered_group(
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None) -> Group:
    """
    Create the registered group
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    :return: new group
    """
    return create_group_and_permissions(
        REGISTERED_GROUP, [
            PermSetting(
                model=Address, all=True, app=PROFILES_APP_NAME, action=ADD
            )
        ], apps=apps, schema_editor=schema_editor)


def remove_registered_group(apps: StateApps,
                            schema_editor: BaseDatabaseSchemaEditor):
    """
    Migration reverse function to remove the registered group
    :param apps: apps registry
    :param schema_editor:
        editor generating statements to change database schema
    """
    migration_remove_group(apps, schema_editor, REGISTERED_GROUP)


def create_group_and_permissions(
        group_name: str,
        perm_settings: list[PermSetting] | None = None,
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None) -> Group:
    """
    Create a group and assign permissions
    :param group_name: name of group to create
    :param perm_settings: list of permission settings
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    :return: new group
    """
    group = None
    if apps:    # called from a migration
        migration_add_group(apps, schema_editor, group_name)

        set_basic_permissions(group_name, perm_settings,
                              apps=apps, schema_editor=schema_editor)
    else:       # called from the app
        group, created = Group.objects.get_or_create(name=group_name)
        if created or group.permissions.count() == 0:
            set_basic_permissions(group, perm_settings)

    return group


def migration_add_group(
        apps: StateApps, schema_editor: BaseDatabaseSchemaEditor, name: str):
    """
    Migration function to add a group
    :param apps: apps registry
    :param schema_editor:
        editor generating statements to change database schema
    :param name: name of group to add
    """
    group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    group.objects.using(db_alias).create(name=name)


def migration_remove_group(
        apps: StateApps, schema_editor: BaseDatabaseSchemaEditor, name: str):
    """
    Migration reverse function to remove a group
    :param apps: apps registry
    :param schema_editor:
        editor generating statements to change database schema
    :param name: name of group to remove
    """
    group = apps.get_model("auth", "Group")
    db_alias = schema_editor.connection.alias
    group.objects.using(db_alias).filter(name=name).delete()


def set_basic_permissions(group: [Group, str],
                          perm_settings: list[PermSetting] = None,
                          apps: StateApps = None,
                          schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Set the permissions for the specified group
    :param group:
        group to update; Group object in app mode or name of group in
        migration mode
    :param perm_settings: list of permission settings
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    def set_permissions(grp: Group, setting: PermSetting, perms):
        # add/remove specified permissions
        if setting.action == ADD:
            grp.permissions.add(*perms)
        elif setting.action == REMOVE:
            grp.permissions.remove(*perms)

    if apps:    # called from a migration
        db_alias = schema_editor.connection.alias
        group = apps.get_model("auth", "Group")\
            .objects.using(db_alias).filter(name=group).first()
        assert group is not None
        permission = apps.get_model("auth", "Permission")

        if not permission.objects.using(db_alias).exists():
            migrate_permissions(apps=apps, schema_editor=schema_editor)

        if perm_settings:
            for perm_setting in perm_settings:
                if perm_setting.all:
                    # add all model crud permissions
                    model = perm_setting.model._meta.model_name.lower()
                    filter_args = {
                        'codename__endswith': f"_{model}",
                        'content_type__app_label': perm_setting.app
                    }
                else:
                    # add specified permissions
                    filter_args = {
                        'codename__in': perm_setting.perms,
                        'content_type__app_label': perm_setting.app
                    }
                permissions = permission.objects.using(db_alias).\
                    filter(**filter_args)
                assert permissions.exists(), f'{filter_args}'
                set_permissions(group, perm_setting, permissions)

    else:   # called from the app
        if perm_settings:
            for perm_setting in perm_settings:
                content_type = ContentType.objects. \
                    get_for_model(perm_setting.model)
                if perm_setting.all:
                    # add all model crud permissions
                    permissions = Permission.objects.\
                        filter(content_type=content_type)
                else:
                    # add specified permissions
                    permissions = Permission.objects.filter(
                        content_type=content_type,
                        codename__in=perm_setting.perms)
                assert permissions.exists()
                set_permissions(group, perm_setting, permissions)


def add_to_registered(user: User):
    """
    Add the specified user to the registered group
    :param user: user to update
    """
    user.groups.add(
        create_registered_group()
    )


def migrate_permissions(apps: StateApps = None,
                        schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Migrate permissions.

    This is a necessary operation prior to assigning permissions during
    migration on a *pristine* database. If this operation is not performed
    the permissions don't exist, so can't be assigned.
    Thanks to https://stackoverflow.com/a/40092780/4054609

    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    for app_config in apps.get_app_configs():
        app_config.models_module = True
        create_permissions(app_config, apps=apps, verbosity=0)
        app_config.models_module = None


def reverse_migrate_permissions(
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None):
    """ Dummy reverse for migrate_permissions """


def set_group_permissions(
        assignees: Union[str, List[str]],
        model: Model, ops: List[Crud], app_name: str,
        action: str, apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Set group permissions
    :param assignees: name(s) of group(s) to set permissions for
    :param model: model whose permissions to apply
    :param ops: list of Crud operations
    :param app_name: app name
    :param action: action to perform; ADD or REMOVE
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    to_assign = ensure_list(assignees)
    if not apps:    # called from the app
        to_assign = list(
            map(lambda grp: Group.objects.get_or_create(name=grp), to_assign)
        )
    # else called from a migration

    permissions = [
        permission_name(model, cmt) for cmt in ensure_list(ops)
    ]
    for group in to_assign:
        set_basic_permissions(group, [
            PermSetting(model=model, perms=permissions,
                        app=app_name, action=action)
        ], apps=apps, schema_editor=schema_editor)


def add_subs_permissions_for_registered(
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Add subscription permissions for registered group
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    create_registered_group(apps=apps, schema_editor=schema_editor)
    set_group_permissions(
        REGISTERED_GROUP, Subscription, Crud.READ, SUBSCRIPTION_APP_NAME,
        ADD, apps=apps, schema_editor=schema_editor)


def remove_subs_permissions_for_registered(
        apps: StateApps = None,
        schema_editor: BaseDatabaseSchemaEditor = None):
    """
    Remove subscription permissions for registered group
    :param apps: apps registry, default None
    :param schema_editor:
        editor generating statements to change database schema, default None
    """
    set_group_permissions(
        REGISTERED_GROUP, Subscription, Crud.READ, SUBSCRIPTION_APP_NAME,
        REMOVE, apps=apps, schema_editor=schema_editor)
