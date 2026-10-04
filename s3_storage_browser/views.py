import json
import logging
import os

import boto3
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.shortcuts import render
from rest_framework import views

from .access import HasStorageBrowserAccess

logger = logging.getLogger(__name__)

DEFAULT_SESSION_SECONDS = 3600


@staff_member_required
def storage_browser_view(request):
    '''
    Returns view for S3 storage browser
    '''
    context = {
        'storage_browser_s3_bucket_name': settings.AWS_STORAGE_BUCKET_NAME
    }
    return render(request, 's3_storage_browser/index.html', context)


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
