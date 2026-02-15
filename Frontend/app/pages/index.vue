<template>
  <div class="min-h-screen bg-slate-50 font-sans text-slate-800 overflow-x-hidden">
    <!-- Hero Section -->
    <div class="relative w-full h-[110vh] overflow-hidden">
      <!-- Background Image -->
      <img src="/images/family.jpg" alt="Family Gathering" class="absolute inset-0 w-full h-full object-cover" />
      
      <div class="absolute inset-0 bg-linear-to-b from-black/30 via-black/60 to-slate-50"></div>

      <!-- Hero Content -->
      <div class="absolute top-0 left-0 w-full h-screen flex flex-col items-center md:items-start justify-end px-4 pb-40 md:px-24 md:pb-24">
        
        <div class="bg-black/80 backdrop-blur-md shadow-[0_0_40px_40px_rgba(0,0,0,0.8)] absolute left-0 bottom-0 p-8 md:p-10 rounded-tr-3xl max-w-3xl text-center md:text-left">
            <h1 class="font-fleur text-6xl md:text-8xl lg:text-8xl lg:text-nowrap text-white mb-4 drop-shadow-2xl mx-auto md:mx-0 leading-tight">
                Kollamparambil Family
            </h1>

            <!-- Malayalam Verse -->
            <div class="flex flex-col mt-2">
                <p class="text-sm md:text-base font-bold text-white leading-relaxed drop-shadow-md">
                    "മക്കളുടെ മക്കള്‍ വൃദ്ധന്മാര്‍ക്കും കിരീടമാകുന്നു; മക്കളുടെ മഹത്വം അവരുടെ അപ്പന്മാര്‍ തന്നേ."
                </p>
                <p class="text-xs md:text-sm text-gray-300 mt-1 font-medium place-self-end">
                    - സദൃശ്യവാക്യങ്ങൾ 17:6
                </p>
            </div>
        </div>

      </div>
    </div>

    <!-- Navigation Buttons (Intersection Layout) -->
    <div class="relative z-20 -mt-12 px-4 md:px-12 pb-20 md:pb-12">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-3 md:gap-4 max-w-6xl mx-auto">
            
            <!-- Button 1: Committee Members (Public) -->
            <NuxtLink 
                to="/committee" 
                class="group relative h-32 md:h-40 rounded-xl overflow-hidden shadow-2xl transition-transform hover:-translate-y-1 bg-white border border-slate-100"
            >
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-3">
                    <h3 class="text-lg md:text-xl font-bold text-slate-800 uppercase tracking-wide leading-tight group-hover:text-brand-gold transition-colors">Committee<br>Members</h3>
                </div>
            </NuxtLink>

            <!-- Button 2: Events (Public) -->
            <NuxtLink to="/news-events" class="group relative h-32 md:h-40 rounded-xl overflow-hidden shadow-2xl transition-transform hover:-translate-y-1 bg-linear-to-b from-brand-gold to-brand-gold-dark">
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-3">
                    <h3 class="text-lg md:text-xl font-bold text-white uppercase tracking-wide leading-tight">Events & News</h3>
                </div>
            </NuxtLink>

            <!-- Button 3: Annual Kudumbayogam (Restricted) -->
             <div 
                @click="handleRestrictedNavigation('/yogam')"
                class="group relative h-32 md:h-40 rounded-xl overflow-hidden shadow-2xl transition-transform hover:-translate-y-1 cursor-pointer bg-white border border-slate-100"
            >
                <div class="absolute inset-0 flex flex-col items-center justify-center text-center p-3">
                    <h3 class="text-lg md:text-xl font-bold text-slate-800 uppercase tracking-wide leading-tight group-hover:text-brand-gold transition-colors">Annual<br>Kudumbayogam</h3>
                </div>
            </div>

        </div>
    </div>

    <!-- News Section -->
    <div class="bg-slate-50 py-16 px-4 md:px-12">
        <div class="max-w-7xl mx-auto">
            <div class="flex flex-col md:flex-row md:items-end justify-between mb-10 gap-4">
                <div class="space-y-2">
                    <h2 class="text-3xl md:text-5xl font-serif font-bold text-slate-900 drop-shadow-sm">
                        Latest News & Events
                    </h2>
                    <div class="h-1.5 w-24 bg-brand-gold rounded-full"></div>
                </div>
                <div class="flex flex-wrap items-center gap-4 self-start md:self-auto shrink-0">
                    <NuxtLink 
                      to="/news-events"
                      class="bg-white border-2 border-brand-gold text-brand-gold hover:bg-brand-gold hover:text-white px-6 py-2.5 rounded-full font-bold text-sm transition-all flex items-center gap-2 shadow-md active:scale-95"
                    >
                      View All
                    </NuxtLink>

                    <button 
                      v-if="auth.isAuthenticated"
                      @click="isAddModalOpen = true"
                      class="bg-linear-to-b from-brand-gold to-brand-gold-dark hover:brightness-110 text-white px-6 py-2.5 rounded-full font-bold text-sm transition-all flex items-center gap-2 shadow-lg active:scale-95 shrink-0"
                    >
                      <span class="text-xl leading-none">+</span> Add News
                    </button>
                </div>
            </div>
            
            <!-- Horizontal Scroll Container -->
            <div class="flex overflow-x-auto gap-6 pb-8 snap-x custom-scrollbar">
                
                <!-- Skeleton News Cards -->
                <template v-if="newsList.length === 0">
                    <div v-for="n in 4" :key="n" class="snap-start min-w-[260px] w-[260px] bg-white rounded-xl overflow-hidden shadow-sm border border-slate-200 shrink-0 animate-pulse">
                        <div class="h-36 bg-slate-200"></div>
                        <div class="p-5 space-y-3">
                            <div class="h-4 bg-slate-200 rounded w-3/4"></div>
                            <div class="h-3 bg-slate-200 rounded w-full"></div>
                            <div class="h-3 bg-slate-200 rounded w-5/6"></div>
                        </div>
                    </div>
                </template>

                <!-- Real News Card -->
                <div 
                    v-else
                    v-for="item in newsList" 
                    :key="item.id" 
                    @click="openDetails(item)"
                    class="snap-start min-w-[260px] w-[260px] bg-white rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-all cursor-pointer shrink-0 group hover:-translate-y-1 border border-slate-200"
                >
                    <div class="relative h-36 overflow-hidden">
                        <img :src="resolveImage(item.image) || 'https://placehold.co/600x400/f1f5f9/64748b?text=News'" :alt="item.title" class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500" />
                        <div v-if="item.type === 'event'" class="absolute top-2 right-2 bg-brand-gold text-white text-xs font-bold px-2 py-0.5 rounded shadow">
                            EVENT
                        </div>
                    </div>
                    <div class="p-5">
                        <h3 class="text-xl font-bold text-slate-900 mb-2 line-clamp-2 leading-tight group-hover:text-brand-gold-dark transition-colors">{{ item.title }}</h3>
                        <p class="text-slate-600 text-sm line-clamp-2 leading-relaxed font-medium">{{ item.description }}</p>
                        <div class="mt-3 flex justify-between items-center">
                            <span class="text-xs text-slate-400 uppercase tracking-wider">{{ getDay(item.created_at) }} {{ getMonth(item.created_at) }}</span>
                            <span class="text-brand-gold text-xs font-bold uppercase tracking-wide group-hover:underline">Read More</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Details Modal -->
    <Transition name="fade">
        <div v-if="selectedItem" class="fixed inset-0 z-50 flex items-center justify-center p-4" @click.self="closeDetails">
            <div class="absolute inset-0 bg-black/60 backdrop-blur-sm"></div>

            <div class="relative bg-white rounded-2xl max-w-2xl w-full max-h-[90vh] overflow-y-auto shadow-2xl border border-slate-200 flex flex-col">
                <!-- Close Button -->
                <button @click="closeDetails" class="absolute top-4 right-4 z-10 p-2 bg-black/10 hover:bg-black/20 rounded-full text-white transition-colors">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path>
                    </svg>
                </button>

                <!-- Modal Image -->
                <div class="relative h-64 sm:h-80 shrink-0">
                    <img :src="resolveImage(selectedItem.image) || 'https://placehold.co/800x600/f1f5f9/d4af37?text=News'" class="w-full h-full object-cover" />
                    <div class="absolute inset-0 bg-linear-to-t from-black/60 to-transparent"></div>

                    <div class="absolute bottom-4 left-6">
                        <span class="inline-block px-3 py-1 bg-brand-gold text-white text-xs font-bold uppercase tracking-wider rounded-md mb-2">
                            {{ getMonth(selectedItem.created_at) }} {{ getDay(selectedItem.created_at) }}, {{ getYear(selectedItem.created_at) }}
                        </span>
                        <h2 class="text-3xl font-serif font-bold text-white leading-tight mt-1 drop-shadow-md">{{ selectedItem.title }}</h2>
                        <p v-if="selectedItem.author_name" class="text-brand-gold/70 text-sm mt-1 font-medium">Posted by {{ selectedItem.author_name }}</p>
                    </div>
                </div>

                <!-- Modal Body -->
                <div class="p-6 space-y-6">
                    <!-- Description -->
                    <div class="prose prose-slate max-w-none text-slate-800 font-sans leading-loose text-lg">
                        <p class="font-medium">{{ selectedItem.description }}</p>
                        <p class="opacity-75">Full article content would go here. Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.</p>
                    </div>

                    <!-- Actions -->
                    <div class="pt-4 border-t border-slate-100 flex items-center justify-between">
                         <div class="flex items-center gap-4">
                             <span class="text-sm text-slate-400 uppercase font-bold tracking-wider">Share:</span>
                             <ShareButtons :title="selectedItem.title" :description="selectedItem.description" />
                         </div>
                         
                         <!-- Delete Button -->
                         <button 
                            v-if="auth.isAuthenticated && selectedItem.author_id === auth.user?.id"
                            @click="deleteNews(selectedItem.id)"
                            class="bg-red-50 text-red-600 hover:bg-red-100 px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-widest transition-colors border border-red-100"
                        >
                            Delete Post
                        </button>
                    </div>
                </div>
            </div>
        </div>
    </Transition>

    <!-- Add Post Modal -->
    <AddPostModal 
        v-if="auth.isAuthenticated"
        :is-open="isAddModalOpen"
        type="news"
        @close="isAddModalOpen = false"
        @refresh="refreshNews"
    />

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useHead, useRuntimeConfig, navigateTo } from '#imports'
import { useAuthStore } from '~/stores/auth'
import ShareButtons from '~/components/ShareButtons.vue'
import AddPostModal from '~/components/AddPostModal.vue'

