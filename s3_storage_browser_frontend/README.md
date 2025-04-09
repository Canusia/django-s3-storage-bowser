# Storage Browser

A React application for browsing S3 storage, built with Vite.

## Development

```bash
npm run dev
```

## Building for Production

To build the application for production, use:

```bash
npm run build:deploy
```

This will:
1. Build the React application using Vite
2. Output the HTML file to `../s3_storage_browser/templates/s3_storage_browser/`
3. Output the JS and CSS files to `../s3_storage_browser/templates/assets/` with consistent filenames (no hashes)
4. Move the JS and CSS files from `../s3_storage_browser/templates/assets/` to `../s3_storage_browser/static/`
5. Automatically update the HTML file to use Django's static template tags

## Configuration

The build configuration is defined in `vite.config.ts`. It is set up to:

- Output the HTML file to `../s3_storage_browser/templates/s3_storage_browser/`
- Generate JS and CSS files with consistent names (no content hashes)
- Initially output JS and CSS files to `../s3_storage_browser/templates/assets/`
- The `move-assets.js` script then moves these files to `../s3_storage_browser/static/`
- A custom Vite plugin (`djangoTemplatePlugin`) automatically updates the HTML file to use Django's static template tags

## Integration with Django

The application is integrated with Django:

1. The HTML template uses Django's `{% load static %}` and `{% static '...' %}` tags to reference the static files
2. The static files are served by Django's static file handling

## Browser Caching

Since we're not using content hashes for cache busting, browsers might cache old versions of your files. During development and after deployments, you may need to:

1. Use browser hard refresh (Ctrl+F5 or Cmd+Shift+R)
2. Add a query parameter to force a refresh in production (e.g., `?v=1.0.1`)
3. Configure appropriate cache headers on your server
