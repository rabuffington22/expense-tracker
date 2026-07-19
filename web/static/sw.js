/*
 * The Ledger — Service Worker
 *
 * Strategy:
 *   - Static assets (CSS, JS, icons, images): Cache-first, fall back to network
 *   - HTML navigations: Network-only, fall back to the generic offline page
 *   - Dynamic/HTMX/API routes: Network-only; never retain protected content
 *   - Offline fallback: Simple branded page when nothing is available
 */

const CACHE_NAME = 'the-ledger-v4';
const OFFLINE_URL = '/offline';

// App shell and static assets to pre-cache on install
const PRECACHE_URLS = [
  '/offline',
  '/static/style.css',
  '/static/htmx.min.js',
  '/static/manifest.json',
  '/static/the-ledger-logo-lockup.png',
  '/static/the-ledger-seal.png',
  '/static/favicon.ico',
  '/static/favicon-16x16.png',
  '/static/favicon-32x32.png',
  '/static/favicon-64x64.png',
  '/static/apple-touch-icon.png',
  '/static/icon-192x192.png',
  '/static/icon-512x512.png',
  '/static/icon-1024x1024.png',
];

// ── Install: pre-cache app shell ────────────────────────────────────────────
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(PRECACHE_URLS);
    }).then(() => self.skipWaiting())
  );
});

// ── Activate: clean old caches ──────────────────────────────────────────────
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys
          .filter((key) => key !== CACHE_NAME)
          .map((key) => caches.delete(key))
      );
    }).then(() => self.clients.claim())
  );
});

// ── Fetch: routing strategy ─────────────────────────────────────────────────
self.addEventListener('fetch', (event) => {
  const { request } = event;

  // Only handle GET requests
  if (request.method !== 'GET') return;

  const url = new URL(request.url);

  // Do not intercept or retain cross-origin requests.
  if (url.origin !== self.location.origin) return;

  // Static assets: cache-first
  if (url.pathname.startsWith('/static/')) {
    event.respondWith(cacheFirst(request));
    return;
  }

  // HTML navigation requests: network-only with generic offline fallback.
  if (request.mode === 'navigate' || request.headers.get('accept')?.includes('text/html')) {
    event.respondWith(networkOnlyWithOfflineFallback(request));
    return;
  }

  // Everything else (HTMX partials, API calls): network-only.
  event.respondWith(fetch(request));
});

// ── Cache-first (static assets) ─────────────────────────────────────────────
async function cacheFirst(request) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(CACHE_NAME);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    return new Response('', { status: 503, statusText: 'Offline' });
  }
}

// ── Network-only with offline fallback (navigation) ─────────────────────────
async function networkOnlyWithOfflineFallback(request) {
  try {
    return await fetch(request);
  } catch {
    // The only cached HTML is the generic, data-free offline page.
    const offlinePage = await caches.match(OFFLINE_URL);
    if (offlinePage) return offlinePage;

    return new Response('<h1>Offline</h1><p>Please check your connection.</p>', {
      status: 503,
      headers: { 'Content-Type': 'text/html' },
    });
  }
}
