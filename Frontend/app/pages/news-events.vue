<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 pt-32 pb-16 px-4 sm:px-6 lg:px-8 font-sans selection:bg-brand-gold selection:text-white">
    <!-- Header -->
    <div class="max-w-7xl mx-auto mb-16 text-center space-y-4">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
          {{ t('newsEvents.header.title') }}
        </h1>
        <div class="h-1.5 w-32 bg-brand-gold rounded-full mx-auto"></div>
        <p class="text-lg text-slate-500 max-w-xl mx-auto font-medium">
          {{ t('newsEvents.header.description') }}
        </p>
        
        <div v-if="auth.isAuthenticated" class="pt-6 flex justify-center">
            <button 
                @click="isAddModalOpen = true"
                class="bg-brand-gold text-white px-8 py-3 rounded-2xl font-bold shadow-lg shadow-brand-gold/20 hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
            >
                <span class="text-xl leading-none">+</span> {{ t('newsEvents.header.postNews') }}
            </button>
        </div>
    </div>

    <!-- Masonry Feed -->
    <div class="max-w-7xl mx-auto">
      <div v-if="loading && items.length === 0" class="columns-2 lg:columns-3 gap-8 space-y-8">
         <div v-for="n in 6" :key="n" class="break-inside-avoid bg-white rounded-3xl overflow-hidden shadow-sm border border-slate-200 animate-pulse h-96"></div>
      </div>

      <div v-else class="columns-2 lg:columns-3 gap-8 space-y-8">
        <div 
          v-for="item in items" 
          :key="item.id"
          @click="openDetails(item)"
          class="break-inside-avoid group relative bg-white rounded-3xl overflow-hidden shadow-md hover:shadow-2xl border border-slate-100 transition-all duration-500 cursor-pointer flex flex-col"
        >
          <!-- Image Section (Fixed Frame) -->
          <div class="relative overflow-hidden bg-slate-100 border-b border-slate-100/50 h-64 sm:h-72">
            <img 
              :src="resolveImage(item.image) || 'https://placehold.co/800x600/f1f5f9/d4af37?text=Family+News'" 
              :alt="item.title"
              class="w-full h-full object-contain p-2 transition-transform duration-700 group-hover:scale-105"
            />
            <div class="absolute inset-0 bg-linear-to-t from-black/20 via-transparent to-transparent opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>
            
            <!-- Type Badge -->
            <div class="absolute top-4 right-4">
                <span 
                   class="px-4 py-1.5 rounded-full text-[10px] font-black uppercase tracking-widest shadow-lg backdrop-blur-md border border-white/20"
                   :class="item.is_auto_generated ? 'bg-amber-500 text-white shadow-amber-500/30' : (item.type === 'event' ? 'bg-brand-gold text-white shadow-brand-gold/30' : 'bg-white/90 text-slate-800')"
                >
                   {{ getTypeLabel(item.type, item.is_auto_generated) }}
                </span>
            </div>

            <!-- Multi-photo Badge -->
            <div v-if="item.media && item.media.length > 1" class="absolute bottom-3 right-3 bg-black/70 backdrop-blur-md text-white px-3 py-1 rounded-full text-xs font-bold flex items-center gap-1.5 shadow-md">
              <svg class="w-3.5 h-3.5 text-brand-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path>
              </svg>
              <span>{{ item.media.length }}</span>
            </div>
          </div>

          <!-- Content Section -->
          <div class="p-8 space-y-4">
             <div class="flex items-center gap-3 text-xs font-bold text-brand-gold/60 uppercase tracking-widest">
                <span>{{ formatDate(item.created_at) }}</span>
                <span v-if="item.location" class="flex items-center gap-1">
                   <span class="w-1 h-1 bg-slate-300 rounded-full"></span>
                   {{ item.location }}
                </span>
             </div>

             <h2 class="text-2xl font-serif font-bold text-slate-900 group-hover:text-brand-gold transition-colors leading-tight">
                {{ item.title }}
             </h2>

             <p class="text-slate-600 text-sm leading-relaxed font-medium line-clamp-4">
                {{ item.description }}
             </p>

             <div class="pt-4 flex items-center justify-between border-t border-slate-50">
                 <span class="text-sm font-bold text-slate-400 group-hover:text-brand-gold transition-colors">{{ t('newsEvents.card.readArticle') }} &rarr;</span>
                <div v-if="item.author_name" class="flex items-center gap-2">
                   <span class="text-[10px] font-bold text-slate-400 uppercase tracking-tight">{{ t('newsEvents.card.by', { name: item.author_name }) }}</span>
                </div>
             </div>
          </div>
        </div>
      </div>

      <!-- Loading More Trigger -->
      <div ref="loadMoreTrigger" class="h-20 flex items-center justify-center mt-12">
          <div v-if="loadingMore" class="flex gap-2">
             <div class="w-2 h-2 bg-brand-gold rounded-full animate-bounce"></div>
             <div class="w-2 h-2 bg-brand-gold rounded-full animate-bounce delay-100"></div>
             <div class="w-2 h-2 bg-brand-gold rounded-full animate-bounce delay-200"></div>
          </div>
      </div>
    </div>

    <!-- Details Modal (Facebook Card Format: Photo Left, Content Right) -->
    <Transition name="fade">
      <div v-if="selectedItem" class="fixed inset-0 z-50 flex items-center justify-center p-3 sm:p-6 overflow-hidden" @click.self="closeDetails">
        <div class="absolute inset-0 bg-black/75 backdrop-blur-sm" @click="closeDetails"></div>
        
        <div class="relative bg-white rounded-2xl max-w-5xl w-full max-h-[92vh] overflow-y-auto md:overflow-hidden shadow-2xl border border-slate-200 flex flex-col md:flex-row z-10">
          <!-- Mobile Close Button -->
          <button @click="closeDetails" class="md:hidden absolute top-3 right-3 z-20 p-2 bg-black/60 hover:bg-black/80 rounded-full text-white transition-colors" aria-label="Close modal">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>

          <!-- Left Side: Large Unobstructed Photo Viewer -->
          <div class="md:w-3/5 bg-slate-50 border-b md:border-b-0 md:border-r border-slate-100 relative flex flex-col justify-between items-center min-h-[320px] sm:min-h-[420px] md:min-h-[550px] md:max-h-[92vh] shrink-0 overflow-hidden">
            <div class="relative flex-1 w-full flex items-center justify-center p-2 sm:p-4 min-h-0">
              <img :src="resolveImage(activeModalImage) || 'https://placehold.co/800x1200/f1f5f9/d4af37?text=News'" :alt="selectedItem.title || t('newsEvents.modal.newsImageAlt')" class="w-full h-full max-h-[55vh] md:max-h-[76vh] object-contain select-none rounded-lg" />

              <!-- Prev / Next Controls -->
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
                  :alt="`${selectedItem.title} - ${idx + 1}`"
                  fetchpriority="low"
                  loading="lazy"
                  class="w-full h-full object-cover"
                />
              </button>
            </div>
          </div>

          <!-- Right Side: Content & Actions -->
          <div class="md:w-2/5 flex flex-col md:max-h-[92vh] bg-white">
            <div class="p-6 pb-4 border-b border-slate-100 flex items-start justify-between gap-4">
              <div class="space-y-2">
                <span 
                  class="inline-block px-3 py-1 text-[10px] font-black uppercase tracking-[0.2em] rounded-full border"
                  :class="selectedItem.is_auto_generated ? 'bg-amber-500/10 text-amber-600 border-amber-500/20' : 'bg-brand-gold/10 text-brand-gold border-brand-gold/10'"
                >
                  {{ getTypeLabel(selectedItem.type, selectedItem.is_auto_generated) }}
                </span>
                <h2 class="text-xl sm:text-2xl font-serif font-bold text-slate-900 leading-snug">{{ selectedItem.title }}</h2>
                <p class="text-xs font-bold text-slate-400 tracking-wide">{{ formatDate(selectedItem.created_at) }}</p>
              </div>
              <button @click="closeDetails" class="hidden md:flex p-2 bg-slate-100 hover:bg-slate-200 rounded-full text-slate-600 transition-colors shrink-0" aria-label="Close modal">
                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
              </button>
            </div>

            <div class="p-6 flex-1 overflow-y-auto">
              <div class="prose prose-slate max-w-none text-slate-700 font-sans leading-relaxed text-base sm:text-lg">
                <p class="whitespace-pre-wrap">{{ selectedItem.description }}</p>
              </div>
            </div>

            <div class="p-6 pt-4 border-t border-slate-100 bg-slate-50/50 flex flex-wrap items-center justify-between gap-3 mt-auto">
                <div v-if="selectedItem.author_name" class="flex flex-col">
                   <span class="text-[10px] font-black uppercase tracking-widest text-slate-400 mb-0.5">{{ t('newsEvents.modal.contributor') }}</span>
                   <span class="text-sm font-bold text-slate-900">{{ selectedItem.author_name }}</span>
                </div>
                <button 
                   v-if="selectedItem.type === 'event'"
                   @click="addToCalendar(selectedItem)"
                   class="bg-brand-gold text-white px-5 py-2 rounded-xl font-bold text-xs shadow-lg shadow-brand-gold/20"
                >
                   {{ t('newsEvents.modal.addToCalendar') }}
                </button>
                <div v-if="auth.isAuthenticated && (selectedItem.author_id === auth.user?.id || auth.user?.is_superuser)" class="flex gap-2">
                   <button 
                      @click="openEdit"
                      class="bg-slate-50 text-slate-600 px-5 py-2 rounded-xl font-bold text-xs border border-slate-200 hover:bg-slate-100 transition-colors"
                   >
                      {{ t('newsEvents.modal.edit') }}
                   </button>
                   <button 
                      @click="deletePost(selectedItem.id)"
                      class="bg-red-50 text-red-600 px-5 py-2 rounded-xl font-bold text-xs border border-red-100 hover:bg-red-100 transition-colors"
                   >
                      {{ t('newsEvents.modal.delete') }}
                   </button>
                </div>
            </div>
          </div>
        </div>
      </div>
    </Transition>

    <AddPostModal 
        v-if="auth.isAuthenticated"
        :is-open="isAddModalOpen"
        :type="selectedItem?.type || 'news'"
        :initial-data="editingItem"
        @close="closeAddModal"
        @refresh="refreshData"
    />
  </div>
