<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { useRouter, useRuntimeConfig } from '#imports'

export interface CelebrationNotificationItem {
  id: number
  title: string
  description: string
  image: string | null
  post_type: string
  created_at: string
  creator_name?: string
  is_auto_generated?: boolean
  celebration_type?: 'birthday' | 'wedding_anniversary' | 'death_anniversary' | 'celebration' | null
}

interface ActiveToast extends CelebrationNotificationItem {
  toastId: string
  timerId?: ReturnType<typeof setTimeout>
}

const router = useRouter()
const config = useRuntimeConfig()
const apiBase = (config.public.apiBase as string) || 'http://localhost:8000'

const notifications = ref<CelebrationNotificationItem[]>([])
const activeToasts = ref<ActiveToast[]>([])
const isDrawerOpen = ref(false)
const activeFilter = ref<'all' | 'birthday' | 'wedding_anniversary' | 'death_anniversary'>('all')
const loading = ref(false)
const seenIds = ref<Set<number>>(new Set())
const notificationPermission = ref<NotificationPermission>('default')
const swRegistration = ref<ServiceWorkerRegistration | null>(null)
const toastRefs = new Map<string, HTMLElement>()

const STORAGE_KEY = 'kollamparampil_seen_celebrations_v1'
let pollInterval: ReturnType<typeof setInterval> | null = null

const setToastRef = (toastId: string, el: Element | null) => {
  if (el instanceof HTMLElement) {
    toastRefs.set(toastId, el)
  } else {
    toastRefs.delete(toastId)
  }
}

const resolveImage = (path: string | null | undefined) => {
  if (!path) return '/images/logo.png'
  if (path.startsWith('http')) return path
  const cleanPath = path.startsWith('/') ? path : `/${path}`
  return `${apiBase}${cleanPath}`
}

const getBadgeMeta = (type?: string | null) => {
  switch (type) {
    case 'birthday':
      return {
        label: 'Birthday Poster',
        icon: '🎂',
        pillClass: 'bg-amber-500/15 text-amber-700 border-amber-500/30',
        accentClass: 'from-amber-500 to-yellow-600'
      }
    case 'wedding_anniversary':
      return {
        label: 'Wedding Anniversary',
        icon: '💍',
        pillClass: 'bg-emerald-500/15 text-emerald-700 border-emerald-500/30',
        accentClass: 'from-emerald-600 to-teal-700'
      }
    case 'death_anniversary':
      return {
        label: 'In Loving Memory',
        icon: '🕯️',
        pillClass: 'bg-slate-500/15 text-slate-700 border-slate-500/30',
        accentClass: 'from-slate-600 to-slate-800'
      }
    default:
      return {
        label: 'Family Celebration',
        icon: '🎉',
        pillClass: 'bg-brand-gold/15 text-brand-gold border-brand-gold/30',
        accentClass: 'from-brand-gold to-amber-700'
      }
  }
}

const formatRelativeDate = (dateStr: string) => {
  const d = new Date(dateStr)
  return d.toLocaleDateString('en-US', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const unreadCount = computed(() => {
  return notifications.value.filter((n) => !seenIds.value.has(n.id)).length
})

const filteredNotifications = computed(() => {
  if (activeFilter.value === 'all') return notifications.value
  return notifications.value.filter((n) => n.celebration_type === activeFilter.value)
})

const loadSeenIds = () => {
  if (typeof window === 'undefined') return
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) {
      const parsed = JSON.parse(raw)
      if (Array.isArray(parsed)) {
        seenIds.value = new Set(parsed.map(Number))
      }
    }
  } catch {
    // ignore storage errors
  }
}

const saveSeenIds = () => {
  if (typeof window === 'undefined') return
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify([...seenIds.value]))
  } catch {
    // ignore storage errors
  }
}

const markAsSeen = (id: number) => {
  seenIds.value.add(id)
  saveSeenIds()
}

const markAllAsSeen = () => {
  for (const item of notifications.value) {
    seenIds.value.add(item.id)
  }
  saveSeenIds()
}

