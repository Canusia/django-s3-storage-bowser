import json
from datetime import datetime, timezone
from unittest import mock

from botocore.exceptions import ClientError
from django.test import TestCase, override_settings
from django.urls import reverse

from .helpers import make_user, grant_package_permission, login

ROLE_ARN = 'arn:aws:iam::123456789012:role/StorageBrowser'
BUCKET = 'tenant-bucket'

STS_RESPONSE = {
    'Credentials': {
        'AccessKeyId': 'ASIAEXAMPLE',
        'SecretAccessKey': 'secret',
        'SessionToken': 'token',
        'Expiration': datetime(2030, 1, 1, tzinfo=timezone.utc),
    }
}


@override_settings(
    ROOT_URLCONF='s3_storage_browser.tests.urls',
    AWS_STORAGE_BUCKET_NAME=BUCKET,
    S3_STORAGE_BROWSER_ROLE_ARN=ROLE_ARN,
    S3_STORAGE_BROWSER_ACCESS_CHECK=None,
)
class CredentialsApiTests(TestCase):

    def setUp(self):
        self.url = reverse('s3_storage_browser:credentials')
        patcher = mock.patch('s3_storage_browser.views.boto3.client')
        self.boto_client = patcher.start()
        self.addCleanup(patcher.stop)
        self.sts = self.boto_client.return_value
        self.sts.assume_role.return_value = STS_RESPONSE
        self.client = self.client_class(REMOTE_ADDR='127.0.0.1')

    def post_as(self, user):
        login(self.client, user)
        return self.client.post(self.url)

    def test_anonymous_is_refused_without_calling_sts(self):
        resp = self.client.post(self.url)
        self.assertIn(resp.status_code, (401, 403))
        self.sts.assume_role.assert_not_called()

    def test_authenticated_user_without_access_is_refused(self):
        resp = self.post_as(make_user())
        self.assertEqual(resp.status_code, 403)
        self.sts.assume_role.assert_not_called()

    def test_staff_user_gets_credentials(self):
        resp = self.post_as(make_user(is_staff=True))
        self.assertEqual(resp.status_code, 200)
        body = resp.json()
        self.assertEqual(body['AccessKeyId'], 'ASIAEXAMPLE')
        self.assertEqual(body['SecretAccessKey'], 'secret')
        self.assertEqual(body['SessionToken'], 'token')
        self.assertTrue(body['Expiration'].startswith('2030-01-01'))

    def test_session_is_scoped_to_the_bucket(self):
        self.post_as(make_user(is_staff=True))
        kwargs = self.sts.assume_role.call_args.kwargs
        self.assertEqual(kwargs['RoleArn'], ROLE_ARN)
        self.assertEqual(kwargs['RoleSessionName'], 'S3StorageBrowserSession')
        self.assertEqual(kwargs['DurationSeconds'], 3600)
        policy = json.loads(kwargs['Policy'])
        resources = set()
        for statement in policy['Statement']:
            self.assertEqual(statement['Effect'], 'Allow')
            res = statement['Resource']
            resources.update([res] if isinstance(res, str) else res)
        self.assertEqual(
            resources,
            {f'arn:aws:s3:::{BUCKET}', f'arn:aws:s3:::{BUCKET}/*'})

    @override_settings(S3_STORAGE_BROWSER_SESSION_SECONDS=900)
    def test_session_duration_is_configurable(self):
        self.post_as(make_user(is_staff=True))
        self.assertEqual(
            self.sts.assume_role.call_args.kwargs['DurationSeconds'], 900)

    def test_package_permission_grants_access_without_staff(self):
        user = grant_package_permission(make_user())
        self.assertEqual(self.post_as(user).status_code, 200)

    def test_inactive_staff_user_is_refused(self):
        user = make_user(is_staff=True)
        login(self.client, user)
        user.is_active = False
        user.save()
        resp = self.client.post(self.url)
        self.assertIn(resp.status_code, (401, 403))
        self.sts.assume_role.assert_not_called()

    @override_settings(
        S3_STORAGE_BROWSER_ACCESS_CHECK='s3_storage_browser.tests.helpers.allow_all')
    def test_access_check_setting_can_grant(self):
        self.assertEqual(self.post_as(make_user()).status_code, 200)

    @override_settings(
        S3_STORAGE_BROWSER_ACCESS_CHECK='s3_storage_browser.tests.helpers.deny_all')
    def test_access_check_setting_can_deny_staff(self):
        resp = self.post_as(make_user(is_staff=True))
        self.assertEqual(resp.status_code, 403)
        self.sts.assume_role.assert_not_called()

    @override_settings(S3_STORAGE_BROWSER_ROLE_ARN=None)
    def test_missing_role_arn_is_a_server_error(self):
        with mock.patch.dict('os.environ', {}, clear=False) as env:
            env.pop('S3_STORAGE_BROWSER_ROLE_ARN', None)
            with self.assertLogs('s3_storage_browser', level='ERROR'):
                resp = self.post_as(make_user(is_staff=True))
        self.assertEqual(resp.status_code, 500)
        self.sts.assume_role.assert_not_called()

    @override_settings(S3_STORAGE_BROWSER_ROLE_ARN=None)
    def test_role_arn_falls_back_to_environment(self):
        with mock.patch.dict('os.environ', {'S3_STORAGE_BROWSER_ROLE_ARN': ROLE_ARN}):
            resp = self.post_as(make_user(is_staff=True))
        self.assertEqual(resp.status_code, 200)

    def test_sts_failure_does_not_leak_the_aws_error(self):
        self.sts.assume_role.side_effect = ClientError(
            {'Error': {'Code': 'AccessDenied',
                       'Message': f'User is not authorized to assume {ROLE_ARN}'}},
            'AssumeRole')
        with self.assertLogs('s3_storage_browser', level='ERROR'):
            resp = self.post_as(make_user(is_staff=True))
        self.assertEqual(resp.status_code, 502)
        self.assertNotIn(ROLE_ARN, resp.content.decode())
        self.assertNotIn('AccessDenied', resp.content.decode())
