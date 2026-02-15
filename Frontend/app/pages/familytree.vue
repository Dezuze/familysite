<template>
  <div class="min-h-screen bg-slate-50 text-slate-800 font-sans pt-32 relative overflow-hidden">
    
    <!-- Standardized Premium Header -->
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 mb-12 relative z-20 pointer-events-auto">
        <div class="text-center space-y-4">
            <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
                Family Tree
            </h1>
            <div class="h-1.5 w-24 bg-brand-gold mx-auto rounded-full"></div>
            <p class="text-lg text-slate-500 max-w-xl mx-auto font-medium">
                Interactive Genealogy & Member Directory
            </p>
        </div>

        <!-- Unified Controls Area -->
        <div class="mt-10 flex flex-col md:flex-row items-center justify-between gap-6 bg-white/80 backdrop-blur-md p-4 rounded-2xl border border-slate-200 shadow-xl relative z-30 pointer-events-auto">
            <!-- View Mode Toggle -->
            <div class="bg-slate-100 rounded-xl p-1 flex border border-slate-200 shadow-inner relative z-40 pointer-events-auto">
                <button 
                    @click="viewMode = 'visual'"
                    :class="['px-6 py-2 rounded-lg text-sm font-bold transition-all', viewMode==='visual' ? 'bg-brand-gold text-white shadow-md' : 'text-slate-500 hover:text-brand-gold']"
                >
                    Visual Map
                </button>
                <button 
                    @click="viewMode = 'grid'"
                    :class="['px-6 py-2 rounded-lg text-sm font-bold transition-all', viewMode==='grid' ? 'bg-brand-gold text-white shadow-md' : 'text-slate-500 hover:text-brand-gold']"
                >
                    Directory
                </button>
            </div>

            <!-- Contextual Controls (Search/Layout) -->
            <div class="flex flex-1 items-center justify-center md:justify-end gap-4 w-full">
                <!-- Search -->
                <div class="relative flex-1 max-w-xs">
                    <input v-model="searchQuery" @keyup.enter="performSearch" type="search" placeholder="Find member..." 
                            class="w-full pl-10 pr-4 py-2.5 rounded-xl bg-slate-50 border border-slate-200 text-slate-900 placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-gold/40 transition-all">
                    <svg class="w-5 h-5 text-slate-400 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    
                    <!-- Search Results Dropdown -->
                    <div v-if="searchResults.length > 0 && viewMode === 'visual'" class="absolute top-full right-0 mt-2 w-full bg-white rounded-xl shadow-2xl border border-slate-200 max-h-60 overflow-y-auto z-50">
                        <div v-for="res in searchResults" :key="res.id" @click="focusOnMember(res)" class="px-4 py-2 hover:bg-slate-50 cursor-pointer border-b border-slate-100 last:border-0">
                            <div class="font-bold text-slate-800 text-sm">{{ res.name }}</div>
                            <div class="text-xs text-slate-50">{{ res.relation || 'Member' }}</div>
                        </div>
                    </div>
                </div>

                <!-- Directory Specific Layout Controls -->
                <div v-if="viewMode === 'grid'" class="flex items-center gap-4 text-xs font-bold text-slate-400 uppercase tracking-widest bg-slate-50 px-4 py-2 rounded-xl border border-slate-200">
                    <div class="flex items-center gap-2">
                        <label>Layout</label>
                        <select v-model="layout" class="bg-transparent border-none focus:ring-0 text-slate-800 cursor-pointer">
                            <option value="grid">Grid</option>
                            <option value="list">List</option>
                            <option value="compact">Compact</option>
                        </select>
                    </div>
                    
                    <div v-if="layout === 'grid' || layout === 'compact'" class="hidden lg:flex items-center gap-2">
                        <label>Size</label>
                        <input type="range" min="160" max="420" v-model.number="minWidth" class="w-20 accent-brand-gold cursor-pointer" />
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Visual View -->
    <div v-show="viewMode === 'visual'" class="w-full h-[calc(100vh-100px)] cursor-move" ref="chartContainer">
       <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-gold"></div>
       </div>
       <svg ref="svgRef" class="w-full h-full"></svg>
    </div>

     <!-- Grid View -->
     <div v-if="viewMode === 'grid'" class="max-w-7xl mx-auto px-4 pb-20 overflow-y-auto h-[calc(100vh-280px)]">

         <div :class="containerClass" :style="containerStyle">
            <!-- Skeleton Grid -->
            <template v-if="loading">
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
            <template v-else>
               <div 
                  v-for="member in sortedMembers" 
                  :key="member.id"
                  @click="openMember(member)"
                  class="cursor-pointer"
               >
                  <MemberCard 
                    :member="member" 
                    :variant="cardVariant"
                  />
               </div>
            </template>
         </div>
         
         <!-- Empty State -->
         <div v-if="!loading && sortedMembers.length === 0" class="text-center text-slate-500 py-20 bg-white rounded-xl border border-slate-200 shadow-sm">
            <svg class="w-16 h-16 mx-auto text-slate-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
            <p class="font-bold text-slate-400">No members found matching your search</p>
         </div>
     </div>

     <!-- Member Modal -->
     <MemberDetailsModal 
        v-if="selectedMember" 
        :member="selectedMember" 
        @close="selectedMember = null" 
     />

  </div>
