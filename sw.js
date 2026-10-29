/* OuRi service worker — офлайн-доступ к сайту и банку вопросов */
const CACHE = 'ouri-v1.6.0';
const CORE = [
  './', './index.html', './css/style.css', './js/app.js', './js/i18n.js',
  './manifest.webmanifest', './assets/bank-index.js', './js/reader.js',
  './assets/logo.png', './assets/favicon.png', './assets/favicon.ico',
  './assets/icon-192.png', './assets/icon-512.png', './assets/apple-touch-icon.png'
];
const BANKS = [1,2,3,4,5,6,7,8,9,10,11].map(n => './assets/bank-' + n + '.js');
/* Хрестоматия: каталог кэшируем сразу (он один на весь раздел), тексты авторов —
   лениво, при первом открытии автора (см. обработчик fetch ниже). */
const LIT = ['./assets/lit/catalog.js'];

self.addEventListener('install', e => {
  /* LIT кладём вторым заходом и с catch: если каталога хрестоматии в сборке нет,
     установка service worker не должна из-за этого падать. */
  e.waitUntil(
    caches.open(CACHE)
      .then(c => c.addAll(CORE))
      .then(() => caches.open(CACHE))
      .then(c => c.addAll(LIT).catch(() => {}))
      .then(() => self.skipWaiting())
  );
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
  const isBank = /\/assets\/bank-\d+\.js$/.test(url.pathname) ||
               /\/assets\/lit\/.+\.json$/.test(url.pathname);
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
    }).catch(() => caches.match(req).then(hit => {
      if (hit) return hit;
      // навигация на статическую посадочную (/7/algebra/) офлайн — отдаём кэш страницы,
      // иначе приложение, чтобы сайт не «умирал» без сети
      if (req.mode === 'navigate') {
        return caches.match(url.pathname).then(p2 => p2 || caches.match('./index.html'));
      }
      return url.pathname.endsWith('/') ? caches.match('./index.html') : null;
    }))
  );
});

self.addEventListener('message', e => {
  if (e.data === 'precache-banks') {
    e.waitUntil(caches.open(CACHE).then(c => Promise.all(BANKS.map(u => c.add(u).catch(() => {})))));
  }
});
