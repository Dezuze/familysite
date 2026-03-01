<template>
  <div class="min-h-screen text-slate-800 font-sans pt-32 relative overflow-hidden" style="background: linear-gradient(135deg, #faf8f5 0%, #f0ede6 30%, #e8e4db 60%, #f5f2ec 100%);">
    
    <!-- Subtle decorative background pattern -->
    <div class="absolute inset-0 opacity-[0.03] pointer-events-none" style="background-image: url('data:image/svg+xml,%3Csvg width=&quot;60&quot; height=&quot;60&quot; viewBox=&quot;0 0 60 60&quot; xmlns=&quot;http://www.w3.org/2000/svg&quot;%3E%3Cg fill=&quot;none&quot; fill-rule=&quot;evenodd&quot;%3E%3Cg fill=&quot;%23A08050&quot; fill-opacity=&quot;1&quot;%3E%3Cpath d=&quot;M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z&quot;/%3E%3C/g%3E%3C/g%3E%3C/svg%3E');"></div>
    
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
    <div v-show="viewMode === 'visual'" class="w-full h-[calc(100vh-100px)] cursor-move relative" ref="chartContainer">
       <!-- Tree area backdrop -->
       <div class="absolute inset-0 rounded-none" style="background: radial-gradient(ellipse at center, rgba(160,128,80,0.04) 0%, transparent 70%);"></div>
       <div v-if="loading" class="absolute inset-0 flex items-center justify-center z-10">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-gold"></div>
       </div>
       <svg ref="svgRef" class="w-full h-full relative z-1"></svg>
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
import MemberDetailsModal from '~/components/MemberDetailsModal.vue'
import MemberCard from '~/components/MemberCard.vue'

// ============================================================
// familytree.vue — Interactive Family Tree & Member Directory
// ============================================================
// Renders an interactive D3.js genealogy tree with:
//   • Gender-coded cards (blue=male, rose=female, gold=current user)
//   • Dynamic separation (spouse-aware spacing prevents overlap)
//   • Multi-tree forest rendering (separate family heads side-by-side)
//   • Pan, zoom, auto-focus on logged-in user, search-to-focus
//   • Switchable grid/list/compact directory view
// ============================================================

import * as d3 from 'd3'
import { useFamilyStore } from '~/stores/family'
import type { FamilyMember } from '~/types/family'
import { useAuthStore } from '~/stores/auth'

const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string

const familyStore = useFamilyStore()
const auth = useAuthStore()

// --- Refs & UI State ---
const route = useRoute()

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

// --- Computed Data ---
// Flatten the store's tree data into a simple array of nodes and links.
// Nodes = all FamilyMembers, Links = parent/spouse/sibling connections.
const nodes = computed(() => familyStore.flatList())
const links = computed(() => familyStore.links)

// When user presses Enter in search, auto-focus the first result
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

// --- Global D3 State ---
// These module-scoped variables are updated each time initGraph() runs.
// They enable the search-to-focus and auto-focus features to access
// the last-rendered tree state.
let globalZoom: any = null        // D3 zoom behavior for programmatic pan/zoom
let globalSVG: any = null         // D3 selection of the <svg> element
let globalRoot: any = null        // Root of the first tree (for fallback searches)
let globalForestData: { root: any, xOffset: number }[] = [] // All trees + X offsets

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

/**
 * Search-to-Focus: smoothly pan/zoom the tree to center on a member.
 * Searches across ALL forest trees (not just the first) and handles
 * both direct tree nodes and spouse-rendered cards.
 */
