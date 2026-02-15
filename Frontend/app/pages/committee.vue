<template>
  <div class="min-h-screen bg-slate-100 text-slate-800 font-sans pt-32 pb-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 mb-4">Committee Members</h1>
        <div class="h-1 w-24 bg-brand-gold mx-auto rounded-full"></div>
        <div class="mt-6 flex justify-center">
            <span class="bg-white text-brand-gold px-6 py-2 rounded-full border border-slate-200 font-bold tracking-widest text-sm uppercase shadow-md backdrop-blur-sm">
                Term 2025 - 2027
            </span>
        </div>
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
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-8">
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
            class="bg-white rounded-2xl overflow-hidden shadow-lg border border-slate-200 group hover:-translate-y-1 transition-all duration-300"
          >
             <!-- Full Size Image -->
             <div class="h-64 sm:h-72 w-full relative bg-slate-100">
                 <img 
                   v-if="m.photo" 
                   :src="m.photo" 
                   class="w-full h-full object-cover object-top transition-transform duration-500 group-hover:scale-105" 
                 />
                 <div v-else class="w-full h-full flex items-center justify-center bg-slate-200 text-slate-400">
                     <span class="text-6xl font-bold opacity-30">{{ m.name.charAt(0) }}</span>
                 </div>
                 
                 <!-- Gradient Overlay -->
                 <div class="absolute inset-x-0 bottom-0 h-32 bg-linear-to-t from-black/80 to-transparent"></div>
                 
                 <!-- Position Badge -->
                 <div class="absolute bottom-4 left-4 right-4 text-white">
                     <span class="bg-brand-gold text-white text-xs font-bold px-2 py-1 rounded uppercase tracking-wider mb-2 inline-block">
                         {{ m.role || 'Member' }}
                     </span>
                     <h3 class="text-xl font-bold font-serif leading-tight drop-shadow-md">{{ m.name }}</h3>
                 </div>
             </div>
             
             <!-- Details (Footer) -->
             <div class="p-4 flex justify-between items-center bg-white">
                 <div class="text-sm text-slate-500 font-medium flex items-center gap-2">
                     <svg class="w-4 h-4 text-brand-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path></svg>
                     <span v-if="m.phone_no">Available</span>
                     <span v-else>Contact via Directory</span>
                 </div>
                 <button class="text-brand-gold hover:text-brand-gold/80 font-bold text-sm">View Profile &rarr;</button>
             </div>
          </div>
        </template>

        <!-- Empty State -->
        <template v-else>
          <div class="col-span-full text-center text-slate-500 py-20">
            No committee members found
          </div>
        </template>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { useHead, useRuntimeConfig } from '#imports'
import type { FamilyMember } from '~/types/family'

useHead({
  title: 'Committee - Kollamparambil Family'
})

// Types
type LayoutType = 'grid' | 'list' | 'compact'

// State
const committee = ref<FamilyMember[]>([])
const loading = ref(true)
const query = ref('')
const layout = ref<LayoutType>('grid')
const minWidth = ref(250) // Default slightly larger card width

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
    if (path.startsWith('http')) return path
    return `${apiBase}${path}`
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
