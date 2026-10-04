export interface Credentials {
  accessKeyId: string;
  secretAccessKey: string;
  sessionToken: string;
  expiration: Date;
}

// Refetch this long before the server-reported expiry.
const REFRESH_MARGIN_MS = 5 * 60 * 1000;

/**
 * Returns a function that yields valid credentials from the Django endpoint,
 * reusing the last set until it is about to expire.
 */
export const createCredentialsProvider = (credentialsUrl: string, csrfToken: string) => {
  let cached: Credentials | undefined;
  let inFlight: Promise<Credentials> | undefined;

  const fetchCredentials = async (): Promise<Credentials> => {
    const response = await fetch(credentialsUrl, {
      method: 'POST',
      credentials: 'same-origin',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': csrfToken,
      },
    });
    if (!response.ok) {
      throw new Error(`Credentials request failed (HTTP ${response.status})`);
    }
    const body = await response.json();
    return {
      accessKeyId: body.AccessKeyId,
      secretAccessKey: body.SecretAccessKey,
      sessionToken: body.SessionToken,
      expiration: new Date(body.Expiration),
    };
  };

  return async (): Promise<Credentials> => {
    if (cached && cached.expiration.getTime() - Date.now() > REFRESH_MARGIN_MS) {
      return cached;
    }
    inFlight ??= fetchCredentials()
      .then((credentials) => (cached = credentials))
      .finally(() => (inFlight = undefined));
    return inFlight;
  };
};
