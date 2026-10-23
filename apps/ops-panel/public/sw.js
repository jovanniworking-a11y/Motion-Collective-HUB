/* MOTION Ops — offline cache (draft). Network first, so the login gate always applies when online;
   the last good copy of each page is the offline fallback. Logging out clears this cache. */
const CACHE = "motion-ops-panel-v2";

self.addEventListener("install", () => self.skipWaiting());

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
  event.respondWith(
    fetch(req)
      .then((res) => {
        if (res.ok && !res.redirected && res.type === "basic") {
          const copy = res.clone();
          caches.open(CACHE).then((c) => c.put(req, copy));
        }
        return res;
      })
      .catch(() => caches.match(req).then((hit) => hit || caches.match("/night-of") || Response.error())),
  );
});
