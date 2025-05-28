
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
        print('request', request)
        if getattr(settings, 'DEBUG', True):
            access_key = os.environ.get('AWS_ACCESS_KEY_ID',None)
            secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY',None)
            if not access_key or not secret_key:
                return JsonResponse({'error': 'AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY not set in environment variables'}, status=500)
        
        client = boto3.client('sts')
        response = client.get_session_token()
        return JsonResponse(response['Credentials'])