</template>

<script setup lang="ts">
import { useRuntimeConfig, useHead, ref, onMounted, onUnmounted, useRoute } from '#imports'
import { useI18n } from 'vue-i18n'
import { computed, watch } from 'vue'
import AddPostModal from '~/components/AddPostModal.vue'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const config = useRuntimeConfig()
const route = useRoute()
const apiBase = config.public.apiBase || 'http://localhost:8000'
const { t, locale } = useI18n()
const activeDateLocale = computed(() => locale.value === 'ml' ? 'ml-IN' : 'en-US')

useHead(() => ({
  title: t('newsEvents.meta.title'),
  meta: [{ name: 'description', content: t('newsEvents.meta.description') }],
  link: [{ rel: 'canonical', href: `${config.public.siteUrl || 'http://localhost:3000'}${route.path}` }]
}))

interface NewsMediaItem {
  id: number
  media_url: string
  caption?: string
  media_type?: string
}

interface NewsItem {
  id: number
  title: string
  description: string
  image: string
  media?: NewsMediaItem[]
  type: 'news' | 'event'
  created_at: string
  location?: string
  author_name?: string
  author_id?: number
  is_auto_generated?: boolean
}

const items = ref<NewsItem[]>([])
const events = ref<any[]>([])
const loading = ref(true)
const loadingMore = ref(false)
const isAddModalOpen = ref(false)
const editingItem = ref<any | null>(null)
const selectedItem = ref<NewsItem | null>(null)
const activeImageIndex = ref(0)
const page = ref(1)
const hasMore = ref(true)
const loadMoreTrigger = ref<HTMLElement | null>(null)

