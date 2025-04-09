
from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render


@staff_member_required
def storage_browser_view(request):
    '''
    Returns view for S3 storage browser
    '''
    context = {
        'storage_browser_s3_bucket_name': settings.AWS_STORAGE_BUCKET_NAME
    }
    return render(request, 's3_storage_browser/index.html', context)
