import { useState, useEffect } from 'react';
import { Amplify } from 'aws-amplify';
import '@aws-amplify/ui-react/styles.css';
import '@aws-amplify/ui-react-storage/styles.css';
import {
  createStorageBrowser,
} from '@aws-amplify/ui-react-storage/browser';

interface Credentials {
  accessKeyId: string;
  secretAccessKey: string;
  sessionToken: string;
  expiration: Date;
};

const BUCKET_NAME = (window as any).STORAGE_BROWSER_S3_BUCKET_NAME as string;

// Configure Amplify
Amplify.configure({
  Storage: {
    S3: {
      bucket: BUCKET_NAME, // S3 bucket name
      region: 'us-east-1', // AWS region
    },
  },
});

// Helper function to get CSRF token
const getCookie = (name: string) => {
  let cookieValue = null;
  if (document.cookie && document.cookie !== '') {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
      const cookie = cookies[i].trim();
      if (cookie.substring(0, name.length + 1) === (name + '=')) {
        cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
        break;
      }
    }
  }
  return cookieValue;
}

// Custom auth provider for Amplify
const customAuthProvider = {
  // Get credentials from Django backend
  async getCredentials() {
    try {
      const response = await fetch('/api/awscreds/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRFToken': getCookie('csrftoken') || '',
        },
      });
      
      if (!response.ok) {
        throw new Error('Failed to get AWS credentials');
      }
      
      const credentials = await response.json();
      
      return {
        accessKeyId: credentials.AccessKeyId,
        secretAccessKey: credentials.SecretAccessKey,
        sessionToken: credentials.SessionToken,
        expiration: new Date(credentials.Expiration)
      };
    } catch (error) {
      console.error('Error getting credentials:', error);
      throw error;
    }
  }
};

const App = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [error, setError] = useState('');
  const [credentials, setCredentials] = useState<Credentials | undefined>();

  useEffect(() => {
    const fetchCredentials = async () => {
      try {
        const credentials = await customAuthProvider.getCredentials();
        setIsAuthenticated(true);
        setCredentials(credentials as Credentials);
        setError('');
      } catch (error) {
        setCredentials(undefined);
        setIsAuthenticated(false);
        setError('Failed to authenticate with AWS. Please check your credentials.');
      }
    };

    fetchCredentials();
  }, []);

  if (!credentials) {
    return <div>Loading...</div>;
  }

  const { StorageBrowser } = createStorageBrowser({
    credentials,
    bucket: BUCKET_NAME,
    config: {
      listLocations: async (input = {}) => {
        const { } = input;
        return {
          items: [{
            bucket: BUCKET_NAME as string,
            prefix: '',
            id: '1',
            key: '', 
            region: 'us-east-1',
            type: 'BUCKET',
            permissions: ['get', 'list', 'write', 'delete'],
            scope: `s3://${BUCKET_NAME}`,
          }],
          nextToken: '',
        }
      },
      getLocationCredentials: async ({ }) => {
        return {
          credentials: credentials as any,
        };
      },
      region: 'us-east-1',
      registerAuthListener: (_) => {
        
      }
    },
 });

  return (
    <div className="s3-browser-container">
      <h1>S3 Storage Browser</h1>
      {error && <div className="error-message">{error}</div>}
      {isAuthenticated ? (
        <StorageBrowser />
      ) : (
        <p>Loading credentials...</p>
      )}
    </div>
  );
};

export default App;
