<template>
  <div class="min-h-screen bg-slate-100 text-slate-800 font-sans pt-32 pb-8">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 mb-4">Family Directory</h1>
        <div class="h-1 w-24 bg-[#A08050] mx-auto rounded-full"></div>
      </div>

      <!-- Controls -->
      <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-6 mb-8 bg-white p-4 rounded-xl border border-slate-200 shadow-md">
        
        <!-- Search -->
        <div class="flex items-center gap-3 w-full md:w-auto flex-1">
          <div class="relative w-full max-w-md">
             <input v-model="query" @input="onSearch" type="search" placeholder="Search members..." 
                    class="w-full pl-10 pr-4 py-2.5 rounded-lg bg-slate-50 border border-slate-300 text-slate-900 placeholder-slate-400 focus:ring-2 focus:ring-amber-500 focus:border-transparent outline-none transition-all" />
             <svg class="w-5 h-5 text-slate-400 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
          </div>
          <button @click="clear" class="px-4 py-2.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg transition-colors text-sm font-bold">Clear</button>
        </div>

        <!-- Controls -->
        <div class="flex items-center gap-4 text-sm text-slate-500 font-medium">
          <div class="flex items-center gap-2">
              <label>Layout</label>
              <select v-model="layout" class="bg-slate-50 border border-slate-300 rounded px-2 py-1 text-slate-800 focus:outline-none focus:ring-1 focus:ring-amber-500 cursor-pointer">
                <option value="grid">Grid</option>
                <option value="list">List</option>
                <option value="compact">Compact</option>
              </select>
          </div>
          
          <div class="hidden sm:flex items-center gap-2">
            <label>Size</label>
            <input type="range" min="160" max="420" v-model.number="minWidth" class="w-24 accent-amber-500 cursor-pointer" />
          </div>
        </div>
      </div>

    <!-- Grid Section -->
    <div class="grid gap-4" :class="containerClass" :style="containerStyle">
      <!-- Skeleton Grid -->
      <template v-if="family.loading && filtered.length === 0">
        <div v-for="n in 8" :key="n" class="bg-white rounded-xl h-48 animate-pulse border border-slate-200">
           <div class="h-full flex items-center p-4 gap-4">
              <div class="w-24 h-24 rounded-full bg-slate-200 shrink-0"></div>
              <div class="flex-1 space-y-3">
                 <div class="h-5 bg-slate-200 rounded w-3/4"></div>
                 <div class="h-4 bg-slate-200 rounded w-1/2"></div>
              </div>
           </div>
        </div>
      </template>

      <!-- Real Cards -->
      <template v-else-if="filtered.length > 0">
        <component
          v-for="m in filtered"
          :key="m.id"
          :is="cardComponent"
          :member="m"
          :variant="cardVariant"
        />
      </template>

      <!-- Empty State -->
      <template v-else-if="!family.loading">
        <div class="col-span-full text-center text-slate-500 py-10 bg-white rounded-xl border border-slate-200">No members found</div>
      </template>
    </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useFamilyStore } from '~/stores/family'
import type { FamilyMember } from '~/types/family'

const family = useFamilyStore()

onMounted(() => {
    family.fetchFamily()
})

const all = computed(() => family.flatList())

// UI state
const query = ref('')
const layout = ref<'grid'|'list'|'compact'>('grid')
const minWidth = ref(220)

const onSearch = () => {
  // simple debounce could be added; for now immediate
}

const clear = () => { query.value = '' }

const normalized = (s: string) => s.trim().toLowerCase()

const filtered = computed(() => {
  if (!query.value) return all.value
  const q = normalized(query.value)
  // match id exactly if numeric
  const idNum = Number(query.value)
  return all.value.filter(m => {
    if (!m) return false
    if (!isNaN(idNum) && idNum && m.id === idNum) return true
    const name = normalized(m.name || '')
    if (name.includes(q)) return true
    // family name = last word of name
    const parts = name.split(' ')
    if (parts.length > 1 && parts[parts.length -1] === q) return true
    return false
  })
})

// dynamic layout helpers
const cardComponent = computed(() => 'MemberCard')
const cardVariant = computed(() => layout.value === 'compact' ? 'compact' : (layout.value === 'list' ? 'list' : 'default'))

const containerClass = computed(() => {
  if (layout.value === 'list') return 'flex flex-col gap-3'
  if (layout.value === 'compact') return 'grid gap-2'
  return 'grid gap-4'
})

const containerStyle = computed(() => {
  if (layout.value === 'list') return {}
  // use auto-fit with minWidth controlled by slider
  return { gridTemplateColumns: `repeat(auto-fit, minmax(${minWidth.value}px, 1fr))` }
})


</script>

<style scoped>
:deep(.grid) {
  display: grid;
}
</style>
