<template>
  <div class="min-h-screen bg-slate-200/50 text-slate-800 font-sans pt-32 relative overflow-hidden">
    
    <!-- Controls Layout -->
    <div class="absolute top-24 left-0 w-full z-10 px-4 md:px-8 flex justify-between items-start pointer-events-none">
       <!-- Title -->
       <div class="pointer-events-auto">
          <h1 class="text-4xl font-serif font-bold text-slate-800 drop-shadow-sm">Family Tree</h1>
          <p class="text-xs text-slate-500 font-medium">Interactive Genealogy</p>
       </div>

        <!-- Search & Legend -->
       <div class="flex flex-col items-end gap-4 pointer-events-auto">
          <!-- Search -->
          <div class="relative">
             <input v-model="searchQuery" @keyup.enter="performSearch" type="search" placeholder="Find member..." 
                    class="pl-10 pr-4 py-2 rounded-lg bg-white/90 backdrop-blur border border-slate-300 text-slate-900 placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-amber-500 shadow-md w-48 md:w-64 transition-all">
             <svg class="w-4 h-4 text-slate-500 absolute left-3 top-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
             
             <!-- Search Results Dropdown -->
             <div v-if="searchResults.length > 0 && viewMode === 'visual'" class="absolute top-full right-0 mt-2 w-full bg-white rounded-lg shadow-xl border border-slate-200 max-h-60 overflow-y-auto z-50">
                <div v-for="res in searchResults" :key="res.id" @click="focusOnMember(res)" class="px-4 py-2 hover:bg-slate-50 cursor-pointer border-b border-slate-100 last:border-0">
                    <div class="font-bold text-slate-800 text-sm">{{ res.name }}</div>
                    <div class="text-xs text-slate-500">{{ res.relation || 'Member' }}</div>
                </div>
             </div>
          </div>

          <!-- View Switch -->
          <div class="bg-white/90 backdrop-blur rounded-lg p-1 flex border border-slate-300 shadow-md">
             <button 
                @click="viewMode = 'visual'"
                :class="['px-4 py-2 rounded-md text-sm font-bold transition-all', viewMode==='visual' ? 'bg-slate-800 text-white shadow-lg' : 'text-slate-500 hover:text-slate-800']"
             >
               Visual
             </button>
             <button 
                @click="viewMode = 'grid'"
                :class="['px-4 py-2 rounded-md text-sm font-bold transition-all', viewMode==='grid' ? 'bg-slate-800 text-white shadow-lg' : 'text-slate-500 hover:text-slate-800']"
             >
               Directory
             </button>
          </div>
       </div>
    </div>

    <!-- Visual View -->
    <div v-show="viewMode === 'visual'" class="w-full h-[calc(100vh-100px)] cursor-move" ref="chartContainer">
       <div v-if="loading" class="absolute inset-0 flex items-center justify-center">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-amber-500"></div>
       </div>
       <svg ref="svgRef" class="w-full h-full"></svg>
    </div>

     <!-- Grid View -->
     <div v-if="viewMode === 'grid'" class="max-w-7xl mx-auto px-4 pt-10 pb-20 overflow-y-auto h-[calc(100vh-100px)]">
         <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-6">
            <!-- Skeleton Grid -->
            <template v-if="loading">
               <div v-for="n in 8" :key="n" class="bg-white rounded-xl h-48 animate-pulse border border-slate-200">
                  <div class="h-24 bg-slate-200"></div>
                  <div class="p-4 space-y-2">
                     <div class="h-4 bg-slate-200 rounded w-3/4"></div>
                     <div class="h-3 bg-slate-200 rounded w-1/2"></div>
                  </div>
               </div>
            </template>

            <!-- Real Cards -->
            <template v-else>
               <div 
                  v-for="member in sortedMembers" 
                  :key="member.id"
                  @click="openMember(member)"
                  class="bg-white rounded-xl overflow-hidden border border-slate-200 hover:border-amber-500/50 transition-all cursor-pointer group hover:-translate-y-1 shadow-md hover:shadow-xl"
               >
                  <div class="h-24 bg-linear-to-r from-slate-200 to-slate-300 relative">
                      <div class="absolute -bottom-8 left-4 w-16 h-16 rounded-full border-4 border-white overflow-hidden bg-slate-100 shadow-md">
                        <img :src="resolveImage(member.photo) || `https://ui-avatars.com/api/?name=${member.name}&background=random`" class="w-full h-full object-cover">
                      </div>
                  </div>
                  <div class="pt-10 px-4 pb-4">
                     <h3 class="font-bold text-slate-800 truncate">{{ member.name }}</h3>
                      <div class="flex justify-between items-center">
                        <p class="text-xs text-amber-600 uppercase tracking-wide">{{ member.role || member.relation }}</p>
                        <span v-if="member.is_committee" class="bg-blue-100 text-blue-700 text-[10px] px-2 py-0.5 rounded-full font-bold">Committee</span>
                      </div>
                      <div class="mt-3 flex items-center gap-2 text-xs text-slate-500">
                         <span>{{ member.age }} Years</span>
                         <span>•</span>
                         <span>{{ member.occupation || 'N/A' }}</span>
                      </div>
                  </div>
               </div>
            </template>
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

