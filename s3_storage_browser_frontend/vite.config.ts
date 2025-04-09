import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import { readFileSync, writeFileSync } from 'fs'
import { resolve } from 'path'

// Custom plugin to modify the generated HTML file
const djangoTemplatePlugin = () => {
  return {
    name: 'django-template-plugin',
    closeBundle: () => {
      // Path to the generated HTML file
      const htmlPath = resolve(__dirname, '../s3_storage_browser/templates/s3_storage_browser/index.html');

      // Read the generated HTML file
      let html = readFileSync(htmlPath, 'utf-8');

      // Load Django static template tags
      html = `{% extends "admin/base_site.html" %}\n\n{% load static %}\n\n{% block content %}\n${html}\n{% endblock %}\n`;

      // Inject the Django environment variable script before the first <script> tag with proper indentation
      const envScript = `
    <script>
        window.STORAGE_BROWSER_S3_BUCKET_NAME = "{{ storage_browser_s3_bucket_name|escapejs }}";
    </script>`;

      // Ensure the script appears before the first `<script>` tag with correct spacing
      html = html.replace(/(\s*)<script.*?>/, `$1${envScript}$1$&`);

      // Replace asset references with Django static template tags
      html = html.replace(/src="\/assets\/(.*?)"/g, 'src="{% static \'$1\' %}"');
      html = html.replace(/href="\/assets\/(.*?)"/g, 'href="{% static \'$1\' %}"');
      html = html.replace(/href="\/vite.svg"/g, 'href="{% static \'favicon.ico\' %}"');

      // Write the modified HTML file
      writeFileSync(htmlPath, html);
      console.log('HTML file updated with Django template tags and correct script indentation');
    },
  };
};

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    react(),
    djangoTemplatePlugin(),
  ],
  build: {
    outDir: '../s3_storage_browser/templates/s3_storage_browser',
    emptyOutDir: true,
    rollupOptions: {
      output: {
        // single chunk output to simplify inlining
        manualChunks: undefined,
        // Place all assets (JS, CSS) in the static directory with fixed names
        assetFileNames: 'assets/[name][extname]',
        // Place JS entry points in the static directory with fixed names
        entryFileNames: 'assets/[name].js',
        // Keep HTML files in the templates directory
        chunkFileNames: 'assets/[name].js'
      },
    },
  },
});
