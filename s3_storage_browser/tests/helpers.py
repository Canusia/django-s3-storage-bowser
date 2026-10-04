import itertools
from unittest import mock

from django.contrib.auth import get_user_model
from django.contrib.auth.models import Permission
from django.contrib.auth.signals import user_logged_in

_seq = itertools.count()


def make_user(**extra):
    n = next(_seq)
    email = f's3b_user_{n}@example.com'
    return get_user_model().objects.create_user(
        username=email, email=email, password='x',
        first_name='S3', last_name=f'User{n}', **extra)


def grant_package_permission(user):
    user.user_permissions.add(
        Permission.objects.get(codename='can_access_s3_storage_browser'))
    # has_perm caches per instance; return a fresh copy
    return get_user_model().objects.get(pk=user.pk)


def allow_all(user):
    return True


def deny_all(user):
    return False


def login(client, user):
    """force_login without host user_logged_in receivers (e.g. login-history
    trackers that need a real request IP), which these tests do not exercise."""
    with mock.patch.object(user_logged_in, 'send'):
        client.force_login(user)


def menu_context(request):
    return {'menu': '<li id="hook-menu-item">Hook</li>'}
