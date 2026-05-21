const CACHE_NAME = "delicia-digital-v3";

const APP_SHELL = [
    "./",
    "./index.html",
    "./manifest.webmanifest"
];

self.addEventListener("install", event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(APP_SHELL))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener("activate", event => {
    event.waitUntil(
        caches.keys()
            .then(keys => {
                return Promise.all(
                    keys
                        .filter(key => key !== CACHE_NAME)
                        .map(key => caches.delete(key))
                );
            })
            .then(() => self.clients.claim())
    );
});

self.addEventListener("fetch", event => {
    const request = event.request;

    if (request.method !== "GET") return;

    event.respondWith(
        fetch(request)
            .then(response => {
                const responseClone = response.clone();

                caches.open(CACHE_NAME).then(cache => {
                    cache.put(request, responseClone).catch(() => {});
                });

                return response;
            })
            .catch(() => {
                return caches.match(request).then(cached => {
                    if (cached) return cached;

                    if (request.mode === "navigate") {
                        return caches.match("./index.html");
                    }

                    return new Response("Offline", {
                        status: 503,
                        statusText: "Offline"
                    });
                });
            })
    );
});
