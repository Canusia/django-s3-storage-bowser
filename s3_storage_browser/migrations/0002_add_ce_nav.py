"""
Add a "File Storage" item to the CE portal menu of MyCE hosts.

The MyCE sidebar is drawn from the ``cis.settings.menu`` Setting, so this
patches every row of it (one per campus on multi-campus deployments).

Skipped entirely when:
- ``cis`` is not installed (not a MyCE host);
- the host has not mounted ``s3_storage_browser.urls`` — cis's draw_menu
  emits a half-built <a> when reverse() fails, which breaks the sidebar;
- no menu Setting exists yet (fresh install; add the item in the UI).

Idempotent; reversed by removing the item by name.
"""
import json

from django.apps import apps as global_apps
from django.db import migrations
from django.urls import NoReverseMatch, reverse

SETTING_KEY = 'cis.settings.menu'
ROLE_KEY = 'ce_menu'

NAV_ENTRY = {
    'type': 'nav-item',
    'icon': 'fas fa-fw fa-folder-open',
    'name': 'storage_browser',
    'label': 'File Storage',
    'url': 's3_storage_browser:browser',
}


def _menu_settings(apps):
    try:
        Setting = apps.get_model('cis', 'Setting')
    except LookupError:
        return []
    return list(Setting.objects.filter(key=SETTING_KEY))


def _patch(setting, change):
    raw = (setting.value or {}).get(ROLE_KEY)
    try:
        items = json.loads(raw)
    except (TypeError, ValueError):
        return
    if not isinstance(items, list):
        return
    new_items = change(items)
    if new_items is not items:
        setting.value[ROLE_KEY] = json.dumps(new_items)
        setting.save(update_fields=['value'])


def add_nav(apps, schema_editor):
    try:
        reverse(NAV_ENTRY['url'])
    except NoReverseMatch:
        return

    def add(items):
        if any(i.get('name') == NAV_ENTRY['name'] for i in items):
            return items
        return [*items, dict(NAV_ENTRY)]

    for setting in _menu_settings(apps):
        _patch(setting, add)


def remove_nav(apps, schema_editor):
    def remove(items):
        if not any(i.get('name') == NAV_ENTRY['name'] for i in items):
            return items
        return [i for i in items if i.get('name') != NAV_ENTRY['name']]

    for setting in _menu_settings(apps):
        _patch(setting, remove)


class Migration(migrations.Migration):

    dependencies = [
        ('s3_storage_browser', '0001_s3_storage_browser_permission'),
    ] + ([('cis', '__first__')] if global_apps.is_installed('cis') else [])

    operations = [
        migrations.RunPython(add_nav, remove_nav),
    ]