</template>

<script setup lang="ts">
import { computed, watch, ref, onMounted } from 'vue'
import { useHead, useRuntimeConfig, useRoute } from '#imports'
import * as d3 from 'd3'
import type { FamilyMember } from '~/types/family'
import MemberDetailsModal from '~/components/MemberDetailsModal.vue'
import MemberCard from '~/components/MemberCard.vue'
import { useAuthStore } from '~/stores/auth'
import { useFamilyStore } from '~/stores/family'

const auth = useAuthStore()
const familyStore = useFamilyStore()
const route = useRoute()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'

// View mode can be 'visual' or 'grid'
const viewMode = ref<'visual' | 'grid'>(route.query.view === 'grid' ? 'grid' : 'visual')
const loading = computed(() => familyStore.loading)
const svgRef = ref<SVGSVGElement | null>(null)
const chartContainer = ref<HTMLDivElement | null>(null)
const selectedMember = ref<FamilyMember | null>(null)

// Directory UI state
const layout = ref<'grid'|'list'|'compact'>('grid')
const minWidth = ref(250)
const searchQuery = ref('')
const searchResults = ref<FamilyMember[]>([])

const nodes = computed(() => familyStore.flatList())
const links = computed(() => familyStore.links)

const performSearch = () => {
  if (searchResults.value.length > 0) {
    focusOnMember(searchResults.value[0])
  }
}

// Dynamic layout helpers
const cardVariant = computed(() => layout.value === 'compact' ? 'compact' : (layout.value === 'list' ? 'list' : 'default'))
const containerClass = computed(() => {
  if (layout.value === 'list') return 'flex flex-col gap-3'
  if (layout.value === 'compact') return 'grid gap-2'
  return 'grid gap-4'
})
const containerStyle = computed(() => {
  if (layout.value === 'list') return {}
  const minVal = minWidth.value || 250
  return { gridTemplateColumns: `repeat(auto-fit, minmax(${minVal}px, 1fr))` }
})

const sortedMembers = computed(() => {
   let list = [...nodes.value].sort((a,b) => a.name.localeCompare(b.name))
   if (searchQuery.value) {
       const q = searchQuery.value.toLowerCase()
       return list.filter(m => m.name.toLowerCase().includes(q))
   }
   return list
})

// Store zoom behavior global to access from search
let globalZoom: any = null 
let globalSVG: any = null
let globalRoot: any = null // D3 Hierarchy Root

const resolveImage = (path: string | null) => {
    if (!path) return null
    if (path.startsWith('http') || path.startsWith('data:')) return path
    const cleanPath = path.startsWith('/') ? path : `/${path}`
    return `${apiBase}${cleanPath}`
}

watch(searchQuery, (val) => {
    if (!val || viewMode.value === 'grid') {
        searchResults.value = []
        return
    }
    const q = val.toLowerCase()
    searchResults.value = nodes.value.filter((n: any) => n.name.toLowerCase().includes(q)).slice(0, 5)
})

const focusOnMember = (targetMember: any) => {
    searchQuery.value = '' // clear search
    searchResults.value = []
    
    if (!targetMember || !globalZoom || !globalSVG) return

    if (!globalRoot) return

    let targetNode = globalRoot.descendants().find((d: any) => d.data.id === targetMember.id)
    let targetX = 0
    let targetY = 0
    let found = false

    if (targetNode) {
        targetX = targetNode.x
        targetY = targetNode.y
        found = true
    } else {
        const spouseLink = links.value.find((l: any) => l.type === 'spouse' && (l.source === targetMember.id || l.target === targetMember.id))
        if (spouseLink) {
             const partnerId = spouseLink.source === targetMember.id ? spouseLink.target : spouseLink.source
             const partnerNode = globalRoot.descendants().find((d: any) => d.data.id === partnerId)
             if (partnerNode) {
                 targetX = partnerNode.x + 160
                 targetY = partnerNode.y
                 found = true
             }
        }
    }

    if (found) {
        const container = chartContainer.value
        if (container) {
            const width = container.clientWidth
            const height = container.clientHeight
            const scale = 1.5
            globalSVG.transition().duration(1500).call(
                globalZoom.transform as any, 
                d3.zoomIdentity.translate(width/2 - targetX*scale, height/2 - targetY*scale).scale(scale)
            )
        }
        selectedMember.value = targetMember 
    }
}

