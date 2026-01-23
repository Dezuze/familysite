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
            <div 
               v-for="member in sortedMembers" 
               :key="member.id"
               @click="openMember(member)"
               class="bg-white rounded-xl overflow-hidden border border-slate-200 hover:border-amber-500/50 transition-all cursor-pointer group hover:-translate-y-1 shadow-md hover:shadow-xl"
            >
               <div class="h-24 bg-linear-to-r from-slate-200 to-slate-300 relative">
                   <div class="absolute -bottom-8 left-4 w-16 h-16 rounded-full border-4 border-white overflow-hidden bg-slate-100">
                     <img :src="member.photo || `https://ui-avatars.com/api/?name=${member.name}&background=random`" class="w-full h-full object-cover">
                   </div>
               </div>
               <div class="pt-10 px-4 pb-4">
                  <h3 class="font-bold text-slate-800 truncate">{{ member.name }}</h3>
                   <div class="flex justify-between items-center">
                     <p class="text-xs text-amber-600 uppercase tracking-wide">{{ member.relation }}</p>
                     <span v-if="member.is_committee" class="bg-blue-100 text-blue-700 text-[10px] px-2 py-0.5 rounded-full font-bold">Committee</span>
                   </div>
                   <div class="mt-3 flex items-center gap-2 text-xs text-slate-500">
                      <span>{{ member.age }} Years</span>
                      <span>•</span>
                      <span>{{ member.occupation || 'N/A' }}</span>
                   </div>
               </div>
            </div>
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
import { ref, onMounted, computed, watch } from 'vue'
import * as d3 from 'd3'
import MemberDetailsModal from '~/components/MemberDetailsModal.vue'
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
const viewMode = ref('visual')
const loading = ref(true)
const svgRef = ref(null)
const chartContainer = ref(null)
const nodes = ref([])
const links = ref([])
const selectedMember = ref(null)

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

   // --- D3 Tree Logic ---
   const initGraph = () => {
      if (!nodes.value.length) return
   
      const width = chartContainer.value.clientWidth
      const height = chartContainer.value.clientHeight
      const svg = d3.select(svgRef.value)
         .attr("viewBox", [0, 0, width, height])
      
      const zoom = d3.zoom().on("zoom", (event) => g.attr("transform", event.transform))
      svg.call(zoom)
      
      // Store globals for search focus
      globalZoom = zoom
      globalSVG = svg
   
      svg.selectAll("*").remove()
      const g = svg.append("g").attr("transform", `translate(${width/2}, 50)`) // Start top-center
   
      // 1. Build Hierarchy
      const hasParent = new Set(links.value.filter(l => l.type === 'parent').map(l => l.target))
      const roots = nodes.value.filter(n => !hasParent.has(n.id))
      const primaryRoot = roots.find(n => n.gender === 'M') || roots[0]
      
      if (!primaryRoot) return 
   
      const getChildren = (parentId) => {
         return links.value
            .filter(l => l.type === 'parent' && l.source === parentId)
            .map(l => l.target)
      }
   
      const buildHierarchy = (id) => {
         const childrenIds = getChildren(id)
         const uniqueChildren = [...new Set(childrenIds)]
         const node = nodes.value.find(n => n.id === id)
         return {
            ...node,
            children: uniqueChildren.map(childId => buildHierarchy(childId))
         }
      }
   
      const hierarchyData = buildHierarchy(primaryRoot.id)
      const root = d3.hierarchy(hierarchyData)
      globalRoot = root // Store for search
      const treeLayout = d3.tree().nodeSize([180, 240]) 
      treeLayout(root)
   
      // Helper for spouse
      const getSpouse = (id) => {
          const l = links.value.find(l => l.type === 'spouse' && (l.source === id || l.target === id))
          if (!l) return null
          const spouseId = l.source === id ? l.target : l.source
          return nodes.value.find(n => n.id === spouseId)
      }
   
      // Draw Links
      g.selectAll(".link")
        .data(root.links())
        .join("path")
        .attr("class", "link")
        .attr("fill", "none")
        .attr("stroke", "#cbd5e1") // Slate 300 - lighter
        .attr("stroke-width", 2)
        .attr("d", d3.linkVertical()
            .x(d => d.x)
            .y(d => d.y)
        )
   
      const nodeGroup = g.selectAll(".node")
        .data(root.descendants())
        .join("g")
        .attr("class", "node")
        .attr("transform", d => `translate(${d.x},${d.y})`)
   
      // Render Card Node (Light Theme)
      const renderCard = (selection, dx=0, data=null) => {
         const d = data || selection.datum().data 
         if (!d) return

         const cardWidth = 140
         const cardHeight = 180
         // Center card on x
         const x = dx - cardWidth/2
         const y = -cardHeight/2 

         const group = selection.append("g").attr("transform", `translate(${dx}, 0)`)
         
         const isUser = auth.user && d.username === auth.user.username

         // Card Background
         group.append("rect")
            .attr("x", -cardWidth/2)
            .attr("y", -cardHeight/2)
            .attr("width", cardWidth)
            .attr("height", cardHeight)
            .attr("rx", 12)
            .attr("fill", isUser ? "#fffbeb" : "#ffffff") // Amber tint (very light) or white
            .attr("stroke", isUser ? "#f59e0b" : "#cbd5e1") // Slate 300 border
            .attr("stroke", isUser ? "#f59e0b" : "#cbd5e1") // Slate 300 border
            .attr("stroke-width", isUser ? 2 : 1)
            .attr("filter", d.is_deceased ? "grayscale(100%)" : "drop-shadow(0 10px 15px rgba(0,0,0,0.1))") // Grayscale if deceased
            .style("cursor", "pointer")
            .on("click", () => openMember(d))

         // Image Container
         group.append("circle")
            .attr("cx", 0)
            .attr("cy", -cardHeight/4) 
            .attr("r", 35)
            .attr("fill", "#f1f5f9") // Slate 100
            .attr("stroke", "#fff")
            .attr("stroke-width", 2)
         
         // Image
         group.append("image")
            .attr("xlink:href", d.photo || `https://ui-avatars.com/api/?name=${d.name}&background=f1f5f9&color=64748b`)
            .attr("x", -35)
            .attr("y", -cardHeight/4 - 35)
            .attr("width", 70)
            .attr("height", 70)
            .attr("clip-path", `circle(35px at 0px ${-cardHeight/4}px)`)
            .style("pointer-events", "none")

         // Name
         group.append("text")
            .text(d.name.split(' ')[0]) 
            .attr("x", 0)
            .attr("y", 15)
            .attr("text-anchor", "middle")
            .attr("fill", "#1e293b") // Slate 800
            .attr("font-weight", "bold")
            .attr("font-size", "14px")
            .style("pointer-events", "none")
         
         // Gender Icon + Age
         const genderIcon = d.gender === 'M' ? '♂' : '♀'
         const genderColor = d.gender === 'M' ? '#3b82f6' : '#ec4899'
         
         group.append("text")
             .text(genderIcon)
             .attr("x", -15)
             .attr("y", 35)
             .attr("fill", genderColor)
             .attr("font-size", "14px")
             .attr("font-weight", "bold")

         group.append("text")
            .text(`${d.age} Yrs`)
            .attr("x", 10) // Offset slightly right
            .attr("y", 35)
            .attr("text-anchor", "middle")
            .attr("fill", "#64748b")
            .attr("font-size", "12px")
            
         // Committee Badge
         if (d.is_committee) {
             group.append("rect")
                 .attr("x", -cardWidth/2)
                 .attr("y", cardHeight/2 - 24)
                 .attr("width", cardWidth)
                 .attr("height", 24)
                 .attr("rx", 0) // Bottom strip? Or rounded bottom?
                 // Let's do a pill
             
             // Actually, a star badge at top right or pill at bottom
             group.append("text")
                 .text("★ Committee")
                 .attr("x", 0)
                 .attr("y", 65)
                 .attr("text-anchor", "middle")
                 .attr("fill", "#d97706") // Amber 600
                 .attr("font-size", "10px")
                 .attr("font-weight", "bold")
         }
      }
      
      // Render Nodes
      nodeGroup.each(function(d) {
          renderCard(d3.select(this), 0, d.data)
      })
   
      // Spouses
      nodeGroup.each(function(d) {
          const spouse = getSpouse(d.data.id)
          if (spouse) {
              const sel = d3.select(this)
              const spouseOffset = 160 
              sel.append("line")
                 .attr("x1", 70) 
                 .attr("x2", spouseOffset - 70) 
                 .attr("y1", 0)
                 .attr("y2", 0)
                 .attr("stroke", "#ec4899")
                 .attr("stroke-width", 2)
                 .attr("stroke-dasharray", "4,2")
              renderCard(sel, spouseOffset, spouse)
          }
      })
      
      // FOCUS ON USER
      // Find coordinates of user
      let userNode = null
      let userX = 0
      let userY = 0
      
      // Search in hierarchy descendants
      userNode = root.descendants().find(d => d.data.username === auth.user?.username)
      if (userNode) {
          userX = userNode.x
          userY = userNode.y
      } else {
          // Check spouses?
          // This is harder since spouses are not in 'descendants' list as distinct nodes usually in this layout?
          // Actually no, our API returns all nodes, but Hierarchy filters only bloodline.
          // Spouses are drawn manually.
          // Loop through all members and check if spouse matches user
          const userMember = nodes.value.find(n => n.username === auth.user?.username)
          if (userMember && !userNode) {
             // Maybe they are a spouse of someone in the tree?
             // Find who they are spouse of
             const partnerLink = links.value.find(l => l.type === 'spouse' && (l.source === userMember.id || l.target === userMember.id))
             if (partnerLink) {
                 const partnerId = partnerLink.source === userMember.id ? partnerLink.target : partnerLink.source
                 const partnerNode = root.descendants().find(d => d.data.id === partnerId)
                 if (partnerNode) {
                     userX = partnerNode.x + 160 // Offset for spouse
                     userY = partnerNode.y
                     userNode = true // Marker found
                 }
             }
          }
      }
      
      if (userNode) {
         // Focus animation
         const scale = 1.2
         svg.transition().duration(1500).call(
             zoom.transform, 
             d3.zoomIdentity.translate(width/2 - userX*scale, height/2 - userY*scale).scale(scale)
         )
      } else {
         // Default Center Top
         svg.transition().duration(750).call(
             zoom.transform, 
             d3.zoomIdentity.translate(width/2, 50).scale(0.8)
         )
      }
   }




onMounted(async () => {
    try {
        const res = await fetch('http://localhost:8000/api/families/tree/')
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