const focusOnMember = (targetMember: any) => {
    searchQuery.value = '' // clear search
    searchResults.value = []
    
    if (!targetMember || !globalZoom || !globalSVG) return

    let targetX = 0
    let targetY = 0
    let found = false

    // Search across ALL forest trees, not just the first
    for (const { root, xOffset } of globalForestData) {
        if (found) break
        
        // Check direct node
        const targetNode = root.descendants().find((d: any) => d.data.id === targetMember.id)
        if (targetNode) {
            targetX = xOffset + targetNode.x
            targetY = 100 + targetNode.y
            found = true
            break
        }
        
        // Check if target is a spouse rendered next to a tree node
        const spouseLink = links.value.find((l: any) => l.type === 'spouse' && (l.source === targetMember.id || l.target === targetMember.id))
        if (spouseLink) {
            const partnerId = spouseLink.source === targetMember.id ? spouseLink.target : spouseLink.source
            const partnerNode = root.descendants().find((d: any) => d.data.id === partnerId)
            if (partnerNode) {
                targetX = xOffset + partnerNode.x + 180
                targetY = 100 + partnerNode.y
                found = true
                break
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

// --- D3 Tree Rendering Pipeline ---
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

      // Track which nodes are part of a "real" tree (have children or are children)
      const treeNodeIds = new Set<number>()
      
      potentialRoots.forEach((rootNode: any) => {
          if (globalVisited.has(rootNode.id)) return
          
          // Check if this root is a spouse of any node already in a real tree
          const isSpouseOfTreeNode = links.value.some((l: any) => 
              l.type === 'spouse' && (
                  (l.source === rootNode.id && treeNodeIds.has(l.target)) ||
                  (l.target === rootNode.id && treeNodeIds.has(l.source))
              )
          )
          if (isSpouseOfTreeNode) {
              globalVisited.add(rootNode.id) // Mark visited so it doesn't float
              return
          }
          
          const treeData = buildHierarchy(rootNode.id, globalVisited)
          if (treeData) {
              forest.push(treeData)
              // Track all nodes in this tree that have actual hierarchy (children)
              const collectIds = (node: any) => {
                  treeNodeIds.add(node.id)
                  if (node.children) node.children.forEach(collectIds)
              }
              collectIds(treeData)
          }
      })

      // Any remaining unvisited nodes that are spouses of tree nodes should not float
      const spouseRendered = new Set<number>()
      links.value.filter(l => l.type === 'spouse').forEach((l: any) => {
          if (treeNodeIds.has(l.source) || globalVisited.has(l.source)) {
              spouseRendered.add(l.target)
          }
          if (treeNodeIds.has(l.target) || globalVisited.has(l.target)) {
              spouseRendered.add(l.source)
          }
      })

      nodes.value.forEach((node: any) => {
          if (!globalVisited.has(node.id) && !spouseRendered.has(node.id)) {
              forest.push({...node, children: []})
              globalVisited.add(node.id)
          }
      })

      // Build a set of node IDs that have spouses for dynamic separation
      const nodesWithSpouse = new Set<number>()
      links.value.filter(l => l.type === 'spouse').forEach((l: any) => {
          nodesWithSpouse.add(l.source)
          nodesWithSpouse.add(l.target)
      })

      const treeLayout = d3.tree<any>()
        .nodeSize([200, 300])
        .separation((a: any, b: any) => {
            // Base separation = 1 (200px)
            // If either node has a spouse, add extra space for the spouse card
            const aHasSpouse = nodesWithSpouse.has(a.data?.id)
            const bHasSpouse = nodesWithSpouse.has(b.data?.id)
            if (aHasSpouse && bHasSpouse) return 2.5 // Both have spouses: 500px
            if (aHasSpouse || bHasSpouse) return 2.2 // One has spouse: 440px
            return a.parent === b.parent ? 1.5 : 2  // Siblings: 300px, cousins: 400px
        })

      const forestGroups = forest.map((treeData) => {
          const strategyRoot = d3.hierarchy(treeData)
          treeLayout(strategyRoot)
          return strategyRoot
      })

      // Calculate actual tree widths for dynamic spacing
      const getTreeBounds = (root: any) => {
          let minX = Infinity, maxX = -Infinity
          root.descendants().forEach((d: any) => {
              // Account for node card (75px half-width) plus possible spouse offset (180+75)
              const nodeLeft = d.x - 75
              const hasSpouse = nodesWithSpouse.has(d.data?.id)
              const nodeRight = hasSpouse ? d.x + 180 + 75 : d.x + 75
              if (nodeLeft < minX) minX = nodeLeft
              if (nodeRight > maxX) maxX = nodeRight
          })
          return { minX, maxX, width: maxX - minX }
      }

      let currentXOffset = width / 2
      const forestOffsets: number[] = []
      forestGroups.forEach((root, i) => {
          const bounds = getTreeBounds(root)
          // Offset so tree starts after previous tree with padding
          if (i > 0) currentXOffset += -bounds.minX + 80
          
          forestOffsets.push(currentXOffset)
          const treeG = g.append("g").attr("transform", `translate(${currentXOffset}, 100)`)
          
          if (i === 0) globalRoot = root 

          treeG.selectAll(".link")
            .data(root.links())
            .join("path")
            .attr("class", "link")
            .attr("fill", "none")
            .attr("stroke", "#a89060")
            .attr("stroke-width", 2.5)
            .attr("stroke-linecap", "round")
            .attr("stroke-opacity", 0.7)
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
                      .attr("stroke", "#c9a96e").attr("stroke-width", 2).attr("stroke-dasharray", "6,4")
                      .attr("stroke-linecap", "round")
                   renderCard(sel, spouseOffset, spouse)
               }
          })

          // Advance offset past this tree's right edge
          const treeBounds = getTreeBounds(root)
          currentXOffset += treeBounds.maxX + 80
      })

      function renderCard(selection: d3.Selection<any, any, any, any>, dx=0, d: any) {
          if (!d) return
          const cardWidth = 150
          const cardHeight = 190
          const group = selection.append("g").attr("transform", `translate(${dx}, 0)`)
          const isUser = auth.user && d.username === auth.user.username
          const isMale = d.gender === 'M'
          
          // Color scheme based on gender
          const cardFill = isUser ? '#FEF3C7' : (isMale ? '#f0f4f8' : '#fdf2f4')
          const cardStroke = isUser ? '#c9a96e' : (isMale ? '#93a8c4' : '#d4a0ab')
          const accentColor = isUser ? '#c9a96e' : (isMale ? '#4a6b8a' : '#9c4f63')
          const avatarBg = isMale ? '#dce6f0' : '#f5dde1'
          const avatarRing = isUser ? '#c9a96e' : (isMale ? '#7a9bbd' : '#c88a97')
          
          const clipId = `clip-${d.id}-${Math.random().toString(36).substr(2, 9)}`
          const gradId = `grad-${d.id}-${Math.random().toString(36).substr(2, 9)}`

          // Card shadow (larger, colored)
          group.append("rect")
            .attr("x", -cardWidth/2 + 4).attr("y", -cardHeight/2 + 6)
            .attr("width", cardWidth).attr("height", cardHeight).attr("rx", 16)
            .attr("fill", "none")
            .attr("filter", d.is_deceased ? "grayscale(100%)" : "")
            .style("filter", `drop-shadow(0 8px 20px ${isMale ? 'rgba(74,107,138,0.15)' : 'rgba(156,79,99,0.15)'})`)

          // Main card rect with rounded corners
          group.append("rect")
            .attr("x", -cardWidth/2).attr("y", -cardHeight/2)
            .attr("width", cardWidth).attr("height", cardHeight).attr("rx", 16)
            .attr("fill", cardFill)
            .attr("stroke", cardStroke)
            .attr("stroke-width", isUser ? 2.5 : 1.5)
            .attr("filter", d.is_deceased ? "grayscale(100%)" : "")
            .style("cursor", "pointer")
            .on("click", () => openMember(d))

          // Colored accent bar at top
          const defs = group.append("defs")
          const grad = defs.append("linearGradient").attr("id", gradId)
            .attr("x1", "0%").attr("y1", "0%").attr("x2", "100%").attr("y2", "0%")
          grad.append("stop").attr("offset", "0%").attr("stop-color", accentColor).attr("stop-opacity", 0.8)
          grad.append("stop").attr("offset", "100%").attr("stop-color", accentColor).attr("stop-opacity", 0.3)

          group.append("rect")
            .attr("x", -cardWidth/2).attr("y", -cardHeight/2)
            .attr("width", cardWidth).attr("height", 6).attr("rx", 0)
            .attr("fill", `url(#${gradId})`)
            .attr("clip-path", `inset(0 round 16px 16px 0 0)`)

          // Avatar ring
          group.append("circle")
            .attr("cx", 0).attr("cy", -cardHeight/4 + 5)
            .attr("r", 38)
            .attr("fill", avatarBg)
            .attr("stroke", avatarRing)
            .attr("stroke-width", 2.5)

          // Define ClipPath for photo
          defs.append("clipPath")
            .attr("id", clipId)
            .append("circle")
            .attr("cx", 0)
            .attr("cy", -cardHeight/4 + 5)
            .attr("r", 35)

          group.append("image")
            .attr("href", resolveImage(d.photo || null) || `https://ui-avatars.com/api/?name=${encodeURIComponent(d.name)}&background=${avatarBg.replace('#','')}&color=${accentColor.replace('#','')}&bold=true`)
            .attr("x", -35).attr("y", -cardHeight/4 + 5 - 35).attr("width", 70).attr("height", 70)
            .attr("preserveAspectRatio", "xMidYMid slice")
            .attr("clip-path", `url(#${clipId})`)
            .style("pointer-events", "none")

          // Name
          group.append("text")
            .text(d.name.split(' ')[0])
            .attr("x", 0).attr("y", 22)
            .attr("text-anchor", "middle")
            .attr("fill", accentColor)
            .attr("font-weight", "800")
            .attr("font-size", "14px")
            .attr("font-family", "'Inter', 'Segoe UI', sans-serif")
            .style("pointer-events", "none")
          
          // Role / Relation
          group.append("text")
            .text(d.role || d.relation || 'Member')
            .attr("x", 0).attr("y", 38)
            .attr("text-anchor", "middle")
            .attr("fill", isUser ? '#92750c' : '#7a8494')
            .attr("font-weight", "600")
            .attr("font-size", "10px")
            .attr("text-transform", "uppercase")
            .attr("letter-spacing", "0.5px")
            .style("pointer-events", "none")

          // Gender & Age pill
          const pillWidth = 58
          const pillHeight = 20
          const pillY = 52
          group.append("rect")
            .attr("x", -pillWidth/2).attr("y", pillY - pillHeight/2)
            .attr("width", pillWidth).attr("height", pillHeight).attr("rx", 10)
            .attr("fill", isMale ? 'rgba(74,107,138,0.1)' : 'rgba(156,79,99,0.1)')

          group.append("text")
            .text(`${d.gender === 'M' ? '♂' : '♀'}  ${d.age || '?'} Yrs`)
            .attr("x", 0).attr("y", pillY + 5)
            .attr("text-anchor", "middle")
            .attr("fill", accentColor)
            .attr("font-size", "10px")
            .attr("font-weight", "700")
      }

      function getSpouse(id: number) {
          const l = links.value.find((l: any) => l.type === 'spouse' && (l.source === id || l.target === id))
          if (!l) return null
          const spouseId = l.source === id ? l.target : l.source
          return nodes.value.find((n: any) => n.id === spouseId)
      }
      
      // Store forest data globally for search-to-focus
      globalForestData = forestGroups.map((root, i) => ({
          root,
          xOffset: forestOffsets[i] || (width/2 + i * 1200)
      }))
      
      // FOCUS ON LOGGED-IN USER (search all trees)
      let userCoords = {x: 0, y: 0, found: false}
      
      for (const { root, xOffset } of globalForestData) {
          if (userCoords.found) break
          
          root.descendants().forEach((d: any) => {
              if (userCoords.found) return
              const nodeUsername = d.data.username
              if (nodeUsername === auth.user?.username) {
                  userCoords = { x: xOffset + (d.x || 0), y: 100 + (d.y || 0), found: true }
                  return
              }
              const spouse = getSpouse(d.data.id)
              if (spouse && (spouse as any).username === auth.user?.username) {
                  userCoords = { x: xOffset + (d.x || 0) + 180, y: 100 + (d.y || 0), found: true }
              }
          })
      }
      
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
