# Django S3 Storage Browser

`ah-django-s3-storage-browser` is a Django app that provides S3 storage browser functionality with AWS session credentials management. It includes both a storage browser view and an API endpoint for fetching AWS credentials.

## Features

- **Storage Browser View**: A web interface for browsing S3 storage
- **AWS Credentials API**: RESTful API endpoint for obtaining temporary AWS session tokens
- **Permission Management**: Built-in Django permissions for controlling access
- **Easy Integration**: Simple setup for existing Django projects

## Installation

### Option 1: Install from Git Repository

Add the following line to your `requirements.txt`:

```
git+https://github.com/Canusia/django-s3-storage-bowser.git
```

Then install:

```bash
pip install -r requirements.txt
```

### Option 2: Development Installation

For local development, clone the repository and install in editable mode:

```bash
git clone https://github.com/Canusia/django-s3-storage-bowser.git
pip install -e ./django-s3-storage-bowser
```

## Quick Start

### 1. Add to INSTALLED_APPS

Add `s3_storage_browser` to your Django project's `INSTALLED_APPS` setting:

```python
INSTALLED_APPS = [
    # ... your other apps
    's3_storage_browser',
]
```

### 2. Configure URLs

#### For Storage Browser View

Include the storage browser view in your project's `urls.py`:

```python
from django.urls import path, include
from s3_storage_browser.views import storage_browser_view

urlpatterns = [
    # ... your other URL patterns
    path('admin/storagebrowser/', 
         storage_browser_view, 
         {'template_name': 'admin/storage_browser.html'},
         name='storage_browser_admin'),
]
```

#### For AWS Credentials API

Add the API endpoint for AWS credentials:

```python
from django.urls import path
from s3_storage_browser.views import AwsCredentialsApiView

urlpatterns = [
    # ... your other URL patterns
    path('api/awscreds/', AwsCredentialsApiView.as_view()),
]
```

### 3. Environment Variables

Set the required AWS environment variables:

```bash
export AWS_ACCESS_KEY_ID=your_access_key_id
export AWS_SECRET_ACCESS_KEY=your_secret_access_key
```

### 4. Django Settings

Configure your Django settings with the required AWS settings:

```python
# AWS Configuration
AWS_STORAGE_BUCKET_NAME = 'your-s3-bucket-name'
AWS_REGION_NAME = 'us-east-1'  # or your preferred region
```

### 5. Run Migrations

Apply the database migrations to create the necessary permissions:

```bash
python manage.py migrate
```

## Usage

### Storage Browser View

The storage browser view provides a web interface for browsing S3 storage. It requires staff member permissions and uses the configured S3 bucket.

**URL**: `/admin/storagebrowser/`
**Permission**: Staff member required (`@staff_member_required` decorator)

### AWS Credentials API

The API endpoint provides temporary AWS session tokens for client-side S3 operations.

**Endpoint**: `POST /api/awscreds/`
**Authentication**: Requires authenticated user
**Response**: JSON object containing temporary AWS credentials

Example response:
```json
{
  "AccessKeyId": "ASIA...",
  "SecretAccessKey": "...",
  "SessionToken": "...",
  "Expiration": "2024-01-01T12:00:00Z"
}
```

### Permissions

The app creates a custom permission: `can_access_s3_storage_browser`

You can assign this permission to users or groups through the Django admin interface or programmatically:

```python
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType

# Get the permission
content_type = ContentType.objects.get(app_label='s3_storage_browser', model='globalpermission')
permission = Permission.objects.get(
    codename='can_access_s3_storage_browser',
    content_type=content_type
)

# Assign to a user
user.user_permissions.add(permission)
```

## Configuration Options

### Template Customization

You can customize the storage browser template by overriding the default template:

```python
# In your URL configuration
path('admin/storagebrowser/', 
     storage_browser_view, 
     {'template_name': 'your_custom_template.html'},
     name='storage_browser_admin'),
```

### AWS Session Token Settings

The AWS credentials API uses the default AWS STS settings. You can customize the session duration and other parameters by modifying the `AwsCredentialsApiView` class.

## Security Considerations

1. **Environment Variables**: Always use environment variables for AWS credentials, never hardcode them
2. **Permissions**: Use Django's permission system to control access to the storage browser
3. **HTTPS**: Always use HTTPS in production when transmitting AWS credentials
4. **Session Tokens**: The API returns temporary session tokens with limited lifetime for security

## Troubleshooting

### Common Issues

1. **Missing AWS Credentials**: Ensure `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set
2. **Permission Denied**: Check that users have the required permissions
3. **Template Not Found**: Verify template paths and ensure templates are in the correct location

### Error Messages

- `AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY not set in environment variables`: Set the required environment variables
- `Permission denied`: User lacks the required permissions to access the storage browser

## Dependencies

- Django >= 4.2
- boto3
- djangorestframework

## License

This project is licensed under the BSD License.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Support

For issues and questions, please use the GitHub issue tracker.
