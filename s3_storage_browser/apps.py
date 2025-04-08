from django.apps import AppConfig


class StorageBrowserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 's3_storage_browser'
    verbose_name = "AppHammer S3 Storage Browser"