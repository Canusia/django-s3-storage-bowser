from django.apps import AppConfig


class StorageBrowserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'ah-django-s3-storage-browser'
    label = 'ah-s3-storage-browser'
