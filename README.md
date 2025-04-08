
## ah-django-s3-storage-browser

ah-django-s3-storage-browser is a Django app to display a S3 storage browser.
Works via AWS session credentials that are fetched via a backend API.

Quick start
-----------

1. Add `s3_storage_browser` to your `INSTALLED_APPS` setting like this::
```
    INSTALLED_APPS = [
        ...,
        "s3_storage_browser.apps.StorageBrowserConfig",
    ]
```

2. Include the `s3_storage_browser` URLconf in your project `urls.py` like this::

```
    path("storagebrowser/", include("s3_storage_browser.views.storage_browser_view")),
```

3. Start the development server and visit the the ``/storagebrowser/`` URL to view the S3 storage browser.
