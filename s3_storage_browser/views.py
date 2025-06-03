
from django.http import JsonResponse
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render
import os
import boto3

from rest_framework import views


@staff_member_required
def storage_browser_view(request):
    '''
    Returns view for S3 storage browser
    '''
    context = {
        'storage_browser_s3_bucket_name': settings.AWS_STORAGE_BUCKET_NAME
    }
    return render(request, 's3_storage_browser/index.html', context)


class AwsCredentialsApiView(views.APIView):
    def post(self, request):
        try:
            # Get role ARN from environment variable
            role_arn = os.environ.get('S3_STORAGE_BROWSER_ROLE_ARN')
            if not role_arn:
                return JsonResponse(
                    {"message": "S3_STORAGE_BROWSER_ROLE_ARN environment variable not set"}, 
                    status=500
                )
            
            # Create STS client and assume role
            client = boto3.client('sts')
            response = client.assume_role(
                RoleArn=role_arn,
                RoleSessionName='S3StorageBrowserSession'
            )
            
            return JsonResponse(response['Credentials'])
        except Exception as e:
            msg = {"message": str(e)}
            return JsonResponse(msg, status=500)
