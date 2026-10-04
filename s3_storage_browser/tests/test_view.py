import copy
import json
import os
import re

from django.conf import settings
from django.test import TestCase, override_settings

from .helpers import make_user, grant_package_permission, login

BUCKET = 'tenant-bucket'
TEST_TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), 'templates')

TEST_TEMPLATES = copy.deepcopy(settings.TEMPLATES)
TEST_TEMPLATES[0]['DIRS'] = [*TEST_TEMPLATES[0].get('DIRS', []), TEST_TEMPLATE_DIR]

CONFIG_RE = re.compile(
    r'<script id="s3-storage-browser-config" type="application/json">(.*?)</script>',
    re.S)


@override_settings(
    ROOT_URLCONF='s3_storage_browser.tests.urls',
    TEMPLATES=TEST_TEMPLATES,
    AWS_STORAGE_BUCKET_NAME=BUCKET,
    S3_STORAGE_BROWSER_ACCESS_CHECK=None,
    S3_STORAGE_BROWSER_BASE_TEMPLATE=None,
    S3_STORAGE_BROWSER_EXTRA_CONTEXT=None,
    S3_STORAGE_BROWSER_REGION=None,
    AWS_S3_REGION_NAME=None,
    AWS_REGION_NAME='eu-west-1',
)
class StorageBrowserViewTests(TestCase):
    url = '/storagebrowser/'

    def setUp(self):
        self.client = self.client_class(REMOTE_ADDR='127.0.0.1')

    def get_as(self, user, url=None):
        login(self.client, user)
        return self.client.get(url or self.url)

    def config(self, resp):
        match = CONFIG_RE.search(resp.content.decode())
        self.assertIsNotNone(match, 'config json_script missing')
        return json.loads(match.group(1))

    def test_anonymous_is_sent_to_login(self):
        resp = self.client.get(self.url)
        self.assertEqual(resp.status_code, 302)
        self.assertIn('next=/storagebrowser/', resp['Location'])

    def test_user_without_access_is_forbidden(self):
        self.assertEqual(self.get_as(make_user()).status_code, 403)

    def test_package_permission_grants_the_page(self):
        user = grant_package_permission(make_user())
        self.assertEqual(self.get_as(user).status_code, 200)

    def test_default_renders_standalone_page(self):
        resp = self.get_as(make_user(is_staff=True))
        self.assertEqual(resp.status_code, 200)
        names = [t.name for t in resp.templates]
        self.assertIn('s3_storage_browser/index.html', names)
        self.assertIn('s3_storage_browser/standalone.html', names)
        self.assertIn('s3_storage_browser/_app.html', names)
        html = resp.content.decode()
        self.assertIn('<div id="root"></div>', html)
        self.assertIn('s3_storage_browser/index.js', html)
        self.assertIn('s3_storage_browser/index.css', html)

    def test_config_carries_bucket_region_and_credentials_url(self):
        resp = self.get_as(make_user(is_staff=True))
        self.assertEqual(self.config(resp), {
            'bucket': BUCKET,
            'region': 'eu-west-1',
            'credentialsUrl': '/storagebrowser/credentials/',
        })

    @override_settings(S3_STORAGE_BROWSER_REGION='us-west-2')
    def test_region_setting_wins(self):
        resp = self.get_as(make_user(is_staff=True))
        self.assertEqual(self.config(resp)['region'], 'us-west-2')

    @override_settings(S3_STORAGE_BROWSER_BASE_TEMPLATE='s3b_tests/base.html')
    def test_base_template_setting_wraps_the_app(self):
        resp = self.get_as(make_user(is_staff=True))
        html = resp.content.decode()
        self.assertIn('TEST-BASE-SENTINEL', html)
        self.assertIn('<div id="root"></div>', html)
        self.assertIn('<title>Storage Browser</title>', html)
        self.assertNotIn('s3_storage_browser/standalone.html',
                         [t.name for t in resp.templates])

    @override_settings(
        S3_STORAGE_BROWSER_BASE_TEMPLATE='s3b_tests/base.html',
        S3_STORAGE_BROWSER_EXTRA_CONTEXT='s3_storage_browser.tests.helpers.menu_context')
    def test_extra_context_hook_reaches_the_base_template(self):
        html = self.get_as(make_user(is_staff=True)).content.decode()
        self.assertIn('<li id="hook-menu-item">Hook</li>', html)

    def test_template_name_kwarg_is_honoured(self):
        resp = self.get_as(make_user(is_staff=True), '/custom/')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(f'CUSTOM-TEMPLATE {BUCKET}', resp.content.decode())

    @override_settings(AWS_STORAGE_BUCKET_NAME='</script><script>alert(1)</script>')
    def test_bucket_name_cannot_break_out_of_the_config_script(self):
        resp = self.get_as(make_user(is_staff=True))
        self.assertNotIn('<script>alert(1)', resp.content.decode())
        self.assertEqual(self.config(resp)['bucket'],
                         '</script><script>alert(1)</script>')

    @override_settings(ROOT_URLCONF='s3_storage_browser.tests.urls_legacy')
    def test_hand_mounted_view_falls_back_to_legacy_credentials_url(self):
        resp = self.get_as(make_user(is_staff=True), '/ce/storagebrowser/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(self.config(resp)['credentialsUrl'], '/api/awscreds/')

    @override_settings(AWS_REGION_NAME=None)
    def test_region_defaults_to_us_east_1(self):
        resp = self.get_as(make_user(is_staff=True))
        self.assertEqual(self.config(resp)['region'], 'us-east-1')
