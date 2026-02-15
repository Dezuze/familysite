<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 font-sans pt-32 pb-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <!-- Header -->
      <div class="max-w-7xl mx-auto mb-16 text-center space-y-4">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
            Committee Members
        </h1>
        <div class="h-1.5 w-32 bg-brand-gold mx-auto rounded-full"></div>
        <p class="text-lg text-slate-500 max-w-xl mx-auto font-medium">
            Term 2025 - 2027
        </p>
      </div>

      <!-- Controls -->
      <div class="flex justify-center mb-10">
        <div class="relative w-full max-w-md">
           <input v-model="query" type="search" placeholder="Search committee..." 
                  class="w-full pl-10 pr-4 py-3 rounded-full bg-white border border-slate-200 text-slate-900 placeholder-slate-400 focus:ring-2 focus:ring-brand-gold focus:border-transparent outline-none shadow-md transition-all" />
           <svg class="w-5 h-5 text-slate-400 absolute left-3 top-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
        </div>
      </div>

      <!-- Custom Grid -->
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <!-- Skeleton Grid -->
        <template v-if="loading">
          <div v-for="n in 6" :key="n" class="bg-white rounded-2xl overflow-hidden shadow-sm border border-slate-200 animate-pulse">
            <div class="h-64 sm:h-72 bg-slate-200"></div>
            <div class="p-4 space-y-3">
              <div class="h-6 bg-slate-200 rounded w-1/2"></div>
              <div class="h-4 bg-slate-200 rounded w-1/3"></div>
            </div>
          </div>
        </template>

        <!-- Real Committee Cards -->
        <template v-else-if="filtered.length > 0">
          <div 
            v-for="m in filtered" 
            :key="m.id"
            class="group relative"
          >
            <!-- Card Container with Glassmorphism -->
            <div 
              class="relative bg-white/90 backdrop-blur-md rounded-3xl overflow-hidden shadow-xl border transition-all duration-500 hover:-translate-y-2 hover:shadow-2xl flex flex-col h-full"
              :class="getPriority(m.role) <= 6 ? 'border-brand-gold/40 ring-1 ring-brand-gold/10' : 'border-slate-200'"
            >
              <!-- Image Section -->
              <div class="h-64 w-full relative overflow-hidden bg-slate-50">
                <img 
                  v-if="m.photo" 
                  :src="m.photo" 
                  class="w-full h-full object-cover object-top transition-transform duration-700 group-hover:scale-110" 
                />
                <div v-else class="w-full h-full flex items-center justify-center bg-linear-to-b from-slate-100 to-slate-200 text-brand-gold/20">
                    <span class="text-6xl font-serif font-bold select-none">{{ m.name.charAt(0) }}</span>
                </div>
                
                <!-- Premium Overlays -->
                <div class="absolute inset-x-0 bottom-0 h-40 bg-linear-to-t from-black/70 via-black/30 to-transparent"></div>
                
                <!-- Role Badge (Floating) -->
                <div class="absolute top-4 right-4 animate-in fade-in zoom-in duration-700">
                    <span 
                      class="px-4 py-1.5 rounded-full text-[10px] font-bold uppercase tracking-widest shadow-lg backdrop-blur-md border"
                      :class="getPriority(m.role) <= 6 
                         ? 'bg-brand-gold text-white border-brand-gold-dark' 
                         : 'bg-white/90 text-slate-800 border-slate-200'"
                    >
                      {{ m.role || 'Member' }}
                    </span>
                </div>

                <!-- Profile Link Hover Overlay -->
                <div class="absolute inset-0 bg-brand-gold/10 opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none flex items-center justify-center">
                    <div class="w-12 h-12 bg-white/20 backdrop-blur-md rounded-full flex items-center justify-center border border-white/40 scale-50 group-hover:scale-100 transition-transform duration-500">
                        <svg class="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M12 4v16m8-8H4"></path></svg>
                    </div>
                </div>
              </div>
              
              <!-- Info Section -->
              <div class="p-5 flex-1 flex flex-col justify-between relative">
                <!-- Name & Title -->
                <div>
                  <h3 class="text-xl font-serif font-bold text-slate-900 leading-tight mb-1 group-hover:text-brand-gold transition-colors">
                    {{ m.name }}
                  </h3>
                  <p class="text-[10px] font-sans font-extrabold uppercase tracking-[0.2em] text-brand-gold/80 mb-3">
                    {{ m.role || 'Committee Member' }}
                  </p>
                </div>

                <!-- Action Footer -->
                <div class="flex items-center justify-between mt-auto pt-6 border-t border-slate-100/50">
                   <div class="flex items-center gap-3">
                      <div class="h-8 w-8 rounded-full bg-slate-50 flex items-center justify-center text-brand-gold shadow-xs">
                         <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
                      </div>
                      <span class="text-xs font-bold text-slate-500">
                        {{ m.phone_no ? 'Verified Contact' : 'Directory Only' }}
                      </span>
                   </div>
                   <button 
                     @click="openDetails(m)"
                     class="flex items-center justify-center w-10 h-10 rounded-xl bg-slate-50 text-brand-gold border border-slate-100 hover:bg-brand-gold hover:text-white hover:border-brand-gold transition-all duration-300"
                   >
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3"></path></svg>
                   </button>
                </div>

                <!-- Subtle Pattern Overlay for Officers -->
                <div v-if="getPriority(m.role) <= 6" class="absolute -right-4 -bottom-4 opacity-[0.03] rotate-12 pointer-events-none">
                    <svg class="w-32 h-32" fill="currentColor" viewBox="0 0 24 24"><path d="M12 2L15.09 8.26L22 9.27L17 14.14L18.18 21.02L12 17.77L5.82 21.02L7 14.14L2 9.27L8.91 8.26L12 2Z"/></svg>
                </div>
              </div>
            </div>
            
            <!-- Shadow Flourish for Officers -->
            <div 
              v-if="getPriority(m.role) <= 6" 
              class="absolute -inset-0.5 bg-brand-gold/20 blur-xl opacity-0 group-hover:opacity-40 transition-opacity duration-500 rounded-3xl"
            ></div>
          </div>
        </template>

        <!-- Empty State -->
        <template v-else>
          <div class="col-span-full text-center text-slate-500 py-20">
            No committee members found
          </div>
        </template>
      </div>

    <!-- Professional Details Modal -->
    <Transition name="fade">
      <div v-if="selectedMember" class="fixed inset-0 z-50 flex items-center justify-center p-4 overflow-hidden" @click.self="closeDetails">
        <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-md"></div>
        
        <div class="relative bg-white rounded-4xl max-w-lg w-full overflow-hidden shadow-2xl border border-slate-200 flex flex-col">
          <!-- Header Image -->
          <div class="h-64 sm:h-80 bg-slate-100 relative">
            <img 
              v-if="selectedMember.photo" 
              :src="selectedMember.photo" 
              class="w-full h-full object-cover object-top" 
            />
            <div v-else class="w-full h-full flex items-center justify-center bg-linear-to-b from-slate-100 to-slate-200 text-brand-gold/10">
               <span class="text-9xl font-serif font-bold select-none">{{ selectedMember.name.charAt(0) }}</span>
            </div>
            <div class="absolute inset-0 bg-linear-to-t from-black/60 to-transparent"></div>
            
            <button @click="closeDetails" class="absolute top-6 right-6 p-2.5 bg-black/20 hover:bg-black/40 text-white rounded-full backdrop-blur-md transition-colors">
               <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M6 18L18 6M6 6l12 12"></path></svg>
            </button>

            <div class="absolute bottom-6 left-8">
               <span class="px-4 py-1 bg-brand-gold text-white text-[10px] font-black uppercase tracking-widest rounded-full mb-3 inline-block">
                 {{ selectedMember.role || 'Committee' }}
               </span>
               <h2 class="text-3xl font-serif font-bold text-white drop-shadow-md">{{ selectedMember.name }}</h2>
            </div>
          </div>

          <!-- Professional Body -->
          <div class="p-10 space-y-8">
             <div class="space-y-6">
                <div class="flex items-center gap-5 group">
                   <div class="w-12 h-12 rounded-2xl bg-brand-gold/5 flex items-center justify-center text-brand-gold border border-brand-gold/10 group-hover:bg-brand-gold group-hover:text-white transition-all duration-500">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
                   </div>
                   <div>
                      <span class="block text-[10px] font-black uppercase tracking-widest text-slate-400 mb-0.5">Contact Number</span>
                      <span class="text-lg font-bold text-slate-900">{{ selectedMember.phone_no || 'Not Publicly Listed' }}</span>
                   </div>
                </div>

                <div class="flex items-center gap-5 group">
                   <div class="w-12 h-12 rounded-2xl bg-brand-gold/5 flex items-center justify-center text-brand-gold border border-brand-gold/10 group-hover:bg-brand-gold group-hover:text-white transition-all duration-500">
                      <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-10V4m0 10V4m-4 6h4m-4 4h4m1 1h1m-7 1h1"></path></svg>
                   </div>
                   <div>
                      <span class="block text-[10px] font-black uppercase tracking-widest text-slate-400 mb-0.5">Representation</span>
                      <span class="text-lg font-bold text-slate-900">Kollamparambil Executive Body</span>
                   </div>
                </div>
             </div>

             <div class="pt-8 border-t border-slate-100 flex justify-center">
                <button 
                  @click="closeDetails"
                  class="w-full bg-slate-900 text-white py-4 rounded-2xl font-bold text-sm tracking-widest uppercase hover:bg-brand-gold transition-colors shadow-xl"
                >
                  Close Profile
                </button>
             </div>
          </div>
        </div>
      </div>
    </Transition>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useHead, useRuntimeConfig } from '#imports'
