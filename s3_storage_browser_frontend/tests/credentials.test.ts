import { afterEach, describe, expect, it, vi } from 'vitest';

import { createCredentialsProvider, readCookie } from '../src/credentials';

const HOUR = 60 * 60 * 1000;

const credentialsBody = (expiresInMs: number) => ({
  AccessKeyId: 'AKIA',
  SecretAccessKey: 'secret',
  SessionToken: 'token',
  Expiration: new Date(Date.now() + expiresInMs).toISOString(),
});

const stubFetch = (expiresInMs = HOUR) => {
  const fetch = vi.fn(async () => new Response(JSON.stringify(credentialsBody(expiresInMs))));
  vi.stubGlobal('fetch', fetch);
  return fetch;
};

const sentCsrfToken = (fetch: ReturnType<typeof stubFetch>, call = 0) =>
  (fetch.mock.calls[call] as unknown as [string, RequestInit])[1].headers as Record<string, string>;

afterEach(() => vi.unstubAllGlobals());

describe('readCookie', () => {
  it('returns the decoded value of the named cookie', () => {
    expect(readCookie('a=1; ewu_csrftoken=abc%3D; b=2', 'ewu_csrftoken')).toBe('abc=');
  });

  it('does not match a cookie whose name merely ends with the name', () => {
    expect(readCookie('xcsrftoken=nope', 'csrftoken')).toBeNull();
  });

  it('returns null when the cookie is absent', () => {
    expect(readCookie('', 'csrftoken')).toBeNull();
  });
});

describe('createCredentialsProvider CSRF header', () => {
  it('sends the current cookie value, so a token rotated after page load still works', async () => {
    const fetch = stubFetch();
    vi.stubGlobal('document', { cookie: 'ewu_csrftoken=rotated' });
    const get = createCredentialsProvider({
      credentialsUrl: '/creds/', csrfToken: 'from-page', csrfCookieName: 'ewu_csrftoken',
    });
    await get();
    expect(sentCsrfToken(fetch)['X-CSRFToken']).toBe('rotated');
  });

  it('falls back to the page token when the cookie is missing', async () => {
    const fetch = stubFetch();
    vi.stubGlobal('document', { cookie: '' });
    const get = createCredentialsProvider({
      credentialsUrl: '/creds/', csrfToken: 'from-page', csrfCookieName: 'ewu_csrftoken',
    });
    await get();
    expect(sentCsrfToken(fetch)['X-CSRFToken']).toBe('from-page');
  });

  it('uses the page token when the cookie is not readable by JavaScript', async () => {
    const fetch = stubFetch();
    vi.stubGlobal('document', { cookie: 'csrftoken=ignored' });
    const get = createCredentialsProvider({
      credentialsUrl: '/creds/', csrfToken: 'from-page', csrfCookieName: null,
    });
    await get();
    expect(sentCsrfToken(fetch)['X-CSRFToken']).toBe('from-page');
  });
});

describe('createCredentialsProvider caching', () => {
  const options = { credentialsUrl: '/creds/', csrfToken: 't', csrfCookieName: null };

  it('reuses credentials that are not close to expiry', async () => {
    const fetch = stubFetch(HOUR);
    const get = createCredentialsProvider(options);
    await get();
    await get();
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('refetches credentials that expire within five minutes', async () => {
    const fetch = stubFetch(60 * 1000);
    const get = createCredentialsProvider(options);
    await get();
    await get();
    expect(fetch).toHaveBeenCalledTimes(2);
  });

  it('shares one request between concurrent callers', async () => {
    const fetch = stubFetch(HOUR);
    const get = createCredentialsProvider(options);
    await Promise.all([get(), get(), get()]);
    expect(fetch).toHaveBeenCalledTimes(1);
  });

  it('rejects when the endpoint refuses', async () => {
    vi.stubGlobal('fetch', vi.fn(async () => new Response('{}', { status: 403 })));
    const get = createCredentialsProvider(options);
    await expect(get()).rejects.toThrow('HTTP 403');
  });
});
