// Nombre del caché
const CACHE_NAME = 'control-taller-cache-v2';

// Archivos a cachear (como estáticos)
const urlsToCache = [
    '/',
    '/index.html',
    '/manifest.json',
    '/favicon.ico',
    '/Hartwich_logo192.png', 
    '/Hartwich_logo512.png', 
    '/js/app.js', 
    '/js/chunk-vendors.js',
    '/css/styles.css'
];

// Instalar el Service Worker y cachear archivos estáticos
self.addEventListener('install', (event) => {
  console.log('Service Worker: Instalando...');
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      console.log('Service Worker: Cacheando archivos...');
      return cache.addAll(urlsToCache);
    })
  );
});

// Activar y limpiar cachés antiguas
self.addEventListener('activate', (event) => {
  console.log('Service Worker: Activado');
  event.waitUntil(
    caches.keys().then((cacheNames) => {
      return Promise.all(
        cacheNames.map((cacheName) => {
          if (cacheName !== CACHE_NAME) {
            console.log('Service Worker: Eliminando caché antiguo', cacheName);
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Interceptar solicitudes de la red
self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);

  // Manejo especial para API
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(event.request)
        .then((response) => {
          return caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, response.clone());
            return response;
          });
        })
        .catch(() => {
          return caches.match(event.request).then((cachedResponse) => {
            return cachedResponse || new Response(JSON.stringify([]), {
              headers: { "Content-Type": "application/json" },
            });
          });
        })
    );
  } else {
    // Para archivos estáticos
    event.respondWith(
      caches.match(event.request).then((cachedResponse) => {
        return cachedResponse || fetch(event.request);
      })
    );
  }
});