import type { FamilyMember } from '~/types/family'

useHead({
  title: 'Committee'
})

// Types
type LayoutType = 'grid' | 'list' | 'compact'

// State
const committee = ref<FamilyMember[]>([])
const loading = ref(true)
const query = ref('')
const selectedMember = ref<FamilyMember | null>(null)

const openDetails = (m: FamilyMember) => {
    selectedMember.value = m
    document.body.style.overflow = 'hidden'
}

const closeDetails = () => {
    selectedMember.value = null
    document.body.style.overflow = ''
}

// Role Priority Map (Lower number = Higher priority)
const rolePriority: Record<string, number> = {
    'Patron': 1,
    'President': 2,
    'Vice President': 3,
    'Secretary': 4,
    'Joint Secretary': 5,
    'Treasurer': 6,
    'Committee Member': 99
}

const getPriority = (role?: string) => {
    if (!role) return 100
    // Check for partial matches if exact match fails (e.g. "Vice-President")
    const cleanRole = role.trim()
    return rolePriority[cleanRole] || 100
}

const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'

// Fetch Data
const resolveImage = (path: string) => {
    if (!path) return undefined
    if (path.startsWith('http') || path.startsWith('data:')) return path
    const cleanPath = path.startsWith('/') ? path : `/${path}`
    return `${apiBase}${cleanPath}`
}

