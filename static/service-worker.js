const CACHE_NAME = "transactions-cache-v1";
const urlsToCache = [
  "/finance/transaction/add/",
  "/static/styles/index.css",
  "/static/images/app-icon.png"
];

// Install event: cache resources
self.addEventListener("install", (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(urlsToCache);
    })
  );
});

// Fetch event: serve cached files when offline
self.addEventListener("fetch", (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
