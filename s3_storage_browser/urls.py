from django.urls import path

from .views import AwsCredentialsApiView, storage_browser_view

app_name = 's3_storage_browser'

urlpatterns = [
    path('', storage_browser_view, name='browser'),
    path('credentials/', AwsCredentialsApiView.as_view(), name='credentials'),
]