const openMember = (m: FamilyMember) => { selectedMember.value = m }

// --- D3 Logic ---
   const initGraph = () => {
      if (!nodes.value.length || !svgRef.value || !chartContainer.value) {
          return
      }
   
      const width = chartContainer.value.clientWidth
      const height = chartContainer.value.clientHeight
      
      if (width === 0 || height === 0) {
          setTimeout(initGraph, 500)
          return
      }

      const svg = d3.select(svgRef.value) as d3.Selection<SVGSVGElement, unknown, null, undefined>
      svg.attr("viewBox", `0 0 ${width} ${height}`)
      
      const zoom = d3.zoom<SVGSVGElement, unknown>().on("zoom", (event) => {
          g.attr("transform", event.transform)
      })
      svg.call(zoom)
      
      globalZoom = zoom
      globalSVG = svg
   
      svg.selectAll("*").remove()
      const g = svg.append("g")

      const hasParent = new Set(links.value.filter(l => l.type === 'parent').map(l => l.target))
      const potentialRoots = nodes.value.filter(n => !hasParent.has(n.id))
      const roots = potentialRoots.filter((r, idx) => {
          const spouseLink = links.value.find(l => (l.source === r.id || l.target === r.id) && l.type === 'spouse')
          if (spouseLink) {
              const spouseId = spouseLink.source === r.id ? spouseLink.target : spouseLink.source
              const spouseObj = potentialRoots.find(pr => pr.id === spouseId)
              if (spouseObj && potentialRoots.indexOf(spouseObj) < idx) {
                  return false
              }
          }
          return true
      })
      
      const getChildrenIds = (parentId: number): number[] => {
         return links.value
            .filter((l: any) => l.type === 'parent' && l.source === parentId)
            .map((l: any) => l.target)
      }

      const buildHierarchy = (id: number, visited: Set<number> = new Set()): any => {
         if (visited.has(id)) return null 
         visited.add(id)
         const node = nodes.value.find((n: any) => n.id === id)
         const childrenIds = getChildrenIds(id)
         return {
            ...node,
            children: childrenIds.map(cid => buildHierarchy(cid, visited)).filter(Boolean)
         }
      }

      const forest: any[] = []
      const globalVisited = new Set<number>()
      
      potentialRoots.sort((a: any, b: any) => {
          const childrenA = getChildrenIds(a.id).length
          const childrenB = getChildrenIds(b.id).length
          return childrenB - childrenA
      })

      potentialRoots.forEach((rootNode: any) => {
          if (!globalVisited.has(rootNode.id)) {
              const treeData = buildHierarchy(rootNode.id, globalVisited)
              if (treeData) forest.push(treeData)
          }
      })

      nodes.value.forEach((node: any) => {
          if (!globalVisited.has(node.id)) {
              forest.push({...node, children: []})
              globalVisited.add(node.id)
          }
      })

      const treeLayout = d3.tree<any>().nodeSize([200, 300])
      const forestGroups = forest.map((treeData) => {
          const strategyRoot = d3.hierarchy(treeData)
          treeLayout(strategyRoot)
          return strategyRoot
      })

      let currentXOffset = width / 2
      forestGroups.forEach((root, i) => {
          const treeG = g.append("g").attr("transform", `translate(${currentXOffset}, 100)`)
          
          if (i === 0) globalRoot = root 

          treeG.selectAll(".link")
            .data(root.links())
            .join("path")
            .attr("class", "link")
            .attr("fill", "none")
            .attr("stroke", "#A08050")
            .attr("stroke-width", 2)
            .attr("d", d3.linkVertical<any, d3.HierarchyPointNode<any>>()
                .x(d => d.x)
                .y(d => d.y) as any)

          const nodeGroup = treeG.selectAll(".node")
            .data(root.descendants())
            .join("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${d.x},${d.y})`)

          nodeGroup.each(function(this: any, d: any) {
              renderCard(d3.select(this), 0, d.data)
              const spouse = getSpouse(d.data.id)
               if (spouse) {
                   const sel = d3.select(this)
                   const spouseOffset = 180 
                   sel.append("line")
                      .attr("x1", 70).attr("x2", spouseOffset - 70) 
                      .attr("y1", 0).attr("y2", 0)
                      .attr("stroke", "#A08050").attr("stroke-width", 2).attr("stroke-dasharray", "4,2")
                   renderCard(sel, spouseOffset, spouse)
               }
          })

          currentXOffset += 1200 
      })

      function renderCard(selection: d3.Selection<any, any, any, any>, dx=0, d: any) {
          if (!d) return
          const cardWidth = 140
          const cardHeight = 180
          const group = selection.append("g").attr("transform", `translate(${dx}, 0)`)
          const isUser = auth.user && d.username === auth.user.username
          
          // Unique ID for clipPath
          const clipId = `clip-${d.id}-${Math.random().toString(36).substr(2, 9)}`

           group.append("rect")
            .attr("x", -cardWidth/2).attr("y", -cardHeight/2)
            .attr("width", cardWidth).attr("height", cardHeight).attr("rx", 12)
            .attr("fill", isUser ? "#FEFCE8" : "#ffffff")
            .attr("stroke", isUser ? "#A08050" : "#cbd5e1")
            .attr("stroke-width", isUser ? 2 : 1)
            .attr("filter", d.is_deceased ? "grayscale(100%)" : "drop-shadow(0 4px 6px rgba(0,0,0,0.05))")
            .style("cursor", "pointer")
            .on("click", () => openMember(d))

          // Define ClipPath
          const defs = group.append("defs")
          defs.append("clipPath")
            .attr("id", clipId)
            .append("circle")
            .attr("cx", 0)
            .attr("cy", -cardHeight/4)
            .attr("r", 35)

          group.append("image")
            .attr("href", resolveImage(d.photo || null) || `https://ui-avatars.com/api/?name=${d.name}&background=f1f5f9&color=64748b`)
            .attr("x", -35).attr("y", -cardHeight/4 - 35).attr("width", 70).attr("height", 70)
            .attr("preserveAspectRatio", "xMidYMid slice")
            .attr("clip-path", `url(#${clipId})`)
            .style("pointer-events", "none")

          // Name
          group.append("text")
            .text(d.name.split(' ')[0])
            .attr("x", 0).attr("y", 15)
            .attr("text-anchor", "middle")
            .attr("fill", "#1e293b")
            .attr("font-weight", "bold")
            .attr("font-size", "14px")
            .style("pointer-events", "none")
          
          // Role / Relation
          group.append("text")
            .text(d.role || d.relation || 'Member')
            .attr("x", 0).attr("y", 32)
            .attr("text-anchor", "middle")
            .attr("fill", d.is_committee ? "#A08050" : "#64748b")
            .attr("font-weight", d.is_committee ? "bold" : "normal")
            .attr("font-size", "11px")
            .style("pointer-events", "none")

          // Gender & Age
          const metaGroup = group.append("g").attr("transform", "translate(0, 52)")
          metaGroup.append("text")
            .text(d.gender === 'M' ? '♂' : '♀')
            .attr("x", -20).attr("y", 0)
            .attr("fill", "#A08050")
            .attr("font-size", "12px")
            .attr("font-weight", "bold")

          metaGroup.append("text")
            .text(`${d.age} Yrs`)
            .attr("x", 0).attr("y", 0)
            .attr("text-anchor", "start")
            .attr("fill", "#94a3b8")
            .attr("font-size", "11px")
      }

      function getSpouse(id: number) {
          const l = links.value.find((l: any) => l.type === 'spouse' && (l.source === id || l.target === id))
          if (!l) return null
          const spouseId = l.source === id ? l.target : l.source
          return nodes.value.find((n: any) => n.id === spouseId)
      }
      
      // FOCUS ON USER
      let userCoords = {x: 0, y: 0, found: false}
      
      forestGroups.forEach((root, i) => {
          if (userCoords.found) return
          
          root.descendants().forEach((d: any) => {
              if (userCoords.found) return
              const nodeUsername = d.data.username
              if (nodeUsername === auth.user?.username) {
                  userCoords = { x: (i * 1200) + width/2 + (d.x || 0), y: 100 + (d.y || 0), found: true }
                  return
              }
              const spouse = getSpouse(d.data.id)
              if (spouse && (spouse as any).username === auth.user?.username) {
                  const spouseOffsetX = 180
                  userCoords = { x: (i * 1200) + width/2 + (d.x || 0) + spouseOffsetX, y: 100 + (d.y || 0), found: true }
              }
          })
      })
      
      if (userCoords.found) {
         const scale = 1.2
         svg.transition().duration(1500).call(
             zoom.transform as any, 
             d3.zoomIdentity.translate(width/2 - userCoords.x*scale, height/2 - userCoords.y*scale).scale(scale)
         )
      } else {
         svg.transition().duration(750).call(
             zoom.transform as any, 
             d3.zoomIdentity.translate(width/2, 50).scale(0.5)
         )
      }
   }

onMounted(async () => {
    await familyStore.fetchFamily()
    initGraph()
})

// Re-init graph when data or view changes
watch([nodes, links], () => {
    if (viewMode.value === 'visual') {
        setTimeout(initGraph, 100)
    }
}, { deep: true })

watch(viewMode, (val) => {
    if (val === 'visual') {
        setTimeout(initGraph, 100) 
    }
})
</script>
