// Server-rendered by s3_storage_browser/_app.html via Django's json_script.
export interface StorageBrowserPageConfig {
  bucket: string;
  region: string;
  credentialsUrl: string;
  csrfToken: string;
}

const CONFIG_ELEMENT_ID = 's3-storage-browser-config';

export const readConfig = (): StorageBrowserPageConfig => {
  const element = document.getElementById(CONFIG_ELEMENT_ID);
  if (!element?.textContent) {
    throw new Error(`#${CONFIG_ELEMENT_ID} is missing from the page`);
  }
  return JSON.parse(element.textContent) as StorageBrowserPageConfig;
};
