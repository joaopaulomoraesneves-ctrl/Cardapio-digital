const CACHE_NAME = "delicia-digital-v5";

const APP_SHELL = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "https://cdn.tailwindcss.com",
  "https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600&family=Inter:wght@300;400;600;700;800&display=swap"
];

self.addEventListener("install", event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => Promise.allSettled(APP_SHELL.map(url => cache.add(url))))
      .then(() => self.skipWaiting())
  );
});

self.addEventListener("activate", event => {
  event.waitUntil(
    caches.keys()
      .then(keys => Promise.all(keys.filter(key => key !== CACHE_NAME).map(key => caches.delete(key))))
      .then(() => self.clients.claim())
  );
});

self.addEventListener("fetch", event => {
  const request = event.request;

  if (request.method !== "GET") return;

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then(response => {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone)).catch(() => {});
          return response;
        })
        .catch(() => caches.match(request).then(cached => cached || caches.match("./index.html")))
    );
    return;
  }

  event.respondWith(
    caches.match(request).then(cached => {
      if (cached) return cached;

      return fetch(request).then(response => {
        const responseIsCacheable = response && (response.status === 200 || response.type === "opaque");
        if (responseIsCacheable) {
          const clone = response.clone();
          caches.open(CACHE_NAME).then(cache => cache.put(request, clone)).catch(() => {});
        }
        return response;
      });
    }).catch(() => {
      if (request.destination === "image") {
        return new Response(
          "<svg xmlns='http://www.w3.org/2000/svg' width='600' height='400'><rect fill='#333' width='600' height='400'/><text fill='#fff' x='50%' y='50%' dominant-baseline='middle' text-anchor='middle'>Offline</text></svg>",
          { headers: { "Content-Type": "image/svg+xml" } }
        );
      }
      return new Response("Offline", { status: 503, statusText: "Offline" });
    })
  );
});