<script setup>
import { computed, watch } from 'vue'
import { useHead, useRuntimeConfig } from '#imports'
import * as d3 from 'd3'
import MemberDetailsModal from '~/components/MemberDetailsModal.vue'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'
const viewMode = ref('visual')
const loading = ref(true)
const svgRef = ref(null)
const chartContainer = ref(null)
const nodes = ref([])
const links = ref([])
const selectedMember = ref(null)

const resolveImage = (path) => {
    if (!path) return null
    if (path.startsWith('http')) return path
    return `${apiBase}${path}`
}

const searchQuery = ref('')
const searchResults = ref([])
// Store zoom behavior global to access from search
let globalZoom = null 
let globalSVG = null
let globalRoot = null // D3 Hierarchy Root

const sortedMembers = computed(() => {
   let list = [...nodes.value].sort((a,b) => a.name.localeCompare(b.name))
   if (viewMode.value === 'grid' && searchQuery.value) {
       const q = searchQuery.value.toLowerCase()
       return list.filter(m => m.name.toLowerCase().includes(q))
   }
   return list
})

watch(searchQuery, (val) => {
    if (!val || viewMode.value === 'grid') {
        searchResults.value = []
        return
    }
    const q = val.toLowerCase()
    searchResults.value = nodes.value.filter(n => n.name.toLowerCase().includes(q)).slice(0, 5)
})

const focusOnMember = (targetMember) => {
    searchQuery.value = '' // clear search
    searchResults.value = []
    
    if (!targetMember || !globalZoom || !globalSVG) return

    // Calculate position (similar to user logic)
    // We need to find the specific D3 Node for this member ID
    // Note: D3 creates a hierarchy, so we must search in descendants()
    if (!globalRoot) return

    let targetNode = globalRoot.descendants().find(d => d.data.id === targetMember.id)
    let targetX = 0
    let targetY = 0
    let found = false

    if (targetNode) {
        targetX = targetNode.x
        targetY = targetNode.y
        found = true
    } else {
        // Check spouses logic (manually positioned)
        const spouseLink = links.value.find(l => l.type === 'spouse' && (l.source === targetMember.id || l.target === targetMember.id))
        if (spouseLink) {
             const partnerId = spouseLink.source === targetMember.id ? spouseLink.target : spouseLink.source
             const partnerNode = globalRoot.descendants().find(d => d.data.id === partnerId)
             if (partnerNode) {
                 targetX = partnerNode.x + 160
                 targetY = partnerNode.y
                 found = true
             }
        }
    }

    if (found) {
        const width = chartContainer.value.clientWidth
        const height = chartContainer.value.clientHeight
        const scale = 1.5
        globalSVG.transition().duration(1500).call(
            globalZoom.transform, 
            d3.zoomIdentity.translate(width/2 - targetX*scale, height/2 - targetY*scale).scale(scale)
        )
        selectedMember.value = targetMember // Optional: Open modal? Or just highlight?
    }
}

const openMember = (m) => { selectedMember.value = m }

