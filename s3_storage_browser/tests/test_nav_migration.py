import importlib
import json
from unittest import mock, skipUnless

from django.apps import apps
from django.test import TestCase, override_settings
from django.urls import NoReverseMatch

nav = importlib.import_module('s3_storage_browser.migrations.0002_add_ce_nav')

SETTING_KEY = 'cis.settings.menu'
CE_MENU = [
    {'type': 'nav-item', 'icon': 'fas fa-fw fa-tachometer-alt',
     'name': 'dashboard', 'label': 'Dashboard', 'url': 'cis:dashboard'},
]
STUDENT_MENU = [
    {'type': 'nav-item', 'icon': 'fas fa-fw fa-home',
     'name': 'home', 'label': 'Home', 'url': 'student:dashboard'},
]


@skipUnless(apps.is_installed('cis'), 'nav migration targets the cis menu Setting')
@override_settings(ROOT_URLCONF='s3_storage_browser.tests.urls')
class AddCeNavMigrationTests(TestCase):

    def setUp(self):
        self.Setting = apps.get_model('cis', 'Setting')
        self.Campus = apps.get_model('cis', 'Campus')
        self.Setting.objects.filter(key=SETTING_KEY).delete()

    def seed(self, ce_menu=CE_MENU, campuses=0):
        value = {'ce_menu': json.dumps(ce_menu) if not isinstance(ce_menu, str) else ce_menu,
                 'student_menu': json.dumps(STUDENT_MENU)}
        rows = [self.Setting(key=SETTING_KEY, value=dict(value))]
        for n in range(campuses):
            campus = self.Campus.objects.create(name=f'Campus {n}', code=f'C{n}')
            rows.append(self.Setting(key=SETTING_KEY, value=dict(value), campus=campus))
        # bulk_create skips Setting.save()'s campus-context lookup
        self.Setting.objects.bulk_create(rows)

    def ce_menus(self):
        return [json.loads(s.value['ce_menu'])
                for s in self.Setting.objects.filter(key=SETTING_KEY)]

    def run_add(self):
        nav.add_nav(apps, None)

    def test_appends_the_entry_to_the_ce_menu(self):
        self.seed()
        self.run_add()
        [menu] = self.ce_menus()
        self.assertEqual(menu[-1], nav.NAV_ENTRY)
        self.assertEqual(menu[:-1], CE_MENU)

    def test_entry_points_at_the_namespaced_view(self):
        self.assertEqual(nav.NAV_ENTRY['url'], 's3_storage_browser:browser')
        self.assertEqual(nav.NAV_ENTRY['name'], 'storage_browser')

    def test_is_idempotent(self):
        self.seed()
        self.run_add()
        self.run_add()
        [menu] = self.ce_menus()
        self.assertEqual(
            [i['name'] for i in menu].count('storage_browser'), 1)

    def test_patches_every_campus_row(self):
        self.seed(campuses=2)
        self.run_add()
        menus = self.ce_menus()
        self.assertEqual(len(menus), 3)
        for menu in menus:
            self.assertEqual(
                [i['name'] for i in menu].count('storage_browser'), 1)

    def test_other_role_menus_are_untouched(self):
        self.seed()
        self.run_add()
        setting = self.Setting.objects.get(key=SETTING_KEY)
        self.assertEqual(json.loads(setting.value['student_menu']), STUDENT_MENU)

    def test_unparseable_ce_menu_is_left_alone(self):
        self.seed(ce_menu='not json')
        self.run_add()
        setting = self.Setting.objects.get(key=SETTING_KEY)
        self.assertEqual(setting.value['ce_menu'], 'not json')

    def test_missing_setting_is_a_no_op(self):
        self.run_add()
        self.assertFalse(self.Setting.objects.filter(key=SETTING_KEY).exists())

    def test_skipped_when_the_host_has_not_mounted_the_urls(self):
        # draw_menu leaves a half-built <a> when reverse() fails, which
        # would corrupt the whole sidebar.
        self.seed()
        with mock.patch.object(nav, 'reverse', side_effect=NoReverseMatch):
            self.run_add()
        [menu] = self.ce_menus()
        self.assertEqual(menu, CE_MENU)

    def test_remove_reverses_add(self):
        self.seed()
        self.run_add()
        nav.remove_nav(apps, None)
        [menu] = self.ce_menus()
        self.assertEqual(menu, CE_MENU)
