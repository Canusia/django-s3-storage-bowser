from django.urls import include, path

from s3_storage_browser.views import storage_browser_view

urlpatterns = [
    path('storagebrowser/', include('s3_storage_browser.urls')),
    path('custom/', storage_browser_view,
         {'template_name': 's3b_tests/custom.html'}),
]
