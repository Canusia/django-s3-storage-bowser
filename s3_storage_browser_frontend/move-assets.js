import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = path.dirname(__filename);

// Define paths
const assetsDir = path.resolve(__dirname, '../s3_storage_browser/templates/s3_storage_browser/assets');
const staticDir = path.resolve(__dirname, '../s3_storage_browser/static');

// Create static directory if it doesn't exist
if (!fs.existsSync(staticDir)) {
  fs.mkdirSync(staticDir, { recursive: true });
}

// Move all files from assets to static
if (fs.existsSync(assetsDir)) {
  const files = fs.readdirSync(assetsDir);
  files.forEach(file => {
    const oldPath = path.join(assetsDir, file);
    const newPath = path.join(staticDir, file);
    fs.renameSync(oldPath, newPath);
    console.log(`Moved ${file} to static directory`);
  });

  // Remove the assets directory
  fs.rmdirSync(assetsDir);
  console.log('Removed assets directory');
} else {
  console.log('Assets directory does not exist');
}

console.log('Assets moved successfully!');