// --- D3 Logic ---

   // --- D3 Forest Logic ---
   const initGraph = () => {
      if (!nodes.value.length) return
   
      const width = chartContainer.value.clientWidth
      const height = chartContainer.value.clientHeight
      const svg = d3.select(svgRef.value)
         .attr("viewBox", [0, 0, width, height])
      
      const zoom = d3.zoom().on("zoom", (event) => g.attr("transform", event.transform))
      svg.call(zoom)
      
      globalZoom = zoom
      globalSVG = svg
   
      svg.selectAll("*").remove()
      const g = svg.append("g")

      // 1. Identify all components (Forest)
      const hasParent = new Set(links.value.filter(l => l.type === 'parent').map(l => l.target))
      const potentialRoots = nodes.value.filter(n => !hasParent.has(n.id))
      const roots = potentialRoots.filter((r, idx) => {
          // If this root has a spouse who is also in potentialRoots and appeared earlier, skip it.
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
      
      const getChildrenIds = (parentId) => {
         return links.value
            .filter(l => l.type === 'parent' && l.source === parentId)
            .map(l => l.target)
      }

      const buildHierarchy = (id, visited = new Set()) => {
         if (visited.has(id)) return null // Prevent cycles
         visited.add(id)
         const node = nodes.value.find(n => n.id === id)
         const childrenIds = getChildrenIds(id)
         return {
            ...node,
            children: childrenIds.map(cid => buildHierarchy(cid, visited)).filter(Boolean)
         }
      }

      // Group into trees
      const forest = []
      const globalVisited = new Set()
      
      // Sort potential roots to put the main high-count branch first
      potentialRoots.sort((a,b) => {
          const childrenA = getChildrenIds(a.id).length
          const childrenB = getChildrenIds(b.id).length
          return childrenB - childrenA
      })

      potentialRoots.forEach(rootNode => {
          if (!globalVisited.has(rootNode.id)) {
              const treeData = buildHierarchy(rootNode.id, globalVisited)
              if (treeData) forest.push(treeData)
          }
      })

      // Add remaining orphans just in case
      nodes.value.forEach(node => {
          if (!globalVisited.has(node.id)) {
              forest.push({...node, children: []})
              globalVisited.add(node.id)
          }
      })

      // 2. Lay out each tree in the forest
      const treeLayout = d3.tree().nodeSize([200, 300])
      const forestGroups = forest.map((treeData, i) => {
          const strategyRoot = d3.hierarchy(treeData)
          treeLayout(strategyRoot)
          return strategyRoot
      })

      // Position forest trees in a grid or horizontal spread
      let currentXOffset = width / 2
      forestGroups.forEach((root, i) => {
          const xOffset = i * 800 // Spread trees out significantly
          const treeG = g.append("g").attr("transform", `translate(${currentXOffset}, 100)`)
          
          if (i === 0) globalRoot = root // Store the main tree as default root

          // Links
          treeG.selectAll(".link")
            .data(root.links())
            .join("path")
            .attr("class", "link")
            .attr("fill", "none")
            .attr("stroke", "#cbd5e1")
            .attr("stroke-width", 2)
            .attr("d", d3.linkVertical().x(d => d.x).y(d => d.y))

          // Nodes
          const nodeGroup = treeG.selectAll(".node")
            .data(root.descendants())
            .join("g")
            .attr("class", "node")
            .attr("transform", d => `translate(${d.x},${d.y})`)

          nodeGroup.each(function(d) {
              renderCard(d3.select(this), 0, d.data)
              const spouse = getSpouse(d.data.id)
              if (spouse) {
                  const sel = d3.select(this)
                  const spouseOffset = 180 
                  sel.append("line")
                     .attr("x1", 70).attr("x2", spouseOffset - 70) 
                     .attr("y1", 0).attr("y2", 0)
                     .attr("stroke", "#ec4899").attr("stroke-width", 2).attr("stroke-dasharray", "4,2")
                  renderCard(sel, spouseOffset, spouse)
              }
          })

          currentXOffset += 1200 // Next tree offset
      })

      function renderCard(selection, dx=0, d) {
          if (!d) return
          const cardWidth = 140
          const cardHeight = 180
          const group = selection.append("g").attr("transform", `translate(${dx}, 0)`)
          const isUser = auth.user && d.username === auth.user.username

          group.append("rect")
            .attr("x", -cardWidth/2).attr("y", -cardHeight/2)
            .attr("width", cardWidth).attr("height", cardHeight).attr("rx", 12)
            .attr("fill", isUser ? "#fffbeb" : "#ffffff")
            .attr("stroke", isUser ? "#f59e0b" : "#cbd5e1")
            .attr("stroke-width", isUser ? 2 : 1)
            .attr("filter", d.is_deceased ? "grayscale(100%)" : "drop-shadow(0 10px 15px rgba(0,0,0,0.1))")
            .style("cursor", "pointer")
            .on("click", () => openMember(d))

          group.append("circle").attr("cx", 0).attr("cy", -cardHeight/4).attr("r", 35).attr("fill", "#f1f5f9").attr("stroke", "#fff").attr("stroke-width", 2)
          group.append("image")
            .attr("xlink:href", resolveImage(d.photo) || `https://ui-avatars.com/api/?name=${d.name}&background=f1f5f9&color=64748b`)
            .attr("x", -35).attr("y", -cardHeight/4 - 35).attr("width", 70).attr("height", 70)
            .attr("clip-path", `circle(35px at 0px ${-cardHeight/4}px)`)
            .style("pointer-events", "none")

          group.append("text").text(d.name.split(' ')[0]).attr("x", 0).attr("y", 15).attr("text-anchor", "middle").attr("fill", "#1e293b").attr("font-weight", "bold").attr("font-size", "14px").style("pointer-events", "none")
          
          group.append("text").text(d.gender === 'M' ? '♂' : '♀').attr("x", -15).attr("y", 35).attr("fill", d.gender === 'M' ? '#3b82f6' : '#ec4899').attr("font-size", "14px").attr("font-weight", "bold")
          group.append("text").text(`${d.age} Yrs`).attr("x", 10).attr("y", 35).attr("text-anchor", "middle").attr("fill", "#64748b").attr("font-size", "12px")
          
          if (d.is_committee) {
              group.append("text").text("★ Committee").attr("x", 0).attr("y", 65).attr("text-anchor", "middle").attr("fill", "#d97706").attr("font-size", "10px").attr("font-weight", "bold")
          }
      }

      function getSpouse(id) {
          const l = links.value.find(l => l.type === 'spouse' && (l.source === id || l.target === id))
          if (!l) return null
          const spouseId = l.source === id ? l.target : l.source
          return nodes.value.find(n => n.id === spouseId)
      }
      
      // FOCUS ON USER
      let userCoords = {x: 0, y: 0, found: false}
      console.log("Current user to focus:", auth.user?.username)
      
      forestGroups.forEach((root, i) => {
          if (userCoords.found) return
          
          root.descendants().forEach(d => {
              if (userCoords.found) return
              
              const nodeUsername = d.data.username
              if (nodeUsername) console.log("Checking node:", d.data.name, "username:", nodeUsername)
              
              // Check the primary node (bloodline)
              if (nodeUsername === auth.user?.username) {
                  userCoords = { x: (i * 1200) + width/2 + d.x, y: 100 + d.y, found: true }
                  console.log("Found user (primary):", d.data.name, userCoords)
                  return
              }
              
              // Check the spouse (rendered side-by-side)
              const spouse = getSpouse(d.data.id)
              if (spouse) {
                  const spouseUsername = spouse.username
                  if (spouseUsername) console.log("Checking spouse of", d.data.name, ":", spouse.name, "username:", spouseUsername)
                  if (spouseUsername === auth.user?.username) {
                      const spouseOffsetX = 180
                      userCoords = { x: (i * 1200) + width/2 + d.x + spouseOffsetX, y: 100 + d.y, found: true }
                      console.log("Found user (spouse):", spouse.name, userCoords)
                  }
              }
          })
      })
      
      if (userCoords.found) {
         // Focus with a slight zoom
         const scale = 1.2
         svg.transition().duration(1500).call(
             zoom.transform, 
             d3.zoomIdentity.translate(width/2 - userCoords.x*scale, height/2 - userCoords.y*scale).scale(scale)
         )
      } else {
         // Default view
         svg.transition().duration(750).call(
             zoom.transform, 
             d3.zoomIdentity.translate(width/2, 50).scale(0.5)
         )
      }
   }




onMounted(async () => {
    try {
        const res = await fetch(`${apiBase}/api/families/tree/`)
        if (res.ok) {
            const data = await res.json()
            nodes.value = data.nodes
            links.value = data.links
            initGraph()
        }
    } catch (e) {
        console.error("Tree Error", e)
    } finally {
        loading.value = false
    }
})

// Re-init graph when switching back to visual
watch(viewMode, (val) => {
    if (val === 'visual') {
        setTimeout(initGraph, 100) // wait for DOM
    }
})
</script>