// Dispatch native PWA Service Worker / Notification API alert
const sendPwaBrowserNotification = async (item: CelebrationNotificationItem) => {
  if (typeof window === 'undefined' || !('Notification' in window)) return
  if (Notification.permission !== 'granted') return

  const meta = getBadgeMeta(item.celebration_type)
  const imageUrl = resolveImage(item.image)
  const title = `${meta.icon} ${item.title}`
  const body = item.description || 'A new celebration poster has been generated in the Kollamparampil Family feed.'

  try {
    if (swRegistration.value && swRegistration.value.active) {
      swRegistration.value.active.postMessage({
        type: 'SHOW_CELEBRATION_NOTIFICATION',
        payload: {
          title,
          body,
          image: imageUrl,
          postId: item.id,
          celebrationType: item.celebration_type
        }
      })
      return
    }
    const n = new Notification(title, {
      body,
      icon: '/favicon.png',
      tag: `celebration-${item.id}`
    })
    n.onclick = () => {
      window.focus()
      openCelebrationPost(item)
    }
  } catch (e) {
    console.warn('PWA notification dispatch fallback:', e)
  }
}

// Show Top-Layer persistent toast notification using Popover API (`popover="manual"`)
const spawnCelebrationToast = async (item: CelebrationNotificationItem, alsoSendPwa = true) => {
  const toastId = `celebration-toast-${item.id}-${Date.now()}`
  const existingIdx = activeToasts.value.findIndex((t) => t.id === item.id)
  if (existingIdx !== -1) {
    const existing = activeToasts.value[existingIdx]
    if (existing?.timerId) clearTimeout(existing.timerId)
    activeToasts.value.splice(existingIdx, 1)
  }

  const toastObj: ActiveToast = {
    ...item,
    toastId
  }

  // Keep maximum 3 stacked toasts at once
  if (activeToasts.value.length >= 3) {
    const oldest = activeToasts.value.shift()
    if (oldest?.timerId) clearTimeout(oldest.timerId)
  }

  activeToasts.value.push(toastObj)

  await nextTick()
  const el = toastRefs.get(toastId)
  if (el && typeof el.showPopover === 'function') {
    try {
      el.showPopover()
    } catch {
      // fallback if already open or polyfill pending
    }
  }

  // Auto-dismiss after 8000ms using hidePopover()
  toastObj.timerId = setTimeout(() => {
    dismissToast(toastId)
  }, 8000)

  if (alsoSendPwa) {
    sendPwaBrowserNotification(item)
  }
}

const dismissToast = (toastId: string) => {
  const idx = activeToasts.value.findIndex((t) => t.toastId === toastId)
  if (idx === -1) return
  const toastObj = activeToasts.value[idx]
  if (toastObj?.timerId) clearTimeout(toastObj.timerId)

  const el = toastRefs.get(toastId)
  if (el && typeof el.hidePopover === 'function') {
    try {
      el.hidePopover()
    } catch {
      // ignore if already hidden
    }
  }
  activeToasts.value.splice(idx, 1)
}

const onToastToggle = (event: Event, toastId: string) => {
  const toggleEv = event as ToggleEvent
  if (toggleEv.newState === 'closed') {
    const idx = activeToasts.value.findIndex((t) => t.toastId === toastId)
    if (idx !== -1) {
      const t = activeToasts.value[idx]
      if (t?.timerId) clearTimeout(t.timerId)
      activeToasts.value.splice(idx, 1)
    }
  }
}

const requestPwaNotificationPermission = async () => {
  if (typeof window === 'undefined' || !('Notification' in window)) return
  try {
    const perm = await Notification.requestPermission()
    notificationPermission.value = perm
    if (perm === 'granted' && notifications.value.length > 0) {
      const latest = notifications.value[0]
      if (latest) {
        await spawnCelebrationToast(latest, true)
      }
    }
  } catch (e) {
    console.warn('Permission request error:', e)
  }
}

