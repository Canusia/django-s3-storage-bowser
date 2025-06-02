
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
            client = boto3.client('sts')
            response = client.get_session_token()
            return JsonResponse(response['Credentials'])
        except Exception as e:
            msg = {"message": str(e)}
            return JsonResponse(msg, status=500)
