import json
import logging
import os

import boto3
from django.conf import settings
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.http import JsonResponse
from django.shortcuts import render
from django.urls import NoReverseMatch, reverse
from django.utils.module_loading import import_string
from rest_framework import views

from .access import HasStorageBrowserAccess, has_access

logger = logging.getLogger(__name__)

DEFAULT_SESSION_SECONDS = 3600
DEFAULT_REGION = 'us-east-1'
DEFAULT_BASE_TEMPLATE = 's3_storage_browser/standalone.html'
LEGACY_CREDENTIALS_URL = '/api/awscreds/'


def _region():
    for name in ('S3_STORAGE_BROWSER_REGION', 'AWS_S3_REGION_NAME', 'AWS_REGION_NAME'):
        value = getattr(settings, name, None)
        if value:
            return value
    return DEFAULT_REGION


def _credentials_url():
    try:
        return reverse('s3_storage_browser:credentials')
    except NoReverseMatch:
        # Hosts that mount the views by hand (pre-0.2.0 README) serve the
        # API here.
        return LEGACY_CREDENTIALS_URL


def storage_browser_view(request, template_name='s3_storage_browser/index.html'):
    """
    The storage browser page.

    The page extends ``settings.S3_STORAGE_BROWSER_BASE_TEMPLATE`` (which must
    provide ``title`` and ``body`` blocks), and ``S3_STORAGE_BROWSER_EXTRA_CONTEXT``
    — a dotted path to ``callable(request) -> dict`` — adds host context such
    as a navigation menu.
    """
    if not request.user.is_authenticated:
        return redirect_to_login(request.get_full_path())
    if not has_access(request.user):
        raise PermissionDenied

    context = {
        's3_storage_browser_base_template': (
            getattr(settings, 'S3_STORAGE_BROWSER_BASE_TEMPLATE', None)
            or DEFAULT_BASE_TEMPLATE),
        's3_storage_browser_config': {
            'bucket': settings.AWS_STORAGE_BUCKET_NAME,
            'region': _region(),
            'credentialsUrl': _credentials_url(),
        },
    }
    extra_context = getattr(settings, 'S3_STORAGE_BROWSER_EXTRA_CONTEXT', None)
    if extra_context:
        context.update(import_string(extra_context)(request))
    return render(request, template_name, context)


def session_policy(bucket):
    """
    STS session policy limiting the assumed role to ``bucket``.

    A session policy can only narrow what the role already allows, so this
    is safe to send whatever the role's own policy says.
    """
    return json.dumps({
        'Version': '2012-10-17',
        'Statement': [
            {
                'Effect': 'Allow',
                'Action': ['s3:ListBucket', 's3:GetBucketLocation'],
                'Resource': f'arn:aws:s3:::{bucket}',
            },
            {
                'Effect': 'Allow',
                'Action': [
                    's3:GetObject',
                    's3:PutObject',
                    's3:DeleteObject',
                    's3:AbortMultipartUpload',
                    's3:ListMultipartUploadParts',
                ],
                'Resource': f'arn:aws:s3:::{bucket}/*',
            },
        ],
    })


def _role_arn():
    return (getattr(settings, 'S3_STORAGE_BROWSER_ROLE_ARN', None)
            or os.environ.get('S3_STORAGE_BROWSER_ROLE_ARN'))


class AwsCredentialsApiView(views.APIView):
    permission_classes = [HasStorageBrowserAccess]

    def post(self, request):
        role_arn = _role_arn()
        if not role_arn:
            logger.error('S3_STORAGE_BROWSER_ROLE_ARN is not set')
            return JsonResponse(
                {'message': 'Storage browser is not configured.'}, status=500)

        try:
            response = boto3.client('sts').assume_role(
                RoleArn=role_arn,
                RoleSessionName='S3StorageBrowserSession',
                DurationSeconds=getattr(
                    settings, 'S3_STORAGE_BROWSER_SESSION_SECONDS',
                    DEFAULT_SESSION_SECONDS),
                Policy=session_policy(settings.AWS_STORAGE_BUCKET_NAME),
            )
        except Exception:
            logger.exception('Could not assume the storage browser role')
            return JsonResponse(
                {'message': 'Could not obtain storage credentials.'}, status=502)

        return JsonResponse(response['Credentials'])
