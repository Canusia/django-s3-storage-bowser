
============
ah-django-s3-storage-browser
============

ah-django-s3-storage-browser is a Django app to display a S3 storage browser.
Works via AWS session credentials that are fetched via a backend API.

Quick start
-----------

1. Add "ah-s3-storage-browser" to your INSTALLED_APPS setting like this::

    INSTALLED_APPS = [
        ...,
        "ah-django-s3-storage-browser",
    ]

2. Include the ah-s3-storage-browser URLconf in your project urls.py like this::

    path("storagebrowser/", include("ah-s3-storage-s3-browser.storage_browser_view")),

3. Run ``python manage.py migrate`` to create the models.

4. Start the development server and visit the the ``/storagebrowser/`` URL to view the S3 storage browser.
