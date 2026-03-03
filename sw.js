// Second Breakfast Service Worker
// Network-first for navigation — guarantees fresh HTML when online
const CACHE = 'sb-v2.7';

self.addEventListener('install', function(e) {
  self.skipWaiting();
});

self.addEventListener('activate', function(e) {
  e.waitUntil(
    caches.keys().then(function(keys) {
      return Promise.all(
        keys.filter(function(k) { return k !== CACHE; })
            .map(function(k) { return caches.delete(k); })
      );
    }).then(function() { return clients.claim(); })
  );
});

self.addEventListener('fetch', function(e) {
  // Network-first for HTML navigation — always get fresh app when online
  if (e.request.mode === 'navigate') {
    e.respondWith(
      fetch(e.request).then(function(r) {
        var clone = r.clone();
        caches.open(CACHE).then(function(c) { c.put(e.request, clone); });
        return r;
      }).catch(function() {
        return caches.match(e.request);
      })
    );
    return;
  }
  // Cache-first for everything else (icons, version.json etc)
  e.respondWith(
    caches.match(e.request).then(function(r) {
      return r || fetch(e.request).then(function(nr) {
        caches.open(CACHE).then(function(c) { c.put(e.request, nr.clone()); });
        return nr;
      });
    })
  );
});
