<template>
  <div class="min-h-screen bg-slate-100 text-slate-800 pt-32 pb-16 px-4 sm:px-6 lg:px-8 font-sans selection:bg-amber-500 selection:text-white">
    <!-- Header Section -->
    <div class="max-w-7xl mx-auto text-center mb-20 relative">
      <h1 class="text-4xl md:text-5xl font-serif font-medium tracking-tight text-slate-900 mb-6">
        Upcoming Gatherings
      </h1>
      <div class="h-1 w-24 bg-amber-500 mx-auto rounded-full mb-6"></div>
      <p class="text-lg md:text-xl text-slate-500 max-w-2xl mx-auto leading-relaxed">
        Join our family in fellowship and celebration. Save the date for these upcoming moments together.
      </p>
      
      <!-- Add Event Button -->
      <button 
        v-if="auth.isAuthenticated"
        @click="isAddModalOpen = true"
        class="absolute right-0 top-0 hidden md:flex bg-amber-500 hover:bg-amber-600 text-white px-6 py-2 rounded-xl font-bold transition-all shadow-md hover:shadow-lg active:scale-95 items-center gap-2"
      >
        <span class="text-xl">+</span> Add Event
      </button>

      <!-- Mobile Add Button -->
      <button 
        v-if="auth.isAuthenticated"
        @click="isAddModalOpen = true"
        class="md:hidden mt-6 bg-amber-500 hover:bg-amber-600 text-white px-6 py-2 rounded-xl font-bold transition-all shadow-md items-center gap-2 inline-flex"
      >
        <span class="text-xl">+</span> Add Event
      </button>
    </div>

    <!-- Events Grid -->
    <div class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
      
      <!-- Event Card -->
      <div 
        v-for="event in events" 
        :key="event.id" 
        @click="openDetails(event)"
        class="group relative flex flex-col bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl border border-slate-200 transition-all duration-300 hover:-translate-y-1 cursor-pointer"
      >
        <!-- Image & Date -->
        <div class="relative aspect-4/3 overflow-hidden">
          <img 
            :src="resolveImage(event.image) || 'https://placehold.co/800x600/f1f5f9/d4af37?text=Event'" 
            :alt="event.title" 
            class="w-full h-full object-cover transition-transform duration-700 group-hover:scale-110" 
          />
          <div class="absolute inset-0 bg-linear-to-t from-black/40 via-transparent to-transparent opacity-60"></div>
          
          <!-- Floating Date Badge -->
          <div class="absolute top-4 left-4 bg-white/90 backdrop-blur-md border border-slate-200 rounded-lg p-3 text-center min-w-[70px] shadow-lg">
            <span class="block text-xs font-bold uppercase tracking-wider text-amber-600 mb-0.5">{{ getMonth(event.event_date) }}</span>
            <span class="block text-2xl font-serif font-bold text-slate-900 leading-none">{{ getDay(event.event_date) }}</span>
          </div>
        </div>

        <!-- Content -->
        <div class="flex-1 p-6 flex flex-col relative">
          <!-- Meta Info -->
          <div class="flex items-center gap-4 text-xs font-medium text-amber-600 mb-3 tracking-wide uppercase">
            <div v-if="event.location" class="flex items-center gap-1.5">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
              {{ event.location }}
            </div>
            <div class="flex items-center gap-1.5">
              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
              {{ getTime(event.event_date) }}
            </div>
          </div>

          <h2 class="text-2xl font-serif font-medium text-slate-800 mb-3 group-hover:text-amber-600 transition-colors">
            {{ event.title }}
          </h2>
          
          <p class="text-slate-500 text-sm leading-relaxed mb-6 line-clamp-3">
            {{ event.description }}
          </p>

          <div class="mt-auto pt-4 border-t border-slate-100 flex items-center justify-between">
             <button class="text-sm font-semibold text-slate-700 group-hover:text-amber-600 transition-colors flex items-center gap-2">
                View Details
                <svg class="w-4 h-4 transition-transform group-hover:translate-x-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
             </button>
             <button @click.stop="addToCalendar(event)" class="text-xs bg-slate-100 hover:bg-slate-200 px-3 py-1.5 rounded-full text-slate-600 transition-colors border border-slate-200">
                Add to Calendar
             </button>
          </div>
        </div>
      </div>

    </div>

    <!-- Empty State -->
    <div v-if="events.length === 0 && !loading" class="max-w-md mx-auto mt-20 text-center p-10 bg-white rounded-2xl border border-slate-200 shadow-sm">
       <svg class="w-16 h-16 text-slate-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
       <h3 class="text-xl font-serif text-slate-800 mb-2">No Upcoming Events</h3>
       <p class="text-slate-500 text-sm">We are currently planning our next gathering. Check back soon.</p>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="max-w-7xl mx-auto grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
        <div v-for="n in 3" :key="n" class="bg-white h-[500px] rounded-xl animate-pulse border border-slate-200"></div>
    </div>

    <!-- Details Modal -->
    <Transition name="fade">
      <div v-if="selectedEvent" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="closeDetails">
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>
        
        <div class="relative bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200 flex flex-col">
          <!-- Close Button -->
          <button @click="closeDetails" class="absolute top-4 right-4 z-10 p-2 bg-black/10 hover:bg-black/20 rounded-full text-white transition-colors">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
          </button>

          <!-- Modal Image -->
          <div class="relative h-64 sm:h-80 shrink-0">
            <img :src="resolveImage(selectedEvent.image) || 'https://placehold.co/800x600/f1f5f9/d4af37?text=Event'" class="w-full h-full object-cover" />
            <div class="absolute inset-0 bg-linear-to-t from-black/60 to-transparent"></div>
            
             <div class="absolute bottom-4 left-6">
                <span class="inline-block px-3 py-1 bg-amber-500 text-white text-xs font-bold uppercase tracking-wider rounded-md mb-2">
                  {{ getMonth(selectedEvent.event_date) }} {{ getDay(selectedEvent.event_date) }}
                </span>
                <h2 class="text-3xl font-serif font-bold text-white drop-shadow-md">{{ selectedEvent.title }}</h2>
                <p v-if="selectedEvent.author_name" class="text-amber-200 text-sm mt-1 font-medium">Organized by {{ selectedEvent.author_name }}</p>
             </div>
          </div>

          <!-- Modal Body -->
          <div class="p-6 space-y-6">
             <!-- Info Row -->
             <div class="flex flex-wrap gap-6 text-sm text-slate-600 border-b border-slate-100 pb-6 font-medium">
                <div class="flex items-center gap-2">
                   <svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                   {{ new Date(selectedEvent.event_date).toLocaleDateString(undefined, { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' }) }}
                </div>
                 <div class="flex items-center gap-2">
                   <svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                   {{ getTime(selectedEvent.event_date) }}
                </div>
                 <div v-if="selectedEvent.location" class="flex items-center gap-2">
                   <svg class="w-5 h-5 text-amber-500" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
                   {{ selectedEvent.location }}
                </div>
             </div>

             <!-- Description -->
             <div class="prose prose-slate max-w-none text-slate-600">
                <p>{{ selectedEvent.description }}</p>
                <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.</p>
             </div>

             <!-- Actions -->
             <div class="pt-4 flex flex-col gap-4">
               <button @click="addToCalendar(selectedEvent)" class="w-full bg-amber-500 hover:bg-amber-600 text-white font-bold py-3 rounded-lg transition-colors shadow-md">
                  Add to Calendar
               </button>
               
               <div class="flex items-center justify-between border-t border-slate-100 pt-4">
                  <div class="flex items-center gap-4">
                     <span class="text-sm text-slate-400 uppercase font-bold tracking-wider">Share Event:</span>
                     <ShareButtons :title="selectedEvent.title" :description="selectedEvent.description" />
                  </div>

                  <!-- Delete Button -->
                  <button 
                    v-if="selectedEvent.author_id === auth.user?.id"
                    @click="deleteEvent(selectedEvent.id)"
                    class="text-red-500 hover:text-red-700 text-sm font-bold uppercase tracking-wide hover:underline"
                  >
                    Delete
                  </button>
               </div>
             </div>
          </div>
        </div>
      </div>
    </Transition>

    <!-- Add Post Modal -->
    <AddPostModal 
        v-if="auth.isAuthenticated"
        :is-open="isAddModalOpen"
        type="event"
        @close="isAddModalOpen = false"
        @refresh="refreshEvents"
    />

  </div>
</template>

<script setup lang="ts">
import { useRuntimeConfig, useHead } from '#imports'
import ShareButtons from '~/components/ShareButtons.vue'
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

const selectedEvent = ref<EventItem | null>(null)

const openDetails = (event: EventItem) => {
  selectedEvent.value = event
  document.body.style.overflow = 'hidden' // Prevent background scrolling
}

const closeDetails = () => {
  selectedEvent.value = null
  document.body.style.overflow = ''
}

// Date Helpers
const getMonth = (dateStr: string) => new Date(dateStr).toLocaleString('default', { month: 'short' })
const getDay = (dateStr: string) => new Date(dateStr).getDate()
const getTime = (dateStr: string) => new Date(dateStr).toLocaleTimeString('default', { hour: '2-digit', minute: '2-digit' })

const resolveImage = (path: string) => {
    if (!path) return null
    if (path.startsWith('http')) return path
    return `${apiBase}${path}`
}

function getCookie(name: string) {
  if (typeof document === 'undefined') return null
  const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
  return matches ? matches[2] : null
}

const refreshEvents = async () => {
    loading.value = true
    try {
    const response = await fetch(`${apiBase}/api/news/events/`)
    if (response.ok) {
        events.value = await response.json()
    }
  } catch (e) {
    console.error("Failed to fetch events", e)
  } finally {
    loading.value = false
  }
}

const addToCalendar = (event: EventItem | null) => {
    if(!event) return
    const start = new Date(event.event_date)
    const end = new Date(start.getTime() + 60 * 60 * 1000) // 1 hour duration

    const formatDate = (date: Date) => date.toISOString().replace(/-|:|\.\d\d\d/g, "")

    const url = new URL("https://www.google.com/calendar/render")
    url.searchParams.append("action", "TEMPLATE")
    url.searchParams.append("text", event.title)
    url.searchParams.append("dates", `${formatDate(start)}/${formatDate(end)}`)
    url.searchParams.append("details", event.description)
    if (event.location) url.searchParams.append("location", event.location)

    window.open(url.toString(), "_blank")
}

const deleteEvent = async (id: number) => {
    if (!confirm('Are you sure you want to delete this event?')) return
    
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
  title: 'Events - Kollaparambil Family',
})
</script>
