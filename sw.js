// MedStudy Service Worker
const CACHE_NAME = 'medstudy-v1.0.0';
const STATIC_CACHE = 'medstudy-static-v1';
const DYNAMIC_CACHE = 'medstudy-dynamic-v1';

// Arquivos para cache estático (sempre disponíveis offline)
const STATIC_FILES = [
  '/',
  '/static/js/bundle.js',
  '/static/css/main.css',
  '/manifest.json',
  '/icon-192.png',
  '/icon-512.png'
];

// Arquivos para cache dinâmico (APIs e dados)
const DYNAMIC_FILES = [
  '/api/auth/me',
  '/api/questions/session',
  '/api/flashcards/due',
  '/api/progress/stats'
];

// Instalar Service Worker
self.addEventListener('install', event => {
  console.log('[SW] Installing Service Worker...');
  
  event.waitUntil(
    Promise.all([
      // Cache estático
      caches.open(STATIC_CACHE).then(cache => {
        console.log('[SW] Caching static files');
        return cache.addAll(STATIC_FILES);
      }),
      // Pular waiting para ativar imediatamente
      self.skipWaiting()
    ])
  );
});

// Ativar Service Worker
self.addEventListener('activate', event => {
  console.log('[SW] Activating Service Worker...');
  
  event.waitUntil(
    Promise.all([
      // Limpar caches antigos
      caches.keys().then(cacheNames => {
        return Promise.all(
          cacheNames.map(cacheName => {
            if (cacheName !== STATIC_CACHE && cacheName !== DYNAMIC_CACHE) {
              console.log('[SW] Deleting old cache:', cacheName);
              return caches.delete(cacheName);
            }
          })
        );
      }),
      // Tomar controle de todas as abas
      self.clients.claim()
    ])
  );
});

// Interceptar requisições
self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);
  
  // Estratégia para arquivos estáticos: Cache First
  if (STATIC_FILES.some(file => url.pathname.includes(file))) {
    event.respondWith(
      caches.match(request).then(response => {
        return response || fetch(request).then(fetchResponse => {
          return caches.open(STATIC_CACHE).then(cache => {
            cache.put(request, fetchResponse.clone());
            return fetchResponse;
          });
        });
      }).catch(() => {
        // Fallback para página offline
        if (request.destination === 'document') {
          return caches.match('/');
        }
      })
    );
    return;
  }
  
  // Estratégia para APIs: Network First com fallback para cache
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(
      fetch(request).then(response => {
        // Se a resposta for bem-sucedida, cache ela
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(DYNAMIC_CACHE).then(cache => {
            cache.put(request, responseClone);
          });
        }
        return response;
      }).catch(() => {
        // Se falhar, tenta buscar no cache
        return caches.match(request).then(response => {
          if (response) {
            return response;
          }
          // Fallback para dados offline
          return new Response(JSON.stringify({
            offline: true,
            message: 'Dados não disponíveis offline'
          }), {
            headers: { 'Content-Type': 'application/json' }
          });
        });
      })
    );
    return;
  }
  
  // Estratégia padrão: Network First
  event.respondWith(
    fetch(request).catch(() => {
      return caches.match(request);
    })
  );
});

// Sincronização em background
self.addEventListener('sync', event => {
  console.log('[SW] Background sync:', event.tag);
  
  if (event.tag === 'sync-progress') {
    event.waitUntil(syncProgress());
  }
  
  if (event.tag === 'sync-answers') {
    event.waitUntil(syncAnswers());
  }
});

// Notificações push
self.addEventListener('push', event => {
  console.log('[SW] Push received:', event);
  
  const options = {
    body: event.data ? event.data.text() : 'Hora de estudar! 📚',
    icon: '/icon-192.png',
    badge: '/icon-72.png',
    vibrate: [200, 100, 200],
    data: {
      url: '/'
    },
    actions: [
      {
        action: 'study',
        title: 'Estudar Agora',
        icon: '/icon-96.png'
      },
      {
        action: 'later',
        title: 'Mais Tarde',
        icon: '/icon-96.png'
      }
    ]
  };
  
  event.waitUntil(
    self.registration.showNotification('MedStudy', options)
  );
});

// Clique em notificação
self.addEventListener('notificationclick', event => {
  console.log('[SW] Notification clicked:', event);
  
  event.notification.close();
  
  if (event.action === 'study') {
    event.waitUntil(
      clients.openWindow('/questions')
    );
  } else if (event.action === 'later') {
    // Reagendar notificação
    scheduleNotification(30 * 60 * 1000); // 30 minutos
  } else {
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

// Funções auxiliares
async function syncProgress() {
  try {
    // Sincronizar progresso local com servidor
    const cache = await caches.open(DYNAMIC_CACHE);
    const requests = await cache.keys();
    
    for (const request of requests) {
      if (request.url.includes('/api/progress/')) {
        try {
          await fetch(request);
        } catch (error) {
          console.log('[SW] Failed to sync:', request.url);
        }
      }
    }
  } catch (error) {
    console.error('[SW] Sync progress failed:', error);
  }
}

async function syncAnswers() {
  try {
    // Sincronizar respostas offline com servidor
    const offlineAnswers = await getOfflineAnswers();
    
    for (const answer of offlineAnswers) {
      try {
        await fetch('/api/questions/answer', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(answer)
        });
        await removeOfflineAnswer(answer.id);
      } catch (error) {
        console.log('[SW] Failed to sync answer:', answer.id);
      }
    }
  } catch (error) {
    console.error('[SW] Sync answers failed:', error);
  }
}

function scheduleNotification(delay) {
  setTimeout(() => {
    self.registration.showNotification('MedStudy', {
      body: 'Que tal uma sessão rápida de estudos? 🎯',
      icon: '/icon-192.png',
      badge: '/icon-72.png'
    });
  }, delay);
}

// Helpers para IndexedDB (dados offline)
async function getOfflineAnswers() {
  // Implementar busca no IndexedDB
  return [];
}

async function removeOfflineAnswer(id) {
  // Implementar remoção do IndexedDB
  return true;
}

console.log('[SW] Service Worker loaded successfully!');

