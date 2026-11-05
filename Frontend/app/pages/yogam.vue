<template>
   <div class="min-h-screen bg-slate-50 text-slate-800 pt-32 pb-16 px-4 sm:px-6 lg:px-8 font-sans selection:bg-brand-gold selection:text-white">
    <!-- Header Section -->
    <div class="max-w-7xl mx-auto mb-16 text-center space-y-4">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
          {{ t('yogam.header.title') }}
        </h1>
        <div class="h-1.5 w-32 bg-brand-gold mx-auto rounded-full"></div>
        <p class="text-lg text-slate-500 max-w-xl mx-auto font-medium">
          {{ t('yogam.header.description') }}
        </p>
        
        <div v-if="auth.isAuthenticated" class="pt-6 flex justify-center">
            <button 
                @click="isAddModalOpen = true"
                class="bg-brand-gold text-white px-8 py-3 rounded-2xl font-bold shadow-lg shadow-brand-gold/20 hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
            >
                <span class="text-xl leading-none">+</span> {{ t('yogam.header.addHighlight') }}
            </button>
        </div>
    </div>

    <!-- Events Grid -->
    <div class="max-w-7xl mx-auto grid grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-8 lg:gap-10 items-start">
      
      <!-- Skeleton Cards -->
      <template v-if="loading">
        <div v-for="n in 6" :key="n" class="bg-white h-112.5 rounded-xl overflow-hidden shadow-sm border border-slate-200 animate-pulse">
           <div class="h-1/2 bg-slate-200"></div>
           <div class="p-6 space-y-4">
              <div class="h-6 bg-slate-200 rounded w-3/4"></div>
              <div class="h-4 bg-slate-200 rounded w-full"></div>
           </div>
        </div>
      </template>

      <!-- Real Event Cards -->
      <template v-else-if="events.length > 0">
        <div 
          v-for="event in events" 
          :key="event.id" 
          @click="openDetails(event)"
          @keydown.enter.prevent="openDetails(event)"
          tabindex="0"
          role="button"
          class="group relative flex flex-col bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl border border-slate-200 transition-all duration-300 hover:-translate-y-1 cursor-pointer min-h-0 max-h-[calc(100vh-12rem)]"
        >
          <!-- Image & Date -->
          <div class="relative aspect-4/3 overflow-hidden">
            <img 
              :src="resolveImage(event.image) || 'https://placehold.co/800x600/f1f5f9/d4af37?text=Annual+Meeting'" 
              :alt="event.title" 
              class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" 
            />
            <div class="absolute inset-0 bg-linear-to-t from-black/40 via-transparent to-transparent opacity-60"></div>
            
            <!-- Floating Date Badge -->
            <div class="absolute top-4 left-4 bg-white/90 backdrop-blur-md border border-slate-200 rounded-lg p-3 text-center min-w-17.5 shadow-lg">
              <span class="block text-xs font-bold uppercase tracking-wider text-brand-gold mb-0.5">{{ getMonth(event.event_date) }}</span>
              <span class="block text-2xl font-serif font-bold text-slate-900 leading-none">{{ getDay(event.event_date) }}</span>
            </div>
          </div>

          <!-- Content -->
          <div class="flex-1 p-6 flex flex-col relative text-left overflow-hidden">
            <div class="flex items-center gap-4 text-xs font-medium text-brand-gold mb-3 tracking-wide uppercase">
              <div v-if="event.location" class="flex items-center gap-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path></svg>
                {{ event.location }}
              </div>
            </div>

            <h2 class="text-2xl font-serif font-bold text-slate-900 mb-3 group-hover:text-brand-gold transition-colors">
              {{ event.title }}
            </h2>
            
            <p class="text-slate-600 text-sm leading-relaxed mb-6 font-medium overflow-auto" style="max-height:6.5rem;">
              {{ event.description }}
            </p>

            <div class="mt-auto pt-4 border-t border-slate-100">
               <button class="text-sm font-semibold text-slate-700 group-hover:text-brand-gold transition-colors flex items-center gap-2">
                 {{ t('yogam.card.viewHighlights') }}
                   <svg class="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
               </button>
            </div>
          </div>
        </div>
      </template>

      <!-- Empty State -->
      <template v-else>
        <div class="col-span-full max-w-md mx-auto mt-2 text-center p-10 bg-white rounded-2xl border border-slate-200 shadow-sm">
          <svg class="w-16 h-16 text-slate-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
          <h3 class="text-xl font-serif text-slate-800 mb-2">{{ t('yogam.empty.title') }}</h3>
          <p class="text-slate-500 text-sm">{{ t('yogam.empty.description') }}</p>
        </div>
      </template>
    </div>

    <!-- Details Modal (Facebook Card Format: Photo Left, Content Right) -->
    <Transition name="fade">
      <div v-if="selectedEvent" class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6" @click.self="closeDetails">
        <div class="absolute inset-0 bg-black/75 backdrop-blur-sm" @click="closeDetails"></div>
        
        <div class="relative bg-white rounded-2xl max-w-5xl w-full max-h-[92vh] overflow-y-auto md:overflow-hidden shadow-2xl border border-slate-200 flex flex-col md:flex-row z-10">
          <!-- Mobile Close Button -->
          <button @click="closeDetails" class="md:hidden absolute top-3 right-3 z-20 p-2 bg-black/60 hover:bg-black/80 rounded-full text-white transition-colors" aria-label="Close modal">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>

          <!-- Left Side: Large Unobstructed Photo Viewer -->
          <div class="md:w-3/5 bg-slate-50 border-b md:border-b-0 md:border-r border-slate-100 relative flex flex-col justify-between items-center min-h-[320px] sm:min-h-[420px] md:min-h-[550px] md:max-h-[92vh] shrink-0 overflow-hidden">
            <div class="relative flex-1 w-full flex items-center justify-center p-2 sm:p-4 min-h-0">
              <img
                :src="resolveImage(activeModalImage) || 'https://placehold.co/800x600/f1f5f9/d4af37?text=Annual+Meeting'"
                :alt="selectedEvent.title || t('yogam.modal.imageAlt')"
                class="w-full h-full max-h-[55vh] md:max-h-[76vh] object-contain select-none rounded-lg"
              />

              <template v-if="selectedMediaUrls.length > 1">
                <button
                  type="button"
                  @click.stop="prevModalImage"
                  class="absolute left-3 top-1/2 -translate-y-1/2 z-10 p-2.5 rounded-full bg-white/90 hover:bg-white text-slate-700 border border-slate-200 shadow-md transition"
                  aria-label="Previous image"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M15 19l-7-7 7-7"></path></svg>
                </button>
                <button
                  type="button"
                  @click.stop="nextModalImage"
                  class="absolute right-3 top-1/2 -translate-y-1/2 z-10 p-2.5 rounded-full bg-white/90 hover:bg-white text-slate-700 border border-slate-200 shadow-md transition"
                  aria-label="Next image"
                >
                  <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"></path></svg>
                </button>
                <div class="absolute bottom-3 right-3 z-10 bg-white/90 text-slate-700 border border-slate-200 shadow-sm text-xs font-bold px-3 py-1 rounded-full">
                  {{ activeImageIndex + 1 }} / {{ selectedMediaUrls.length }}
                </div>
              </template>
            </div>

            <!-- Thumbnails Strip -->
            <div v-if="selectedMediaUrls.length > 1" class="w-full flex gap-2 overflow-x-auto px-4 py-3 bg-white border-t border-slate-100 shrink-0">
              <button
                v-for="(imgUrl, idx) in selectedMediaUrls"
                :key="idx"
                type="button"
                @click.stop="activeImageIndex = idx"
                class="relative w-12 h-12 rounded-lg overflow-hidden shrink-0 border-2 transition-all"
                :class="idx === activeImageIndex ? 'border-brand-gold scale-105 shadow-md' : 'border-transparent opacity-60 hover:opacity-100'"
              >
                <img
                  :src="resolveImage(imgUrl) || ''"
                  :alt="`${selectedEvent.title} - ${idx + 1}`"
                  fetchpriority="low"
                  loading="lazy"
                  class="w-full h-full object-cover"
                />
              </button>
            </div>
          </div>

          <!-- Right Side: Content & Actions -->
          <div class="md:w-2/5 flex flex-col md:max-h-[92vh] bg-white">
            <!-- Header -->
            <div class="p-6 pb-4 border-b border-slate-100 flex items-start justify-between gap-4">
              <div class="space-y-2">
                <span class="inline-block px-3 py-1 bg-brand-gold text-white text-xs font-bold uppercase tracking-wider rounded-md">
                  {{ getMonth(selectedEvent.event_date || selectedEvent.created_at) }} {{ getDay(selectedEvent.event_date || selectedEvent.created_at) }}, {{ getYear(selectedEvent.event_date || selectedEvent.created_at) }}
                </span>
                <h2 class="text-xl sm:text-2xl font-serif font-bold text-slate-900 leading-snug">{{ selectedEvent.title }}</h2>
                <div v-if="selectedEvent.location" class="flex items-center gap-1.5 text-xs text-slate-600 font-medium pt-1">
                  <svg class="w-4 h-4 text-brand-gold shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path></svg>
                  <span>{{ selectedEvent.location }}</span>
                </div>
              </div>
              <button @click="closeDetails" class="hidden md:flex p-2 bg-slate-100 hover:bg-slate-200 rounded-full text-slate-600 transition-colors shrink-0" aria-label="Close modal">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>

            <!-- Scrollable Description -->
            <div class="p-6 flex-1 overflow-y-auto">
              <div class="prose prose-slate max-w-none text-slate-800 font-sans leading-relaxed text-base sm:text-lg">
                <p class="font-medium whitespace-pre-wrap">{{ selectedEvent.description }}</p>
              </div>
            </div>

            <!-- Footer Actions -->
            <div v-if="auth.isAuthenticated && (selectedEvent.author_id === auth.user?.id || auth.user?.is_superuser)" class="p-6 pt-4 border-t border-slate-100 bg-slate-50/50 flex justify-end gap-2 mt-auto">
              <button 
                @click="openEdit"
                class="bg-slate-50 text-slate-600 px-6 py-2.5 rounded-xl font-bold text-xs border border-slate-200 hover:bg-slate-100 transition-colors"
              >
                {{ t('yogam.modal.edit') }}
              </button>
              <button 
                @click="deletePost(selectedEvent.id)"
                class="bg-red-50 text-red-600 px-6 py-2.5 rounded-xl font-bold text-xs border border-red-100 hover:bg-red-100 transition-colors"
              >
                {{ t('yogam.modal.delete') }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <AddPostModal 
        v-if="auth.isAuthenticated"
        :is-open="isAddModalOpen"
        type="event"
        :is-kudumbayogam="true"
        :initial-data="editingEvent"
        @close="closeAddModal"
        @refresh="refreshEvents"
    />
  </div>
</template>

<script setup lang="ts">
import { useRuntimeConfig, useHead, ref, onMounted, useRoute } from '#imports'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
import AddPostModal from '~/components/AddPostModal.vue'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const config = useRuntimeConfig()
const route = useRoute()
const apiBase = config.public.apiBase || 'http://localhost:8000'
const { t, locale } = useI18n()
const activeDateLocale = computed(() => locale.value === 'ml' ? 'ml-IN' : 'en-US')

useHead(() => ({
  title: t('yogam.meta.title'),
  meta: [{ name: 'description', content: t('yogam.meta.description') }],
  link: [{ rel: 'canonical', href: `${config.public.siteUrl || 'http://localhost:3000'}${route.path}` }]
}))

interface EventItem {
  id: number
  title: string
  description: string
  image: string
  media?: Array<{ id: number; media_url: string; caption?: string; media_type?: string }>
  event_date: string
  created_at?: string
  location?: string
  author_name?: string
  author_id?: number
}

const events = ref<EventItem[]>([])
const loading = ref(true)
const isAddModalOpen = ref(false)
const editingEvent = ref<EventItem | null>(null)
const selectedEvent = ref<EventItem | null>(null)
const activeImageIndex = ref(0)

const selectedMediaUrls = computed(() => {
  if (!selectedEvent.value) return []
  const mediaList = (selectedEvent.value.media || [])
    .map((m) => m.media_url)
    .filter(Boolean)
  if (mediaList.length > 0) return mediaList
  return selectedEvent.value.image ? [selectedEvent.value.image] : []
})

const activeModalImage = computed(() => {
  const urls = selectedMediaUrls.value
  if (urls.length === 0) return selectedEvent.value?.image || ''
  return urls[activeImageIndex.value] || urls[0] || ''
})

const nextModalImage = () => {
  const total = selectedMediaUrls.value.length
  if (total <= 1) return
  activeImageIndex.value = (activeImageIndex.value + 1) % total
}

const prevModalImage = () => {
  const total = selectedMediaUrls.value.length
  if (total <= 1) return
  activeImageIndex.value = (activeImageIndex.value - 1 + total) % total
}

const openDetails = (event: EventItem) => {
  selectedEvent.value = event
  activeImageIndex.value = 0
  document.body.style.overflow = 'hidden'
}

const closeDetails = () => {
  selectedEvent.value = null
  activeImageIndex.value = 0
  document.body.style.overflow = ''
}

const openEdit = () => {
  editingEvent.value = selectedEvent.value
  isAddModalOpen.value = true
}

const closeAddModal = () => {
  isAddModalOpen.value = false
  editingEvent.value = null
}

const getMonth = (dateStr: string) => new Date(dateStr).toLocaleString(activeDateLocale.value, { month: 'short' })
const getDay = (dateStr: string) => new Date(dateStr).getDate()
const getYear = (dateStr: string) => new Date(dateStr).getFullYear()

const resolveImage = (path: string) => {
    if (!path) return null
    if (path.startsWith('http')) return path
    const cleanPath = path.startsWith('/') ? path : `/${path}`
    return `${apiBase}${cleanPath}`
}

const refreshEvents = async () => {
    loading.value = true
    try {
        const [eventsRes, newsRes] = await Promise.all([
            fetch(`${apiBase}/api/news/events/`),
            fetch(`${apiBase}/api/news/list/`)
        ])
        const allItems: any[] = []
        const seenIds = new Set<number>()

        if (eventsRes.ok) {
            const evData = await eventsRes.json()
            const list = Array.isArray(evData) ? evData : (evData?.results || [])
            for (const item of list) {
                if (!seenIds.has(item.id)) {
                    seenIds.add(item.id)
                    allItems.push(item)
                }
            }
        }
        if (newsRes.ok) {
            const newsData = await newsRes.json()
            const list = Array.isArray(newsData) ? newsData : (newsData?.results || [])
            for (const item of list) {
                if (!seenIds.has(item.id)) {
                    seenIds.add(item.id)
                    allItems.push(item)
                }
            }
        }

        events.value = allItems.filter((e: any) => e.is_kudumbayogam)
        if (events.value.length === 0) {
            events.value = allItems.filter((e: any) =>
                (e.title || '').toLowerCase().includes('yogam') ||
                (e.description || '').toLowerCase().includes('yogam') ||
                (e.title || '').includes('കുടുംബയോഗം') ||
                (e.description || '').includes('കുടുംബയോഗം')
            )
        }
  } catch (e) {
    console.error("Failed to fetch kudumbayogam highlights", e)
    } finally {
    loading.value = false
  }
}

function getCookie(name: string) {
  if (typeof document === 'undefined') return null
  const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
  return matches ? matches[2] : null
}

const deletePost = async (id: number) => {
  if (!confirm(t('yogam.alerts.confirmDelete'))) return
    
    try {
    const csrfRes = await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
    const csrfData = await csrfRes.json().catch(() => ({}))
    const csrftoken = getCookie('csrftoken') || csrfData.csrfToken
        
        const res = await fetch(`${apiBase}/api/news/${id}/`, {
            method: 'DELETE',
            headers: {
                ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {})
            },
            credentials: 'include'
        })
        
        if (res.ok) {
            closeDetails()
            refreshEvents()
        } else {
          alert(t('yogam.alerts.deleteFailed'))
        }
    } catch (e) {
        console.error("Delete failed", e)
    }
}

onMounted(() => {
    refreshEvents()
})

</script>