const selectedMediaUrls = computed(() => {
  if (!selectedItem.value) return []
  const mediaList = (selectedItem.value.media || [])
    .map((m) => m.media_url)
    .filter(Boolean)
  if (mediaList.length > 0) return mediaList
  return selectedItem.value.image ? [selectedItem.value.image] : []
})

const activeModalImage = computed(() => {
  const urls = selectedMediaUrls.value
  if (urls.length === 0) return selectedItem.value?.image || ''
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

let observer: IntersectionObserver | null = null

const openDetails = (item: NewsItem) => {
  selectedItem.value = item
  activeImageIndex.value = 0
  document.body.style.overflow = 'hidden'
}

const closeDetails = () => {
  selectedItem.value = null
  activeImageIndex.value = 0
  document.body.style.overflow = ''
}

const openEdit = () => {
  editingItem.value = selectedItem.value
  isAddModalOpen.value = true
}

const closeAddModal = () => {
  isAddModalOpen.value = false
  editingItem.value = null
}

const getTypeLabel = (type?: string, isAuto?: boolean) => {
  if (isAuto) return 'Celebration'
  if (type === 'event') return t('shared.types.event')
  if (type === 'news') return t('shared.types.news')
  return t('shared.types.announcement')
}

const formatDate = (dateStr: string) => {
  return new Date(dateStr).toLocaleDateString(activeDateLocale.value, {
        month: 'long', 
        day: 'numeric',
        year: 'numeric'
    })
}

const resolveImage = (path: string) => {
    if (!path) return null
    if (path.startsWith('http')) return path
    const cleanPath = path.startsWith('/') ? path : `/${path}`
    return `${apiBase}${cleanPath}`
}

const checkPostQuery = () => {
  const postId = Number(route.query.post)
  if (!postId || items.value.length === 0) return
  const found = items.value.find((i) => i.id === postId)
  if (found) {
    openDetails(found)
  }
}

watch(() => route.query.post, () => {
  checkPostQuery()
})

const refreshData = async (loadMore = false) => {
    if (loadMore) {
        if (!hasMore.value || loadingMore.value) return
        loadingMore.value = true
        page.value++
    } else {
        loading.value = true
        page.value = 1
        items.value = []
    }

    try {
        const response = await fetch(`${apiBase}/api/news/list/?page=${page.value}`)
        if (response.ok) {
            const data = await response.json()
            
            // Fix: If backend doesn't send { results: [] }, it's a flat list.
            // If it's a flat list, we load it once and stop.
            const isPaginated = data.results !== undefined
            let newItems = isPaginated ? data.results : data
            
            newItems = newItems.map((item: any) => ({
                ...item,
                type: item.post_type || item.type,
                author_name: item.creator_name || item.author_name
            }))

            if (newItems.length === 0 || !isPaginated) {
                hasMore.value = false
            }
            
            // If flat list, replace instead of append on first load to prevent duplication
            if (!isPaginated) {
                items.value = newItems
            } else {
                items.value = [...items.value, ...newItems]
                if (newItems.length < 10) hasMore.value = false
            }
            checkPostQuery()
        }
    } catch (e) {
        console.error("Failed to fetch news", e)
        hasMore.value = false
    } finally {
        loading.value = false
        loadingMore.value = false
    }
}

const addToCalendar = (item: any) => {
    if(!item || item.type !== 'event') return
    const eventDate = item.event_date || item.created_at
    const start = new Date(eventDate)
    const end = new Date(start.getTime() + 60 * 60 * 1000)

    const formatDateStr = (date: Date) => date.toISOString().replace(/-|:|\.\d\d\d/g, "")

    const url = new URL("https://www.google.com/calendar/render")
    url.searchParams.append("action", "TEMPLATE")
    url.searchParams.append("text", item.title)
    url.searchParams.append("dates", `${formatDateStr(start)}/${formatDateStr(end)}`)
    url.searchParams.append("details", item.description)
    if (item.location) url.searchParams.append("location", item.location)

    window.open(url.toString(), "_blank")
}

function getCookie(name: string) {
  if (typeof document === 'undefined') return null
  const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
  return matches ? matches[2] : null
}

const deletePost = async (id: number) => {
    if (!confirm(t('newsEvents.alerts.confirmDelete'))) return
    
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
            // Reset and reload
            items.value = []
            page.value = 1
            hasMore.value = true
            await refreshData()
        } else {
            alert(t('newsEvents.alerts.deleteFailed'))
        }
    } catch (e) {
        console.error("Delete failed", e)
    }
}

onMounted(() => {
    refreshData()
    
    // Intersection Observer for Lazy Loading
    observer = new IntersectionObserver((entries) => {
        if (entries[0]?.isIntersecting && hasMore.value) {
            refreshData(true)
        }
    }, { threshold: 0.1 })

    if (loadMoreTrigger.value) observer.observe(loadMoreTrigger.value)
})

onUnmounted(() => {
    if (observer) observer.disconnect()
})
</script>

<style scoped>
.fade-enter-active, .fade-leave-active { transition: opacity 0.5s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }

.break-inside-avoid {
  break-inside: avoid;
}
</style>
