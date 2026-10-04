"""
Who may use the storage browser.

One check gates both the page and the credentials API, so a user who cannot
open the page cannot mint bucket credentials either.
"""
from django.conf import settings
from django.utils.module_loading import import_string
from rest_framework.permissions import BasePermission

PERMISSION = 's3_storage_browser.can_access_s3_storage_browser'


def default_access_check(user):
    """Staff, or anyone granted the package permission (superusers included)."""
    return user.is_active and (user.is_staff or user.has_perm(PERMISSION))


def has_access(user):
    """
    True when ``user`` may use the storage browser.

    ``settings.S3_STORAGE_BROWSER_ACCESS_CHECK`` — a dotted path to a
    ``callable(user) -> bool`` — replaces the default check when set.
    """
    if user is None or not user.is_authenticated:
        return False
    dotted = getattr(settings, 'S3_STORAGE_BROWSER_ACCESS_CHECK', None)
    check = import_string(dotted) if dotted else default_access_check
    return bool(check(user))


class HasStorageBrowserAccess(BasePermission):
    def has_permission(self, request, view):
        return has_access(request.user)
