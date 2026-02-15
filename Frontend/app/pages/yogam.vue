<template>
   <div class="min-h-screen bg-slate-50 text-slate-800 pt-32 pb-16 px-4 sm:px-6 lg:px-8 font-sans selection:bg-brand-gold selection:text-white">
    <!-- Header Section -->
    <div class="max-w-7xl mx-auto mb-16 text-center space-y-4">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
            Annual Kudumbayogam
        </h1>
        <div class="h-1.5 w-32 bg-brand-gold mx-auto rounded-full"></div>
        <p class="text-lg text-slate-500 max-w-xl mx-auto font-medium">
            Stay updated with the highlights and schedules of our annual family gatherings, bringing everyone together in celebration.
        </p>
        
        <div v-if="auth.isAuthenticated" class="pt-6 flex justify-center">
            <button 
                @click="isAddModalOpen = true"
                class="bg-brand-gold text-white px-8 py-3 rounded-2xl font-bold shadow-lg shadow-brand-gold/20 hover:scale-105 active:scale-95 transition-all flex items-center gap-2"
            >
                <span class="text-xl leading-none">+</span> Add Highlight
            </button>
        </div>
    </div>

    <!-- Events Grid -->
    <div class="max-w-7xl mx-auto grid grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-8 lg:gap-10">
      
      <!-- Skeleton Cards -->
      <template v-if="loading">
        <div v-for="n in 6" :key="n" class="bg-white h-[450px] rounded-xl overflow-hidden shadow-sm border border-slate-200 animate-pulse">
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
          class="group relative flex flex-col bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl border border-slate-200 transition-all duration-300 hover:-translate-y-1 cursor-pointer"
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
            <div class="absolute top-4 left-4 bg-white/90 backdrop-blur-md border border-slate-200 rounded-lg p-3 text-center min-w-[70px] shadow-lg">
              <span class="block text-xs font-bold uppercase tracking-wider text-brand-gold mb-0.5">{{ getMonth(event.event_date) }}</span>
              <span class="block text-2xl font-serif font-bold text-slate-900 leading-none">{{ getDay(event.event_date) }}</span>
            </div>
          </div>

          <!-- Content -->
          <div class="flex-1 p-6 flex flex-col relative text-left">
            <div class="flex items-center gap-4 text-xs font-medium text-brand-gold mb-3 tracking-wide uppercase">
              <div v-if="event.location" class="flex items-center gap-1.5">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path></svg>
                {{ event.location }}
              </div>
            </div>

            <h2 class="text-2xl font-serif font-bold text-slate-900 mb-3 group-hover:text-brand-gold transition-colors">
              {{ event.title }}
            </h2>
            
            <p class="text-slate-600 text-sm leading-relaxed mb-6 line-clamp-3 font-medium">
              {{ event.description }}
            </p>

            <div class="mt-auto pt-4 border-t border-slate-100">
               <button class="text-sm font-semibold text-slate-700 group-hover:text-brand-gold transition-colors flex items-center gap-2">
                   View Highlights
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
          <h3 class="text-xl font-serif text-slate-800 mb-2">No Yogam History Yet</h3>
          <p class="text-slate-500 text-sm">Highlights of our annual gatherings will appear here.</p>
        </div>
      </template>
    </div>

    <!-- Details Modal -->
    <Transition name="fade">
      <div v-if="selectedEvent" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="closeDetails">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
        
        <div class="relative bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200 flex flex-col">
          <button @click="closeDetails" class="absolute top-4 right-4 z-10 p-2 bg-black/10 hover:bg-black/20 rounded-full text-white transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>

          <div class="relative h-64 sm:h-80 shrink-0">
            <img :src="resolveImage(selectedEvent.image) || 'https://placehold.co/800x600/f1f5f9/d4af37?text=Annual+Meeting'" class="w-full h-full object-cover" />
            <div class="absolute inset-0 bg-linear-to-t from-black/60 to-transparent"></div>
            
             <div class="absolute bottom-4 left-6">
                <span class="inline-block px-3 py-1 bg-brand-gold text-white text-xs font-bold uppercase tracking-wider rounded-md mb-2">
                  {{ getMonth(selectedEvent.event_date) }} {{ getDay(selectedEvent.event_date) }}, {{ getYear(selectedEvent.event_date) }}
                </span>
                <h2 class="text-3xl font-serif font-bold text-white drop-shadow-md">{{ selectedEvent.title }}</h2>
             </div>
          </div>

          <div class="p-6 space-y-6">
             <div v-if="selectedEvent.location" class="flex items-center gap-2 text-sm text-slate-600 border-b border-slate-100 pb-6 font-medium">
               <svg class="w-5 h-5 text-brand-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path></svg>
               {{ selectedEvent.location }}
             </div>

             <div class="prose prose-slate max-w-none text-slate-800 font-sans leading-loose text-lg">
                <p class="font-medium whitespace-pre-wrap">{{ selectedEvent.description }}</p>
             </div>

             <div v-if="auth.isAuthenticated && (selectedEvent.author_id === auth.user?.id || auth.user?.is_superuser)" class="pt-6 border-t border-slate-100 flex justify-end gap-2">
                <button 
                   @click="openEdit"
                   class="bg-slate-50 text-slate-600 px-6 py-2.5 rounded-xl font-bold text-xs border border-slate-200 hover:bg-slate-100 transition-colors"
                >
                   Edit
                </button>
                <button 
                   @click="deletePost(selectedEvent.id)"
                   class="bg-red-50 text-red-600 px-6 py-2.5 rounded-xl font-bold text-xs border border-red-100 hover:bg-red-100 transition-colors"
                >
                   Delete
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
import { useRuntimeConfig, useHead, ref, onMounted } from '#imports'
import AddPostModal from '~/components/AddPostModal.vue'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'

interface EventItem {
  id: number
  title: string
  description: string
  image: string
  event_date: string
  location?: string
  author_name?: string
  author_id?: number
}

const events = ref<EventItem[]>([])
const loading = ref(true)
const isAddModalOpen = ref(false)
const editingEvent = ref<EventItem | null>(null)
const selectedEvent = ref<EventItem | null>(null)

const openDetails = (event: EventItem) => {
  selectedEvent.value = event
  document.body.style.overflow = 'hidden'
}

const closeDetails = () => {
  selectedEvent.value = null
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

const getMonth = (dateStr: string) => new Date(dateStr).toLocaleString('default', { month: 'short' })
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
        // We might want a specific category for Kudumbayogam in the future
        // For now, we fetch all events and perhaps filter on the frontend if needed
        const response = await fetch(`${apiBase}/api/news/events/`)
        if (response.ok) {
            const allEvents = await response.json()
            // Filter strategy: Use the explicit boolean flag
            events.value = allEvents.filter((e: any) => e.is_kudumbayogam)
            
            // Fallback: If no explicit flags found, try string matching as backup for older posts
            if (events.value.length === 0) {
                 events.value = allEvents.filter((e: any) => 
                    e.title.toLowerCase().includes('yogam') || 
                    e.description.toLowerCase().includes('yogam')
                 )
            }
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
    if (!confirm('Are you sure you want to delete this highlight?')) return
    
    try {
        await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
        const csrftoken = getCookie('csrftoken')
        
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
            alert('Failed to delete')
        }
    } catch (e) {
        console.error("Delete failed", e)
    }
}

onMounted(() => {
    refreshEvents()
})

useHead({
  title: 'Annual Kudumbayogam - Kollaparambil Family',
})
</script>