const triggerPreviewNotification = async () => {
  if (notifications.value.length === 0) {
    await fetchCelebrationNotifications(true)
  }
  // Pick a birthday and a wedding anniversary (or top 2 celebrations) to showcase stacking
  const bday = notifications.value.find((n) => n.celebration_type === 'birthday')
  const anniv = notifications.value.find((n) => n.celebration_type === 'wedding_anniversary')
  const targets = [bday, anniv].filter(Boolean) as CelebrationNotificationItem[]
  const fallbackTargets = targets.length > 0 ? targets : notifications.value.slice(0, 2)

  for (let i = 0; i < fallbackTargets.length; i++) {
    const item = fallbackTargets[i]
    if (item) {
      setTimeout(() => {
        spawnCelebrationToast(item, i === 0)
      }, i * 350)
    }
  }
}

const openCelebrationPost = (item: CelebrationNotificationItem) => {
  markAsSeen(item.id)
  isDrawerOpen.value = false
  for (const t of [...activeToasts.value]) {
    dismissToast(t.toastId)
  }
  router.push(`/news-events?post=${item.id}`)
}

const fetchCelebrationNotifications = async (forceToastOnFirstLoad = false) => {
  loading.value = true
  try {
    const res = await fetch(`${apiBase}/api/news/notifications/?limit=12`)
    if (!res.ok) return
    const data = await res.json()
    const list: CelebrationNotificationItem[] = data.notifications || []
    notifications.value = list

    // Identify unseen generated celebration posters
    const unseen = list.filter((item) => !seenIds.value.has(item.id))
    if (unseen.length > 0 || forceToastOnFirstLoad) {
      const toShow = (unseen.length > 0 ? unseen : list).slice(0, 2)
      toShow.forEach((item, idx) => {
        setTimeout(() => {
          spawnCelebrationToast(item, idx === 0)
        }, idx * 450)
      })
    }
  } catch (e) {
    console.warn('Failed to fetch celebration notifications:', e)
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  // Feature detect Popover on HTMLElement.prototype per modern-web-guidance
  if (typeof window !== 'undefined' && typeof HTMLElement !== 'undefined') {
    if (!('popover' in HTMLElement.prototype)) {
      import('https://unpkg.com/@oddbird/popover-polyfill@latest/dist/popover.min.js' as any).catch(() => {})
    }
  }

  loadSeenIds()

  if (typeof window !== 'undefined' && 'Notification' in window) {
    notificationPermission.value = Notification.permission
  }

  // Register PWA Service Worker
  if (typeof navigator !== 'undefined' && 'serviceWorker' in navigator) {
    try {
      const reg = await navigator.serviceWorker.register('/sw.js')
      swRegistration.value = reg

      navigator.serviceWorker.addEventListener('message', (event) => {
        if (event.data?.type === 'NOTIFICATION_CLICKED' && event.data?.url) {
          router.push(event.data.url)
        }
      })
    } catch (e) {
      console.warn('Service Worker registration skipped:', e)
    }
  }

  await fetchCelebrationNotifications()

  // Poll every 5 minutes for newly generated daily posters
  pollInterval = setInterval(() => {
    fetchCelebrationNotifications()
  }, 5 * 60 * 1000)
})

onUnmounted(() => {
  if (pollInterval) clearInterval(pollInterval)
  for (const t of activeToasts.value) {
    if (t.timerId) clearTimeout(t.timerId)
  }
})
</script>

