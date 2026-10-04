# Django S3 Storage Browser

`ah-django-s3-storage-browser` is a Django app that serves the AWS Amplify
Storage Browser for one S3 bucket. The browser talks to S3 directly with
short-lived credentials that a Django endpoint mints by assuming an IAM role,
scoped to that bucket.

## Installation

Pin a tag in `requirements.txt` — `main` moves:

```
git+https://github.com/Canusia/django-s3-storage-bowser.git@v0.2.0
```

```python
INSTALLED_APPS = [
    # ...
    's3_storage_browser',
]
```

```python
# urls.py
from django.urls import include, path

urlpatterns = [
    # ...
    path('ce/storagebrowser/', include('s3_storage_browser.urls')),
]
```

This mounts the page at `ce/storagebrowser/` (`s3_storage_browser:browser`) and
the credentials API at `ce/storagebrowser/credentials/`
(`s3_storage_browser:credentials`). The page finds the API by URL name.

```bash
python manage.py migrate
python manage.py collectstatic
```

## Settings

| Setting | Default | Purpose |
|---|---|---|
| `AWS_STORAGE_BUCKET_NAME` | — (required) | Bucket the browser shows |
| `S3_STORAGE_BROWSER_ROLE_ARN` | env var of the same name | IAM role assumed for browser credentials |
| `S3_STORAGE_BROWSER_SESSION_SECONDS` | `3600` | STS session length |
| `S3_STORAGE_BROWSER_REGION` | `AWS_S3_REGION_NAME`, then `AWS_REGION_NAME`, then `us-east-1` | Bucket region |
| `S3_STORAGE_BROWSER_ACCESS_CHECK` | active staff, or the `can_access_s3_storage_browser` permission | Dotted path to `callable(user) -> bool` gating the page **and** the API |
| `S3_STORAGE_BROWSER_BASE_TEMPLATE` | `s3_storage_browser/standalone.html` | Template the page extends |
| `S3_STORAGE_BROWSER_EXTRA_CONTEXT` | none | Dotted path to `callable(request) -> dict` merged into the page context |

### Rendering inside your site's layout

`s3_storage_browser/index.html` extends `S3_STORAGE_BROWSER_BASE_TEMPLATE`
and fills two blocks, so the base must define both:

- `{% block title %}`
- `{% block body %}`

Anything your base template needs — a navigation menu, say — comes from
`S3_STORAGE_BROWSER_EXTRA_CONTEXT`. To place the browser inside a page of your
own instead, `{% include "s3_storage_browser/_app.html" %}` with
`s3_storage_browser_config` in the context.

### MyCE hosts

```python
# settings.py
S3_STORAGE_BROWSER_ACCESS_CHECK = 'cis.utils.user_has_cis_role'
S3_STORAGE_BROWSER_BASE_TEMPLATE = 'cis/logged-base.html'
S3_STORAGE_BROWSER_EXTRA_CONTEXT = 'myce_tenant_configs.services.storage_browser.storage_browser_context'
```

```python
# myce_tenant_configs/services/storage_browser.py
from cis.menu import cis_menu, draw_menu


def storage_browser_context(request):
    return {'menu': draw_menu(cis_menu, 'storage_browser')}
```

Migration `0002_add_ce_nav` adds a **File Storage** item to the CE menu
(`cis.settings.menu`, every campus row). It runs only when `cis` is installed
and `s3_storage_browser:browser` resolves — so include the URLs **before**
migrating. If it was skipped, add the item in the menu setting by hand:

```json
{"type": "nav-item", "icon": "fas fa-fw fa-folder-open", "name": "storage_browser", "label": "File Storage", "url": "s3_storage_browser:browser"}
```

## Credentials API

`POST` to `s3_storage_browser:credentials` (session + CSRF) returns the STS
credentials:

```json
{"AccessKeyId": "ASIA...", "SecretAccessKey": "...", "SessionToken": "...", "Expiration": "2026-01-01T12:00:00Z"}
```

The session policy allows only `s3:ListBucket`/`s3:GetBucketLocation` on the
bucket and `s3:GetObject`/`PutObject`/`DeleteObject`/`AbortMultipartUpload`/
`ListMultipartUploadParts` on its objects. A session policy can only narrow
the role, never widen it. Callers who fail the access check get 403; AWS
errors are logged and returned as a generic 502.

## Upgrading from 0.1

- Static assets moved to `static/s3_storage_browser/`; run `collectstatic`.
- The page is no longer `@staff_member_required`: unauthenticated users go to
  `LOGIN_URL`, others failing the access check get 403. The default check
  still admits staff.
- The credentials API now applies the same check (it previously admitted any
  authenticated user).
- Hosts that mount `storage_browser_view` and `AwsCredentialsApiView` by hand
  at `/api/awscreds/` keep working; `include('s3_storage_browser.urls')` is
  preferred.

## Development

```bash
cd s3_storage_browser_frontend
npm ci
npm run build      # tsc + vite → ../s3_storage_browser/static/s3_storage_browser/
npm run dev        # standalone dev server (config in index.html)
```

Django tests run inside a host project that installs the app:

```bash
python manage.py test s3_storage_browser
```

## License

BSD.
