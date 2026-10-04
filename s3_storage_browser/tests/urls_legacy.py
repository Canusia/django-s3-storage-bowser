"""A host that mounts the view by hand, as tenants did before v0.2.0."""
from django.urls import path

from s3_storage_browser.views import storage_browser_view

urlpatterns = [
    path('ce/storagebrowser/', storage_browser_view, name='storage_browser'),
]
