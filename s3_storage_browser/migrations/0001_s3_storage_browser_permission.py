from django.db import migrations


def create_s3_browser_permission(apps, schema_editor):
    ContentType = apps.get_model('contenttypes', 'ContentType')
    Permission = apps.get_model('auth', 'Permission')

    content_type, _ = ContentType.objects.get_or_create(
        app_label='s3_storage_browser', model='globalpermission'
    )
    Permission.objects.get_or_create(
        codename='can_access_s3_storage_browser',
        content_type=content_type,
        defaults={'name': 'Can access the S3 storage browser UI'},
    )


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '__first__'),
        ('auth', '__first__'),
    ]

    operations = [
        migrations.RunPython(create_s3_browser_permission, migrations.RunPython.noop),
    ]
