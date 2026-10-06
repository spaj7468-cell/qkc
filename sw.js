/* OuRi service worker — офлайн-доступ к сайту и банку вопросов */
const CACHE = 'ouri-v1.3.0';
const CORE = [
  './', './index.html', './css/style.css', './js/app.js', './js/i18n.js',
  './manifest.webmanifest', './assets/bank-index.js',
  './assets/logo.png', './assets/favicon.png', './assets/favicon.ico',
  './assets/icon-192.png', './assets/icon-512.png', './assets/apple-touch-icon.png'
];
const BANKS = [1,2,3,4,5,6,7,8,9,10,11].map(n => './assets/bank-' + n + '.js');

self.addEventListener('install', e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(CORE)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys().then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', e => {
  const req = e.request;
  if (req.method !== 'GET') return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;

  // банк классов кэшируем в фоне (тяжёлые файлы)
  const isBank = /\/assets\/bank-\d+\.js$/.test(url.pathname);
  if (isBank) {
    e.respondWith(
      caches.open(CACHE).then(cache =>
        cache.match(req).then(hit => {
          const net = fetch(req).then(res => { if (res && res.status === 200) cache.put(req, res.clone()); return res; }).catch(() => hit);
          return hit || net;
        })
      )
    );
    return;
  }

  e.respondWith(
    fetch(req).then(res => {
      const copy = res.clone();
      caches.open(CACHE).then(c => { if (res.status === 200) c.put(req, copy); }).catch(() => {});
      return res;
    }).catch(() => caches.match(req).then(hit => hit || (url.pathname.endsWith('/') ? caches.match('./index.html') : null)))
  );
});

self.addEventListener('message', e => {
  if (e.data === 'precache-banks') {
    e.waitUntil(caches.open(CACHE).then(c => Promise.all(BANKS.map(u => c.add(u).catch(() => {})))));
  }
});
