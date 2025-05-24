from django.conf import settings
from django.db import migrations
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType


def create_s3_browser_permission(apps, schema_editor):
	content_type, created = ContentType.objects.get_or_create(
		app_label='s3_storage_browser', model='globalpermission'
	)
	permission, created = Permission.objects.get_or_create(
		codename='can_access_s3_storage_browser',
		name='Can access the S3 storage browser UI',
		content_type=content_type,
	)

class Migration(migrations.Migration):

    dependencies = [
		migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(create_s3_browser_permission),
    ]
