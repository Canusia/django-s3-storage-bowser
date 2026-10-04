from django.test import TestCase, override_settings

from s3_storage_browser.access import has_access

from .helpers import make_user


class HasAccessTests(TestCase):

    @override_settings(
        S3_STORAGE_BROWSER_ACCESS_CHECK='s3_storage_browser.tests.helpers.allow_all')
    def test_inactive_user_is_refused_even_when_the_override_allows(self):
        # Some host auth backends still return inactive users for a live
        # session, and host role checks rarely look at is_active.
        self.assertFalse(has_access(make_user(is_active=False)))

    @override_settings(
        S3_STORAGE_BROWSER_ACCESS_CHECK='s3_storage_browser.tests.helpers.allow_all')
    def test_active_user_follows_the_override(self):
        self.assertTrue(has_access(make_user()))

    @override_settings(S3_STORAGE_BROWSER_ACCESS_CHECK=None)
    def test_inactive_staff_is_refused_by_default(self):
        self.assertFalse(has_access(make_user(is_staff=True, is_active=False)))
