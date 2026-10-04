from django.urls import include, path

urlpatterns = [
    path('storagebrowser/', include('s3_storage_browser.urls')),
]