<template>
  <!-- Floating PWA Celebration Notification Bell & Drawer -->
  <div class="fixed bottom-6 right-6 z-40 flex flex-col items-end gap-3">
    <!-- Notification Center Drawer -->
    <Transition name="drawer-pop">
      <div
        v-if="isDrawerOpen"
        class="w-[92vw] sm:w-96 max-h-[78vh] bg-white rounded-3xl shadow-2xl border border-slate-200/90 flex flex-col overflow-hidden"
        role="region"
        aria-label="Celebration Notifications"
      >
        <!-- Drawer Header -->
        <div class="p-4 bg-slate-900 text-white flex items-center justify-between">
          <div class="flex items-center gap-2.5">
            <span class="text-xl">🔔</span>
            <div>
              <h3 class="font-serif font-bold text-base leading-tight">Celebration Alerts</h3>
              <p class="text-[11px] text-slate-300">Auto-generated Birthdays &amp; Anniversaries</p>
            </div>
          </div>
          <div class="flex items-center gap-1.5">
            <button
              v-if="unreadCount > 0"
              @click="markAllAsSeen"
              class="text-[11px] font-bold px-2.5 py-1 rounded-full bg-white/10 hover:bg-white/20 text-amber-300 transition-colors"
            >
              Mark all read
            </button>
            <button
              @click="isDrawerOpen = false"
              class="p-1.5 rounded-full bg-white/10 hover:bg-white/20 text-slate-300 transition-colors"
              aria-label="Close notification center"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        </div>

        <!-- PWA Notification Permission & Live Preview Bar -->
        <div class="px-4 py-2.5 bg-amber-50/80 border-b border-amber-200/60 flex items-center justify-between gap-2">
          <div class="flex items-center gap-2 min-w-0">
            <span
              class="w-2 h-2 rounded-full shrink-0"
              :class="notificationPermission === 'granted' ? 'bg-emerald-500' : 'bg-amber-500 animate-pulse'"
            ></span>
            <span class="text-xs font-semibold text-slate-700 truncate">
              {{
                notificationPermission === 'granted'
                  ? 'PWA Push Alerts Active'
                  : 'Enable PWA Celebration Alerts'
              }}
            </span>
          </div>
          <div class="flex items-center gap-1.5 shrink-0">
            <button
              v-if="notificationPermission !== 'granted'"
              @click="requestPwaNotificationPermission"
              class="px-2.5 py-1 rounded-lg bg-brand-gold text-white text-[11px] font-bold hover:brightness-110 transition-all"
            >
              Enable
            </button>
            <button
              @click="triggerPreviewNotification"
              class="px-2.5 py-1 rounded-lg bg-slate-900 text-white text-[11px] font-bold hover:bg-slate-800 transition-all"
              title="Preview celebration toast & PWA notification"
            >
              Test Alert
            </button>
          </div>
        </div>

        <!-- Category Filter Tabs -->
        <div class="px-3 py-2 bg-slate-50 border-b border-slate-100 flex items-center gap-1 overflow-x-auto text-xs font-bold">
          <button
            @click="activeFilter = 'all'"
            class="px-2.5 py-1 rounded-full transition-colors whitespace-nowrap"
            :class="activeFilter === 'all' ? 'bg-slate-900 text-white' : 'text-slate-600 hover:bg-slate-200/60'"
          >
            All ({{ notifications.length }})
          </button>
          <button
            @click="activeFilter = 'birthday'"
            class="px-2.5 py-1 rounded-full transition-colors whitespace-nowrap"
            :class="activeFilter === 'birthday' ? 'bg-amber-500 text-white' : 'text-slate-600 hover:bg-slate-200/60'"
          >
            🎂 Birthdays
          </button>
          <button
            @click="activeFilter = 'wedding_anniversary'"
            class="px-2.5 py-1 rounded-full transition-colors whitespace-nowrap"
            :class="activeFilter === 'wedding_anniversary' ? 'bg-emerald-600 text-white' : 'text-slate-600 hover:bg-slate-200/60'"
          >
            💍 Anniversaries
          </button>
          <button
            @click="activeFilter = 'death_anniversary'"
            class="px-2.5 py-1 rounded-full transition-colors whitespace-nowrap"
            :class="activeFilter === 'death_anniversary' ? 'bg-slate-700 text-white' : 'text-slate-600 hover:bg-slate-200/60'"
          >
            🕯️ Memory
          </button>
        </div>

        <!-- Notification List -->
        <div class="flex-1 overflow-y-auto divide-y divide-slate-100 max-h-96">
          <div v-if="loading && notifications.length === 0" class="p-8 text-center text-sm text-slate-400">
            Scanning family tree celebrations...
          </div>
          <div v-else-if="filteredNotifications.length === 0" class="p-8 text-center text-sm text-slate-400">
            No generated celebration posters in this category yet.
          </div>
          <button
            v-for="item in filteredNotifications"
            :key="item.id"
            @click="openCelebrationPost(item)"
            class="w-full text-left p-3.5 hover:bg-slate-50 transition-colors flex items-start gap-3.5 relative group"
            :class="!seenIds.has(item.id) ? 'bg-amber-50/30' : ''"
          >
            <!-- Poster Thumbnail -->
            <div class="w-14 h-18 rounded-xl overflow-hidden bg-slate-100 border border-slate-200 shrink-0 shadow-xs">
              <img
                :src="resolveImage(item.image)"
                :alt="item.title"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-300"
              />
            </div>

            <!-- Content -->
            <div class="flex-1 min-w-0">
              <div class="flex items-center justify-between gap-1 mb-1">
                <span
                  class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider border"
                  :class="getBadgeMeta(item.celebration_type).pillClass"
                >
                  <span>{{ getBadgeMeta(item.celebration_type).icon }}</span>
                  <span>{{ getBadgeMeta(item.celebration_type).label }}</span>
                </span>
                <span class="text-[10px] font-semibold text-slate-400 shrink-0">
                  {{ formatRelativeDate(item.created_at) }}
                </span>
              </div>
              <h4 class="text-xs font-bold text-slate-900 line-clamp-2 group-hover:text-brand-gold transition-colors">
                {{ item.title }}
              </h4>
              <p class="text-[11px] text-slate-500 line-clamp-1 mt-0.5">
                {{ item.description }}
              </p>
            </div>

            <!-- Unread Dot -->
            <span
              v-if="!seenIds.has(item.id)"
              class="w-2 h-2 rounded-full bg-amber-500 shrink-0 mt-1.5"
              title="New celebration poster"
            ></span>
          </button>
        </div>

        <!-- Drawer Footer -->
        <div class="p-3 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
          <NuxtLink
            to="/news-events"
            @click="isDrawerOpen = false"
            class="text-xs font-bold text-brand-gold hover:underline"
          >
            View All Celebration Posters &rarr;
          </NuxtLink>
          <span class="text-[10px] font-semibold text-slate-400">PWA Auto-Sync</span>
        </div>
      </div>
    </Transition>

    <!-- Floating Bell Trigger Button -->
    <button
      @click="isDrawerOpen = !isDrawerOpen"
      class="relative flex items-center gap-2.5 bg-slate-900 hover:bg-slate-800 text-white pl-4 pr-4 py-3 rounded-full shadow-xl shadow-slate-900/25 border border-white/15 transition-all duration-300 hover:scale-105 active:scale-95 cursor-pointer"
      aria-label="Open Celebration Notifications"
    >
      <span class="text-lg leading-none">🎉</span>
      <span class="text-xs font-bold tracking-wide hidden sm:inline">Celebrations</span>
      <span
        v-if="unreadCount > 0"
        class="px-2 py-0.5 text-[10px] font-black rounded-full bg-amber-500 text-slate-950 shadow-xs"
      >
        {{ unreadCount }}
      </span>
    </button>
  </div>

  <!-- Top-Layer Persistent Toast Notifications Container (Popover API `popover="manual"`) -->
  <div class="celebration-toast-stack" aria-live="polite">
    <div
      v-for="(toast, index) in activeToasts"
      :key="toast.toastId"
      :id="toast.toastId"
      :ref="(el) => setToastRef(toast.toastId, el as Element | null)"
      v-bind="{ popover: 'manual' } as any"
      :style="{ '--toast-index': index }"
      class="celebration-toast-popover rounded-2xl bg-white/98 backdrop-blur-xl shadow-2xl border border-slate-200/90 overflow-hidden"
      @toggle="(e) => onToastToggle(e, toast.toastId)"
    >
      <!-- Top Accent Bar -->
      <div class="h-1.5 w-full bg-linear-to-r" :class="getBadgeMeta(toast.celebration_type).accentClass"></div>

      <div class="p-3.5 flex items-start gap-3.5">
        <!-- Generated Poster Preview -->
        <div
          @click="openCelebrationPost(toast)"
          class="w-16 h-20 rounded-xl overflow-hidden bg-slate-100 border border-slate-200 shrink-0 cursor-pointer shadow-sm group"
        >
          <img
            :src="resolveImage(toast.image)"
            :alt="toast.title"
            class="w-full h-full object-cover group-hover:scale-105 transition-transform"
          />
        </div>

        <!-- Notification Text & Actions -->
        <div class="flex-1 min-w-0">
          <div class="flex items-center justify-between gap-2 mb-1">
            <span
              class="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-[10px] font-extrabold uppercase tracking-wider border"
              :class="getBadgeMeta(toast.celebration_type).pillClass"
            >
              <span>{{ getBadgeMeta(toast.celebration_type).icon }}</span>
              <span>{{ getBadgeMeta(toast.celebration_type).label }}</span>
            </span>

            <!-- Explicit Close button using popovertargetaction="hide" -->
            <button
              type="button"
              v-bind="{ popovertarget: toast.toastId, popovertargetaction: 'hide' } as any"
              @click="dismissToast(toast.toastId)"
              class="p-1 rounded-lg text-slate-400 hover:text-slate-700 hover:bg-slate-100 transition-colors"
              aria-label="Close notification"
            >
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <h4 class="font-serif font-bold text-slate-900 text-sm leading-snug line-clamp-2">
            {{ toast.title }}
          </h4>
          <p class="text-xs text-slate-600 line-clamp-2 mt-0.5">
            {{ toast.description }}
          </p>

          <div class="mt-2.5 flex items-center gap-3">
            <button
              type="button"
              @click="openCelebrationPost(toast)"
              class="text-xs font-extrabold text-brand-gold hover:underline flex items-center gap-1"
            >
              View Poster &rarr;
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style>
/* Top-Layer Popover Toast styling per modern-web-guidance (persistent-toast-notifications) */
.celebration-toast-popover[popover] {
  position: fixed;
  inset: auto;
  top: 1.25rem;
  right: 1.25rem;
  width: min(24rem, calc(100vw - 2.5rem));
  margin: 0;
  padding: 0;
  border: 1px solid rgba(226, 232, 240, 0.95);
  /* Fallback stacking using --toast-index, enhanced with sibling-index() when supported */
  transform: translateY(calc(var(--toast-index, 0) * 10rem));
  opacity: 0;
  transition:
    opacity 0.28s ease,
    transform 0.32s cubic-bezier(0.16, 1, 0.3, 1),
    display 0.28s ease allow-discrete,
    overlay 0.28s ease allow-discrete;
  transition-behavior: allow-discrete;
}

@supports (margin-top: calc(sibling-index() * 1rem)) {
  .celebration-toast-popover[popover] {
    transform: translateY(calc((sibling-index() - 1) * 10rem));
  }
}

/* Fallback sibling spacing */
.celebration-toast-popover[popover] + .celebration-toast-popover[popover] {
  margin-top: 0.5rem;
}

/* Combine native :popover-open and polyfill .\:popover-open with :is() so older browsers don't discard the rule */
.celebration-toast-popover[popover]:is(:popover-open, .\:popover-open) {
  display: block;
  opacity: 1;
}

@starting-style {
  .celebration-toast-popover[popover]:is(:popover-open, .\:popover-open) {
    opacity: 0;
    transform: translateY(calc(var(--toast-index, 0) * 7.75rem - 1rem)) scale(0.96);
  }
}

.drawer-pop-enter-active,
.drawer-pop-leave-active {
  transition: opacity 0.25s ease, transform 0.28s cubic-bezier(0.16, 1, 0.3, 1);
}
.drawer-pop-enter-from,
.drawer-pop-leave-to {
  opacity: 0;
  transform: translateY(12px) scale(0.96);
}
</style>
