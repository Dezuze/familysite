// Kollamparampil Family PWA Service Worker — Celebration & Event Notifications

self.addEventListener('install', (event) => {
  self.skipWaiting()
})

self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim())
})

// Listen for Web Push events from a push service
self.addEventListener('push', (event) => {
  let payload = {
    title: 'Kollamparampil Family Celebration',
    body: 'A new birthday or anniversary poster has been generated!',
    icon: '/favicon.png',
    badge: '/favicon.png',
    image: undefined,
    tag: 'celebration-notification',
    data: { url: '/news-events' }
  }

  if (event.data) {
    try {
      const parsed = event.data.json()
      payload = { ...payload, ...parsed }
    } catch {
      payload.body = event.data.text()
    }
  }

  event.waitUntil(
    self.registration.showNotification(payload.title, {
      body: payload.body,
      icon: payload.icon || '/favicon.png',
      badge: payload.badge || '/favicon.png',
      image: payload.image || undefined,
      tag: payload.tag || 'celebration-notification',
      data: payload.data || { url: '/news-events' },
      vibrate: [150, 80, 150]
    })
  )
})

// Listen for client-triggered PWA celebration notifications when new daily posters are detected
self.addEventListener('message', (event) => {
  if (!event.data || event.data.type !== 'SHOW_CELEBRATION_NOTIFICATION') return

  const { title, body, image, postId, celebrationType } = event.data.payload || {}
  const targetUrl = postId ? `/news-events?post=${postId}` : '/news-events'

  event.waitUntil(
    self.registration.showNotification(title || 'Family Celebration', {
      body: body || 'View the newly generated celebration poster in the family feed.',
      icon: '/favicon.png',
      badge: '/favicon.png',
      image: image || undefined,
      tag: `celebration-${postId || Date.now()}`,
      data: { url: targetUrl, postId, celebrationType }
    })
  )
})

// Focus or open the app at the celebration poster when the user clicks the PWA notification
self.addEventListener('notificationclick', (event) => {
  event.notification.close()
  const targetUrl = (event.notification.data && event.notification.data.url) || '/news-events'

  event.waitUntil(
    self.clients.matchAll({ type: 'window', includeUncontrolled: true }).then((clientList) => {
      for (const client of clientList) {
        if ('focus' in client) {
          client.postMessage({
            type: 'NOTIFICATION_CLICKED',
            url: targetUrl,
            postId: event.notification.data?.postId
          })
          return client.focus()
        }
      }
      if (self.clients.openWindow) {
        return self.clients.openWindow(targetUrl)
      }
    })
  )
})

