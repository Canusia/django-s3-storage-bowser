import { useEffect, useState } from 'react';
import '@aws-amplify/ui-react/styles.css';
import '@aws-amplify/ui-react-storage/styles.css';
import { createStorageBrowser } from '@aws-amplify/ui-react-storage/browser';

import { readConfig } from './config';
import { createCredentialsProvider } from './credentials';

const CONFIG = readConfig();
const getCredentials = createCredentialsProvider(CONFIG);

// Created once: building it inside render would remount the browser (and
// drop its navigation state) on every re-render.
const { StorageBrowser } = createStorageBrowser({
  config: {
    region: CONFIG.region,
    listLocations: async () => ({
      items: [{
        bucket: CONFIG.bucket,
        prefix: '',
        id: CONFIG.bucket,
        type: 'BUCKET',
        permissions: ['get', 'list', 'write', 'delete'],
      }],
      nextToken: undefined,
    }),
    // The browser caches these per location and calls back on expiry.
    getLocationCredentials: async () => ({ credentials: await getCredentials() }),
    registerAuthListener: () => {},
  },
});

type Status = 'loading' | 'ready' | 'error';

const App = () => {
  const [status, setStatus] = useState<Status>('loading');

  useEffect(() => {
    getCredentials()
      .then(() => setStatus('ready'))
      .catch((error) => {
        console.error('Storage browser credentials:', error);
        setStatus('error');
      });
  }, []);

  if (status === 'error') {
    return (
      <div className="alert alert-danger" role="alert">
        Could not connect to file storage. Reload the page to try again; if
        it keeps failing, contact your administrator.
      </div>
    );
  }
  if (status === 'loading') {
    return <p>Loading file storage…</p>;
  }
  return <StorageBrowser />;
};

export default App;
