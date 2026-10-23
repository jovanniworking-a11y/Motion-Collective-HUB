/* MOTION Ops — offline shell cache (network-first for pages).
   Behind the login, a page fetched while logged out comes back as a redirect to /login;
   those are never cached, so the gate always applies online. Logging out clears this cache. */
const CACHE = "motion-ops-panel-v4";
const SHELL = [
  "/",
  "/manifest.webmanifest",
];

function cacheable(res, url) {
  return res.ok && !res.redirected && res.type === "basic" && url.origin === self.location.origin;
}

self.addEventListener("install", (event) => {
  event.waitUntil(
    caches
      .open(CACHE)
      .then((cache) =>
        Promise.all(
          SHELL.map((path) =>
            fetch(path)
              .then((res) => (cacheable(res, new URL(path, self.location.origin)) ? cache.put(path, res) : null))
              .catch(() => null),
          ),
        ),
      )
      .then(() => self.skipWaiting()),
  );
});

self.addEventListener("activate", (event) => {
  event.waitUntil(
    caches.keys().then((keys) =>
      Promise.all(keys.filter((k) => k !== CACHE).map((k) => caches.delete(k))),
    ).then(() => self.clients.claim()),
  );
});

self.addEventListener("fetch", (event) => {
  const req = event.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== self.location.origin) return;
  if (url.pathname.startsWith("/api/") || url.pathname === "/login" || url.pathname === "/health") return;
  // Navigations go network-first: a fresh deploy's HTML (with new hashed
  // JS chunks) is picked up immediately, and the login gate always runs.
  // Offline falls back to the last good copy of the page.
  if (req.mode === "navigate") {
    event.respondWith(
      fetch(req)
        .then((res) => {
          if (cacheable(res, url)) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return res;
        })
        .catch(() =>
          caches.match(req).then((hit) => hit || caches.match("/night-of")).then((hit) => hit || caches.match("/")),
        ),
    );
    return;
  }
  // Static assets: cache-first (they are content-hashed).
  event.respondWith(
    caches.match(req).then(
      (hit) =>
        hit ||
        fetch(req).then((res) => {
          if (cacheable(res, url)) {
            const copy = res.clone();
            caches.open(CACHE).then((c) => c.put(req, copy));
          }
          return res;
        }),
    ),
  );
});