onMounted(async () => {
    try {
        const res = await fetch(`${apiBase}/api/profiles/committee/`)
        if (res.ok) {
            const rawData = await res.json()
            // Map raw API data to FamilyMember interface
            committee.value = rawData.map((item: any) => ({
                id: item.id,
                name: item.name,
                photo: resolveImage(item.pic),
                role: item.role,
                phone_no: item.phone_no,
                // Fallback age/relation if not present in API
                relation: 'Committee', 
            }))
        }
    } catch (e) {
        console.error("Failed to load committee", e)
    } finally {
        loading.value = false
    }
})

// Search & Filter
const normalized = (s: string) => s.trim().toLowerCase()

const filtered = computed(() => {
    let result = [...committee.value]

    // 1. Search Filter
    if (query.value) {
        const q = normalized(query.value)
        result = result.filter(m => {
            const name = normalized(m.name || '')
            const role = normalized(m.role || '')
            return name.includes(q) || role.includes(q)
        })
    }

    // 2. Sort by Role Priority
    result.sort((a, b) => {
        const pA = getPriority(a.role)
        const pB = getPriority(b.role)
        if (pA !== pB) return pA - pB
        // Secondary sort by name
        return (a.name || '').localeCompare(b.name || '')
    })

    return result
})

</script>

<style scoped>
/* Ensure grid works properly */
</style>