const auth = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'

const isAddModalOpen = ref(false)

interface NewsItem {
  id: number;
  title: string;
  description: string;
  image: string;
  created_at: string;
  type: 'news' | 'event';
  author_name?: string;
  author_id?: number;
}

const newsList = ref<NewsItem[]>([])
const selectedItem = ref<NewsItem | null>(null)

const openDetails = (item: NewsItem) => {
  selectedItem.value = item
  document.body.style.overflow = 'hidden'
}

const closeDetails = () => {
  selectedItem.value = null
  document.body.style.overflow = ''
}

// Helpers
const getMonth = (dateStr: string) => new Date(dateStr).toLocaleString('default', { month: 'short' })
const getDay = (dateStr: string) => new Date(dateStr).getDate()
const getYear = (dateStr: string) => new Date(dateStr).getFullYear()

const resolveImage = (path: string) => {
    if (!path) return null
    if (path.startsWith('http')) return path
    return `${apiBase}${path}`
}

const handleRestrictedNavigation = (path: string) => {
    if (auth.isAuthenticated) {
        navigateTo(path)
    } else {
        alert("You need to be logged in to access this section.")
    }
}

function getCookie(name: string) {
  if (typeof document === 'undefined') return null
  const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
  return matches ? matches[2] : null
}

const refreshNews = async () => {
    try {
    const response = await fetch(`${apiBase}/api/news/list/`)
    if (response.ok) {
        newsList.value = await response.json()
    }
  } catch (e) {
    console.error("Failed to fetch news", e)
  }
}

const deleteNews = async (id: number) => {
    if (!confirm('Are you sure you want to delete this?')) return
    
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
            refreshNews()
        } else {
            alert('Failed to delete')
        }
    } catch (e) {
        console.error("Delete failed", e)
    }
}

onMounted(() => {
    refreshNews()
})

useHead({
  title: 'Home'
})
</script>

<style scoped>
/* Animations */
@keyframes slide-up {
  from { transform: translateY(20px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
.animate-slide-up {
  animation: slide-up 0.8s ease-out forwards;
}

@keyframes fade-up {
  from { transform: translateY(15px); opacity: 0; }
  to { transform: translateY(0); opacity: 1; }
}
.animate-fade-up {
  animation: fade-up 0.6s ease-out forwards;
  opacity: 0; /* ensure hidden initially */
}
.animate-fade-up-stagger {
  animation: fade-up 0.6s ease-out forwards;
  opacity: 0;
}

@keyframes fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}
.animate-fade-in {
  animation: fade-in 1s ease-out forwards;
}
</style>