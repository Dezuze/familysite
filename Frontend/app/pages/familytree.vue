<template>
    <div class="h-screen w-screen text-slate-800 font-sans pt-20 relative overflow-hidden flex flex-col bg-[#F8FAFC]">
    
    <!-- Subtle dark lineage grid pattern -->
    <div class="absolute inset-0 opacity-[0.04] pointer-events-none" style="background-image: radial-gradient(circle, #CBD5E1 1.2px, transparent 1.2px); background-size: 26px 26px;"></div>
    
    <!-- Floating Unified Controls Area -->
    <div class="w-full px-4 sm:px-6 lg:px-8 shrink-0 z-40 mt-3 mb-2 pointer-events-none">
        <div class="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-3 bg-white/95 backdrop-blur-xl p-2.5 px-4 rounded-2xl shadow-[0_8px_30px_rgb(0,0,0,0.06)] border border-slate-200/90 pointer-events-auto">
            
            <!-- View Mode & Branch Jump Controls -->
            <div class="flex items-center gap-2 flex-wrap">
                <!-- View Mode Toggle -->
                <div class="bg-slate-100 rounded-xl p-1 flex border border-slate-200 shadow-inner">
                    <button 
                        @click="switchToOverview"
                        :class="['px-3 sm:px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all', viewMode==='visual' && visualSubMode==='overview' ? 'bg-brand-gold text-white shadow-md' : 'text-slate-500 hover:text-slate-800']"
                    >
                        {{ t('familyTree.labels.treeOverview') }}
                    </button>
                    <button 
                        @click="switchToLineage"
                        :class="['px-3 sm:px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all', viewMode==='visual' && visualSubMode==='lineage' ? 'bg-brand-gold text-white shadow-md' : 'text-slate-500 hover:text-slate-800']"
                    >
                        {{ t('familyTree.labels.branchLineage') }}
                    </button>
                    <button 
                        @click="viewMode = 'grid'"
                        :class="['px-3 sm:px-3.5 py-1.5 rounded-lg text-xs font-bold transition-all', viewMode==='grid' ? 'bg-brand-gold text-white shadow-md' : 'text-slate-500 hover:text-slate-800']"
                    >
                        {{ t('familyTree.labels.directory') }}
                    </button>
                </div>

                <!-- Branch Quick Jump Dropdown -->
                <div class="relative">
                    <select 
                        v-model="selectedBranchJump" 
                        @change="jumpToBranch" 
                        class="px-3 py-1.5 bg-slate-50 text-slate-800 text-xs font-bold rounded-xl border border-slate-300 hover:border-slate-400 focus:outline-none focus:ring-2 focus:ring-brand-gold/50 cursor-pointer shadow-sm transition-all"
                    >
                        <option value="overview">Tree Overview (All Branches)</option>
                        <option value="35">I 1 Chandy (Whole Tree)</option>
                        <optgroup label="1. Thazhe (Lower) Branch">
                            <option value="33">II 1 Chandy Chandy (Thazhe Branch)</option>
                            <option value="196">III 1 Chandy Chandy (Kulathammakkal)</option>
                            <option value="31">III 2 Chandy Kurian (Thazhe Sub-branch)</option>
                        </optgroup>
                        <optgroup label="2. Karottu (Upper) Branch">
                            <option value="188">II 2 Chandy Kurian (Karottu Branch)</option>
                            <option value="akkare">III 4 Kurian Abraham (Akkare)</option>
                            <option value="218">III 5 Kurian Kora (Mulekkunnu)</option>
                            <option value="kuttikkal">III 6 Kurian Anthrayose (Kuttikkal)</option>
                            <option value="221">III 7 Kurian Chacko (Karottu Sub-branch)</option>
                        </optgroup>
                        <optgroup label="3. Tharavadu (Ancestral Home) Branch">
                            <option value="189">II 3 Chandy Kora (Tharavadu Branch)</option>
                            <option value="tharavadu-line-1">III 9 Kora Chandy (Tharavadu Line 1)</option>
                            <option value="224">III 12 Kora Kurian (Tharavadu Line 2)</option>
                        </optgroup>
                    </select>
                </div>

                <!-- Zoom Controls -->
                <div class="hidden sm:flex items-center gap-1 bg-slate-100 border border-slate-200 rounded-xl p-1">
                    <button @click="zoomIn" title="Zoom in" class="w-7 h-7 rounded-lg flex items-center justify-center text-slate-700 hover:bg-slate-200 text-sm font-bold transition">+</button>
                    <button @click="zoomOut" title="Zoom out" class="w-7 h-7 rounded-lg flex items-center justify-center text-slate-700 hover:bg-slate-200 text-sm font-bold transition">−</button>
                    <button @click="resetZoom" title="Fit whole tree" class="px-2 h-7 rounded-lg flex items-center justify-center text-slate-700 hover:bg-slate-200 text-[11px] font-bold transition">Fit</button>
                </div>
            </div>

            <!-- Edit Mode Toggle -->
            <div class="flex items-center gap-2">
                <button
                    @click="toggleEditMode"
                    :class="[
                        'px-3.5 py-1.5 rounded-xl text-xs font-bold transition-all duration-300 border active:scale-95',
                        editMode
                            ? 'bg-brand-gold text-white border-brand-gold shadow-md'
                            : 'bg-white text-slate-700 border-slate-300 hover:border-slate-400'
                    ]"
                >
                    {{ editMode ? t('familyTree.editor.editModeOn') : t('familyTree.editor.editMode') }}
                </button>
            </div>

            <!-- Contextual Controls (Search/Filter) -->
            <div class="flex items-center justify-end gap-3 w-full md:w-auto">
                <!-- Search -->
                <div class="relative w-full md:w-64">
                    <input 
                        v-model="searchQuery" 
                        @keyup.enter="performSearch" 
                        type="search" 
                        :placeholder="t('familyTree.header.findMember')" 
                        class="w-full pl-9 pr-3 py-1.5 rounded-xl bg-slate-50 border border-slate-300 text-slate-800 placeholder-slate-400 text-xs focus:outline-none focus:ring-2 focus:ring-brand-gold/50 transition-all"
                    >
                    <svg class="w-4 h-4 text-slate-400 absolute left-2.5 top-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
                    
                    <!-- Search Results Dropdown -->
                    <Transition name="fade-scale">
                        <div v-if="searchResults.length > 0 && viewMode === 'visual'" class="absolute top-full right-0 mt-2 w-full bg-white rounded-xl shadow-2xl border border-slate-200 max-h-60 overflow-y-auto z-50">
                            <div v-for="res in searchResults" :key="res.id" @click="focusOnMember(res)" class="px-3 py-2 hover:bg-slate-50 cursor-pointer border-b border-slate-100 last:border-0 transition-colors">
                                <div class="font-bold text-slate-800 text-xs">{{ res.name }}</div>
                                <div class="text-[10px] text-slate-500">{{ res.relation || t('familyTree.labels.member') }}</div>
                            </div>
                        </div>
                    </Transition>
                </div>

                <!-- Directory Filter Controls -->
                <div v-if="viewMode === 'grid'" class="flex flex-wrap items-center gap-2 text-xs">
                    <input type="text" v-model="filterLocation" placeholder="Location..." class="w-28 bg-white border border-slate-300 rounded-lg px-2 py-1 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-brand-gold" />
                    <input type="text" v-model="filterOccupation" placeholder="Occupation..." class="w-28 bg-white border border-slate-300 rounded-lg px-2 py-1 text-slate-700 placeholder-slate-400 focus:outline-none focus:ring-1 focus:ring-brand-gold" />
                    <select v-model="filterGender" class="bg-white border border-slate-300 rounded-lg px-2 py-1 text-slate-700 focus:outline-none">
                        <option value="">Any Gender</option>
                        <option value="M">Male</option>
                        <option value="F">Female</option>
                    </select>
                    <select v-model="filterBloodGroup" class="bg-white border border-slate-300 rounded-lg px-2 py-1 text-slate-700 focus:outline-none">
                        <option value="">Any Blood Grp</option>
                        <option v-for="bg in uniqueBloodGroups" :key="bg" :value="bg">{{ bg }}</option>
                    </select>
                </div>
            </div>
        </div>
    </div>

    <!-- Visual View (Primary Tree Canvas) -->
    <div
        v-show="viewMode === 'visual'"
        :class="['w-full flex-1 relative cursor-move bg-[#F8FAFC] select-none touch-pan-y md:touch-none transition-all duration-300', editMode ? 'md:pr-[430px]' : '']"
        :style="isMobileView ? { touchAction: 'pan-y pinch-zoom' } : {}"
        ref="chartContainer"
    >
       <!-- Tree area backdrop -->
       <div class="absolute inset-0 rounded-none" style="background: radial-gradient(ellipse at center, rgba(160,128,80,0.04) 0%, transparent 70%);"></div>
       <div v-if="isMobileView" class="absolute left-3 top-3 z-20 md:hidden">
          <button
              type="button"
              class="h-9 w-9 rounded-xl border border-slate-200 bg-white/95 text-sm font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="showMobileTreeHelp = !showMobileTreeHelp"
              aria-label="Tree help"
          >
              ?
          </button>
          <Transition name="fade-scale">
              <div
                  v-if="showMobileTreeHelp"
                  class="mt-2 w-52 rounded-xl border border-slate-200 bg-white/95 px-3 py-2 text-[11px] font-semibold text-slate-700 shadow-xl backdrop-blur"
              >
                  <p class="font-black text-slate-800">{{ t('familyTree.editor.helpTitle') }}</p>
                  <p class="mt-1 leading-relaxed">{{ t('familyTree.editor.helpTouchGesture') }}</p>
              </div>
          </Transition>
       </div>
       <div v-if="isMobileView" class="pointer-events-none absolute bottom-16 right-3 z-20 flex flex-col gap-2 md:hidden">
          <button
              type="button"
              class="pointer-events-auto h-10 w-10 rounded-xl border border-slate-200 bg-white/95 text-xl font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="adjustMobileZoom('in')"
          >
              +
          </button>
          <button
              type="button"
              class="pointer-events-auto h-10 w-10 rounded-xl border border-slate-200 bg-white/95 text-xl font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="adjustMobileZoom('out')"
          >
              -
          </button>
       </div>
       <div v-if="loading" class="absolute inset-0 flex items-center justify-center z-10">
          <div class="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-brand-gold"></div>
       </div>
      <!-- Desktop zoom controls -->
      <div class="pointer-events-none absolute right-4 top-4 z-20 hidden md:flex flex-col gap-2">
          <button
              type="button"
              class="pointer-events-auto h-10 w-10 rounded-xl border border-slate-200 bg-white/95 text-xl font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="adjustMobileZoom('in')"
              aria-label="Zoom in"
          >
              +
          </button>
          <button
              type="button"
              class="pointer-events-auto h-10 w-10 rounded-xl border border-slate-200 bg-white/95 text-xl font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="adjustMobileZoom('out')"
              aria-label="Zoom out"
          >
              -
          </button>
          <button
              type="button"
              class="pointer-events-auto h-10 w-10 rounded-xl border border-slate-200 bg-white/95 text-lg font-black text-slate-700 shadow-lg backdrop-blur active:scale-95"
              @click="toggleHorizontalCompression"
              aria-label="Toggle horizontal compression"
              title="Compress horizontally"
          >
              ↔
          </button>
      </div>
        <!-- Floating Back to Overview Banner inside Visual Canvas -->
        <Transition name="fade-scale">
            <div 
                v-if="visualSubMode === 'lineage' && !editMode" 
                class="absolute top-3 left-1/2 -translate-x-1/2 z-30 flex items-center gap-2 sm:gap-3 bg-white/95 backdrop-blur-xl px-3 sm:px-4 py-1.5 sm:py-2 rounded-2xl border border-slate-200/90 shadow-[0_8px_30px_rgb(0,0,0,0.08)] pointer-events-auto max-w-[92vw] overflow-hidden"
            >
                <button 
                    @click="switchToOverview" 
                    class="flex items-center gap-1.5 px-3 py-1.5 bg-brand-gold text-white text-xs font-bold rounded-xl hover:brightness-110 shadow-sm transition-all active:scale-95 shrink-0"
                >
                    <svg class="w-3.5 h-3.5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
                    <span>{{ t('familyTree.labels.backToOverview') }}</span>
                </button>
                <div class="h-4 w-px bg-slate-200 shrink-0"></div>
                <div class="flex items-center gap-1.5 truncate text-xs">
                    <span class="font-bold text-slate-800 truncate">{{ activeBranchHeaderTitle }}</span>
                    <span v-if="activeBranchMembersCount" class="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 shrink-0">
                        {{ activeBranchMembersCount }} {{ activeBranchMembersCount === 1 ? 'member' : 'members' }}
                    </span>
                </div>
            </div>
        </Transition>
            <svg ref="svgRef" class="w-full h-full relative z-1 touch-pan-y md:touch-none"></svg>

      <!-- Historical Branch Line Modal -->
      <Transition name="fade-scale">
          <div 
              v-if="selectedHistoricalNode" 
              class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-slate-900/40 backdrop-blur-sm"
              @click.self="selectedHistoricalNode = null"
          >
              <div class="bg-white rounded-3xl max-w-md w-full p-6 shadow-2xl border border-slate-200 space-y-4">
                  <div class="flex items-start justify-between">
                      <div>
                          <span class="inline-block px-2.5 py-0.5 rounded-full text-[10px] font-bold tracking-wide uppercase bg-amber-50 text-amber-700 border border-amber-200 mb-1.5">
                              {{ t('familyTree.labels.historicalBranch') }}
                          </span>
                          <h3 class="text-xl font-black text-slate-900">
                              {{ selectedHistoricalNode.titleMl }} • {{ selectedHistoricalNode.title }}
                          </h3>
                          <p class="text-sm font-semibold text-slate-600 mt-0.5">
                              {{ selectedHistoricalNode.romanId }} {{ selectedHistoricalNode.nameMl }} ({{ selectedHistoricalNode.name }})
                          </p>
                      </div>
                      <button 
                          @click="selectedHistoricalNode = null" 
                          class="h-8 w-8 rounded-full bg-slate-100 hover:bg-slate-200 flex items-center justify-center text-slate-500 text-sm font-bold transition-colors"
                      >
                          ✕
                      </button>
                  </div>
                  
                  <div class="p-3.5 bg-slate-50 rounded-2xl border border-slate-100 text-xs text-slate-600 leading-relaxed space-y-1.5">
                      <p>
                          <strong class="text-slate-800">Branch Lineage:</strong> 
                          Part of the {{ selectedHistoricalNode.parentBranchTitle }} (കുടുംബ ശാഖ).
                      </p>
                      <p>
                          This is an official lineage line established in the family annals. Digital profile records for descendants of this line can be added via the Tree Editor.
                      </p>
                  </div>

                  <div class="flex gap-2 pt-2">
                      <button 
                          v-if="selectedHistoricalNode.parentMemberIdNum"
                          @click="viewBranchFamilyById(selectedHistoricalNode.parentMemberIdNum); selectedHistoricalNode = null"
                          class="flex-1 px-4 py-2 bg-brand-gold text-white text-xs font-bold rounded-xl shadow-md hover:brightness-110 active:scale-95 transition-all"
                      >
                          {{ t('familyTree.labels.exploreParentBranch') }} ({{ selectedHistoricalNode.parentBranchTitle }})
                      </button>
                      <button 
                          @click="selectedHistoricalNode = null"
                          class="px-4 py-2 border border-slate-200 text-slate-600 hover:bg-slate-50 text-xs font-bold rounded-xl transition-colors"
                      >
                          Close
                      </button>
                  </div>
              </div>
          </div>
      </Transition>
    </div>

     <!-- Grid View -->
    <div v-show="viewMode === 'grid'" class="w-full flex-1 relative overflow-y-auto bg-slate-50/50">

         <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
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
                  <MemberCard :member="member" :partner="getPartnerForMember(member)" />
               </div>
            </template>
         </div>
         
         <!-- Empty State -->
         <div v-if="!loading && sortedMembers.length === 0" class="text-center text-slate-500 py-20 bg-white rounded-xl border border-slate-200 shadow-sm">
            <svg class="w-16 h-16 mx-auto text-slate-200 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z"></path></svg>
                <p class="font-bold text-slate-400">{{ t('familyTree.empty.noMembersFound') }}</p>
         </div>
     </div>

     <!-- Member Modal -->
     <MemberDetailsModal 
                    v-if="selectedMember && !editMode" 
                :member="selectedMemberForModal" 
          :canEdit="canEditSelected"
        @edit="openQuickEditForSelected"
        @close="selectedMember = null" 
     />

     <div v-if="quickEditOpen && quickEditMemberId" class="fixed inset-0 z-50 flex items-end justify-center p-0 md:items-center md:p-4">
        <div class="absolute inset-0 bg-black/60" @click="quickEditOpen = false"></div>
        <div class="quick-edit-sheet relative w-full max-h-[90vh] overflow-y-auto rounded-t-3xl border border-slate-200 bg-white p-4 pb-5 shadow-2xl md:max-w-2xl md:rounded-2xl md:p-5">
            <div class="sticky top-0 z-10 mb-4 flex items-center justify-between border-b border-slate-100 bg-white pb-3 pt-1">
                <div>
                    <h3 class="text-lg font-black text-slate-900">Add Relative</h3>
                    <p class="text-xs text-slate-500">Create a new relative or link an existing one</p>
                </div>
                <button class="rounded-lg px-2 py-1 text-xs font-bold text-slate-500 hover:bg-slate-100" @click="quickEditOpen = false">Close</button>
            </div>

            <div class="space-y-3 rounded-2xl border border-slate-200 bg-slate-50/60 p-3.5">
                <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">{{ t('familyTree.editor.addRelativeTitle') }}</div>
                <div class="grid grid-cols-2 gap-2.5 rounded-xl border border-slate-200 bg-white p-1.5">
                    <button
                        type="button"
                        class="rounded-lg px-2 py-1.5 text-xs font-bold transition-all duration-300"
                        :class="addRelativeMode === 'create' ? 'bg-brand-gold text-white' : 'text-slate-600 hover:bg-slate-100'"
                        @click="addRelativeMode = 'create'; linkSearchQuery = ''; resetLinkTarget(); editorError = ''; editorSuccess = ''"
                    >
                        {{ t('familyTree.editor.mode.create') }}
                    </button>
                    <button
                        type="button"
                        class="rounded-lg px-2 py-1.5 text-xs font-bold transition-all duration-300"
                        :class="addRelativeMode === 'link' ? 'bg-brand-gold text-white' : 'text-slate-600 hover:bg-slate-100'"
                        @click="addRelativeMode = 'link'; resetAddRelativeForm(); resetLinkTarget(); linkSearchQuery = ''; editorError = ''; editorSuccess = ''"
                    >
                        {{ t('familyTree.editor.mode.link') }}
                    </button>
                </div>
                <select v-model="addRelationType" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold">
                    <option value="PARENT">{{ t('familyTree.editor.relation.parent') }}</option>
                    <option value="SPOUSE" :disabled="selectedMemberHasSpouse">{{ t('familyTree.editor.relation.spouse') }}</option>
                    <option value="SIBLING">{{ t('familyTree.editor.relation.sibling') }}</option>
                    <option value="CHILD">{{ t('familyTree.editor.relation.child') }}</option>
                </select>
                <p v-if="duplicateRelationWarning" class="text-[11px] font-semibold text-amber-700">{{ duplicateRelationWarning }}</p>
                <template v-if="addRelativeMode === 'create'">
                    <div class="grid grid-cols-1 gap-2 sm:grid-cols-2">
                        <input v-model="addRelativeForm.first_name" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.firstName')" />
                        <input v-model="addRelativeForm.last_name" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.lastName')" />
                    </div>
                    <div class="w-full flex gap-2">
                        <input v-model="addRelativeForm.name_ml" class="flex-1 rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" placeholder="Malayalam name (optional)" />
                        <button
                            type="button"
                            class="shrink-0 rounded-xl border border-brand-gold/40 px-3 py-2 text-xs font-bold text-brand-gold hover:bg-brand-gold/10 disabled:opacity-50"
                            :disabled="nameLookupLoadingAdd"
                            @click="lookupMalayalamNameForAddRelative"
                        >
                            {{ nameLookupLoadingAdd ? 'Searching...' : 'Malayalam' }}
                        </button>
                    </div>
                    <input v-model="addRelativeForm.family_name" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" placeholder="Family / House Name (optional)" />
                    <input v-model="addRelativeForm.nickname" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.nickname')" />
                    <input v-model="addRelativeForm.member_id" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" placeholder="Member ID (optional)" />
                    <select v-model="addRelativeForm.gender" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold">
                        <option value="M">{{ t('onboarding.gender.male') }}</option>
                        <option value="F">{{ t('onboarding.gender.female') }}</option>
                        <option value="O">{{ t('onboarding.gender.other') }}</option>
                    </select>
                    <div class="grid grid-cols-2 gap-2">
                        <button type="button" class="rounded-xl border px-2 py-2 text-xs font-bold" :class="addRelativeUseDob ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-600'" @click="addRelativeUseDob = true">{{ t('onboarding.fields.dateOfBirth') }}</button>
                        <button type="button" class="rounded-xl border px-2 py-2 text-xs font-bold" :class="!addRelativeUseDob ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-600'" @click="addRelativeUseDob = false">{{ t('onboarding.managedModal.age') }}</button>
                    </div>
                    <input v-if="addRelativeUseDob" v-model="addRelativeForm.date_of_birth" type="date" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" />
                    <input v-else v-model="addRelativeForm.age" type="number" min="0" max="150" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.managedModal.enterAge')" />
                    <input v-model="addRelativeForm.wedding_anniversary" type="date" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" placeholder="Wedding anniversary" />
                    <select v-model="addRelativeForm.blood_group" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold">
                        <option value="">{{ t('onboarding.placeholders.selectBloodGroup') }}</option>
                        <option value="Unknown">{{ t('onboarding.bloodGroup.unknown') }}</option>
                        <option value="A+">A+</option><option value="A-">A-</option><option value="B+">B+</option><option value="B-">B-</option><option value="O+">O+</option><option value="O-">O-</option><option value="AB+">AB+</option><option value="AB-">AB-</option>
                    </select>
                    <input v-model="addRelativeForm.occupation" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.occupation')" />
                    <input v-model="addRelativeForm.place_of_work" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" placeholder="Place of work" />
                    <input v-model="addRelativeForm.education" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.education')" />
                    <input v-model="addRelativeForm.phone_no" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.phoneNumber')" />
                    <input v-model="addRelativeForm.email_id" type="email" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.email')" />
                    <input v-model="addRelativeForm.church_parish" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.parishChurch')" />
                    <textarea v-model="addRelativeForm.address" rows="2" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.address')"></textarea>
                    <textarea v-model="addRelativeForm.bio" rows="2" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.fields.bio')"></textarea>
                    <label class="flex items-center gap-2 rounded-xl border border-slate-200 bg-white px-3 py-2 text-xs font-semibold text-slate-700">
                        <input v-model="addRelativeForm.is_deceased" type="checkbox" class="accent-brand-gold" />
                        {{ t('onboarding.managedModal.isDeceased') }}
                    </label>
                    <input v-if="addRelativeForm.is_deceased" v-model="addRelativeForm.date_of_death" type="date" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" />
                    <div class="space-y-2">
                        <label class="block text-xs font-semibold uppercase tracking-wide text-slate-500">Profile photo</label>
                        <div class="flex items-center gap-3 rounded-xl border border-slate-200 bg-white px-3 py-2">
                            <div class="h-12 w-12 shrink-0 overflow-hidden rounded-full border border-slate-200 bg-slate-50">
                                <img v-if="addRelativeAvatarPreview" :src="addRelativeAvatarPreview" alt="Member preview" class="h-full w-full object-cover" />
                                <div v-else class="flex h-full w-full items-center justify-center text-[10px] font-bold text-slate-400">No photo</div>
                            </div>
                            <label class="inline-flex cursor-pointer rounded-lg border border-brand-gold/40 px-3 py-2 text-xs font-bold text-brand-gold transition-colors hover:bg-brand-gold/10">
                                Upload & Crop
                                <input type="file" accept="image/*" class="hidden" @change="onAddRelativeAvatarChange" />
                            </label>
                            <button
                                v-if="addRelativeAvatarPreview"
                                type="button"
                                class="rounded-lg border border-slate-200 px-2 py-1.5 text-[11px] font-bold text-slate-600 hover:bg-slate-100"
                                @click="clearAddRelativeAvatar"
                            >
                                Remove
                            </button>
                        </div>
                    </div>
                </template>
                <template v-else>
                    <div class="relative">
                        <input
                            v-model="linkSearchQuery"
                            class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm"
                            :placeholder="t('familyTree.editor.placeholders.searchExisting')"
                            @input="onLinkSearchInput"
                        />
                        <div v-if="linkSearchLoading" class="absolute right-3 top-2.5 text-xs font-semibold text-slate-400">{{ t('familyTree.editor.searching') }}</div>
                        <Transition name="fade-scale">
                        <div v-if="linkSearchResults.length" class="absolute z-50 mt-1 max-h-44 w-full overflow-y-auto rounded-xl border border-slate-200 bg-white shadow-xl">
                            <button
                                v-for="candidate in linkSearchResults"
                                :key="candidate.id"
                                type="button"
                                class="block w-full border-b border-slate-100 px-3 py-2 text-left last:border-b-0 transition-colors duration-200 hover:bg-slate-50"
                                @click="selectLinkTarget(candidate)"
                            >
                                <div class="text-sm font-bold text-slate-800">{{ candidate.name }}</div>
                                <div class="text-xs text-slate-500">{{ candidate.relation || t('familyTree.labels.member') }}</div>
                            </button>
                        </div>
                        </Transition>
                    </div>
                    <Transition name="fade-scale">
                        <div v-if="selectedLinkTarget" class="flex items-center justify-between rounded-xl border border-emerald-200 bg-emerald-50 px-3 py-2 text-xs font-semibold text-emerald-700">
                            <span>{{ t('familyTree.editor.selectedLabel', { name: selectedLinkTarget.name }) }}</span>
                            <button type="button" class="text-emerald-700 transition-colors duration-200 hover:text-emerald-900" @click="resetLinkTarget(); linkSearchQuery = ''">{{ t('familyTree.editor.clear') }}</button>
                        </div>
                    </Transition>
                </template>
                <button
                    class="w-full rounded-xl bg-brand-gold px-3 py-2.5 text-sm font-black text-white shadow-lg transition-all duration-300 hover:brightness-110 active:scale-95 disabled:opacity-50"
                    :disabled="editorLoading || !canSubmitAddRelative"
                    @click="addRelativeFromPanel"
                >
                    {{ editorLoading ? t('familyTree.editor.saving') : t('familyTree.editor.addRelative') }}
                </button>
            </div>
        </div>
     </div>

      <div
          v-if="editMode && isEditorSheetOpen"
          class="fixed inset-0 z-30 pointer-events-none bg-slate-900/10 backdrop-blur-[0.5px] md:hidden"
      ></div>

      <button
          v-if="editMode && !isEditorSheetOpen"
          class="fixed bottom-4 right-4 z-40 rounded-2xl border border-brand-gold/40 bg-white px-4 py-2 text-xs font-black text-brand-gold shadow-xl transition-all duration-300 hover:-translate-y-0.5 hover:shadow-2xl active:scale-95 md:hidden"
          @click="openEditorSheet"
      >
          {{ t('familyTree.editor.openTreeEditor') }}
      </button>

      <Transition name="slide-up-editor">
      <div
          v-if="editMode && isEditorSheetOpen"
          class="editor-sheet fixed inset-x-0 bottom-0 z-40 max-h-[72vh] overflow-y-auto rounded-t-3xl border border-slate-200 bg-white/96 px-4 pt-0 pb-6 shadow-2xl backdrop-blur transition-all duration-300 md:inset-x-auto md:bottom-4 md:right-4 md:top-28 md:w-[410px] md:max-h-[calc(100vh-8rem)] md:rounded-2xl md:p-5"
          :style="mobileEditorSheetStyle"
          :class="isResizingEditorSheet ? 'duration-0' : ''"
      >
          <div class="mb-2 flex justify-center md:hidden">
                <button
                    type="button"
                    class="h-8 w-24 touch-none rounded-full border border-slate-200 bg-white/90"
                    aria-label="Resize editor panel"
                    @pointerdown.prevent="startEditorResize"
                >
                    <span class="mx-auto block h-1.5 w-10 rounded-full bg-slate-300"></span>
                </button>
          </div>
          <div class="sticky top-0 z-20 mb-3 flex items-center justify-between border-b border-slate-100 bg-white/95 pb-3 pt-3 backdrop-blur">
                <div>
                     <h3 class="text-lg font-black text-slate-900">{{ t('familyTree.editor.title') }}</h3>
                     <p class="text-xs font-medium text-slate-500">{{ t('familyTree.editor.subtitle') }}</p>
                </div>
                <div class="flex items-center gap-2">
                     <button class="rounded-lg px-2 py-1 text-xs font-bold text-slate-500 transition-colors duration-200 hover:bg-slate-100 md:hidden" @click="closeEditorSheet">{{ t('familyTree.editor.hide') }}</button>
                     <button class="rounded-lg px-2 py-1 text-xs font-bold text-slate-500 transition-colors duration-200 hover:bg-slate-100" @click="toggleEditMode">{{ t('familyTree.editor.close') }}</button>
                </div>
          </div>

        <div v-if="selectedMember" class="space-y-4">
            <div class="rounded-2xl border border-slate-200 bg-linear-to-br from-white to-slate-50 p-3 shadow-sm">
                <div class="space-y-2">
                    <div class="text-base font-black text-slate-900">
                        {{ householdTitle }}
                    </div>
                    <div class="text-[11px] text-slate-500">
                        {{ selectedMember.relation || selectedMember.role || t('familyTree.labels.member') }}
                    </div>
                    <div v-if="selectedMemberHouseholdMembers.length > 1" class="grid gap-2 sm:grid-cols-2">
                        <button
                            v-for="person in selectedMemberHouseholdMembers"
                            :key="person.id"
                            type="button"
                            @click="selectHouseholdMember(person)"
                            :class="['rounded-xl border p-3 text-left transition duration-200', person.id === selectedMember.id ? 'border-brand-gold bg-brand-gold/10 shadow-inner' : 'border-slate-200 bg-white hover:border-brand-gold/40 hover:bg-slate-50']"
                        >
                            <div class="flex items-center justify-between gap-2">
                                <div class="text-sm font-black text-slate-900">{{ person.name }}</div>
                                <span v-if="person.id === selectedMember.id" class="rounded-full bg-brand-gold/10 px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-brand-gold">Selected</span>
                            </div>
                            <div class="mt-2 text-[11px] text-slate-500">
                                {{ person.member_id || person.id || t('memberDetailsModal.labels.notAvailable') }}
                            </div>
                        </button>
                    </div>
                </div>

            </div>



            <!-- Tabs -->
            <div class="flex items-center gap-1 overflow-x-auto rounded-xl bg-slate-100 p-1">
                <button
                    v-for="tab in ['profile', 'details', 'contact', 'relationships', 'settings']"
                    :key="tab"
                    @click="editorTab = tab as any"
                    :class="[
                        'flex-1 whitespace-nowrap rounded-lg px-3 py-1.5 text-xs font-bold capitalize transition-all duration-200',
                        editorTab === tab
                            ? 'bg-white text-brand-gold shadow-sm'
                            : 'text-slate-500 hover:text-slate-700'
                    ]"
                >
                    {{ tab }}
                </button>
            </div>

            <!-- Tab Content: Profile -->
            <div v-show="editorTab === 'profile'" class="space-y-3.5 mt-4">
                <div class="grid grid-cols-1 gap-3.5 md:grid-cols-2">
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">First name</label>
                        <input v-model="quickEditForm.first_name" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="First name" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Last name</label>
                        <input v-model="quickEditForm.last_name" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Last name" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Member ID</label>
                        <input v-model="quickEditForm.member_id" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Member ID" />
                    </div>
                    <div class="md:col-span-2">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500 mb-1 block">Malayalam name</label>
                        <div class="flex gap-2">
                            <input v-model="quickEditForm.name_ml" class="flex-1 rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Malayalam name" />
                            <button
                                type="button"
                                class="shrink-0 rounded-xl border border-brand-gold/40 px-3 py-2 text-xs font-bold text-brand-gold hover:bg-brand-gold/10 disabled:opacity-50"
                                :disabled="nameLookupLoadingQuick"
                                @click="lookupMalayalamNameForQuickEdit"
                            >
                                {{ nameLookupLoadingQuick ? 'Searching...' : 'Malayalam' }}
                            </button>
                        </div>
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Nickname</label>
                        <input v-model="quickEditForm.nickname" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Nickname" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Gender</label>
                        <select v-model="quickEditForm.gender" class="rounded-xl border border-slate-200 px-3 py-2 text-sm">
                            <option value="M">Male</option>
                            <option value="F">Female</option>
                            <option value="O">Other</option>
                        </select>
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Date of birth</label>
                        <input v-model="quickEditForm.date_of_birth" type="date" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Age</label>
                        <input v-model="quickEditForm.age" type="number" min="0" max="150" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Age" />
                    </div>
                    <div class="md:col-span-2 flex flex-col gap-1 rounded-xl border border-slate-200 px-3 py-2">
                        <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">Is deceased</div>
                        <label class="flex items-center gap-2 text-sm text-slate-700">
                            <input v-model="quickEditForm.is_deceased" type="checkbox" class="accent-brand-gold" />
                            Yes
                        </label>
                    </div>
                    <div v-if="quickEditForm.is_deceased" class="md:col-span-2 flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Date of death</label>
                        <input v-model="quickEditForm.date_of_death" type="date" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" />
                    </div>
                    <div class="md:col-span-2 flex flex-col gap-2">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Profile picture</label>
                        <div class="flex items-center gap-4">
                            <div v-if="quickEditAvatarPreview" class="h-16 w-16 shrink-0 overflow-hidden rounded-full border-2 border-slate-200">
                                <img :src="quickEditAvatarPreview" alt="Member preview" class="h-full w-full object-cover" />
                            </div>
                            <div class="flex flex-col gap-1 w-full">
                                <input type="file" accept="image/*" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm" @change="onQuickEditAvatarChange" />
                                <button v-if="quickEditAvatarPreview" type="button" class="text-xs font-semibold text-red-500 text-left hover:underline" @click="clearQuickEditAvatar">Remove selected photo</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Tab Content: Details -->
            <div v-show="editorTab === 'details'" class="space-y-3.5 mt-4">
                <div class="grid grid-cols-1 gap-3.5 md:grid-cols-2">
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Branch</label>
                        <select v-model="quickEditForm.branch" class="rounded-xl border border-slate-200 px-3 py-2 text-sm">
                            <option value="">Select branch</option>
                            <option value="Thazhe branch">Thazhe branch</option>
                            <option value="Karottu branch">Karottu branch</option>
                            <option value="Tharavadu branch">Tharavadu branch</option>
                            <option value="Kulathamackal branch">Kulathamackal branch</option>
                            <option value="Akkare branch">Akkare branch</option>
                            <option value="Mulekkunnu branch">Mulekkunnu branch</option>
                            <option value="Kuttickal branch">Kuttickal branch</option>
                        </select>
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Generation</label>
                        <select v-model="quickEditForm.generation" class="rounded-xl border border-slate-200 px-3 py-2 text-sm">
                            <option :value="null">Auto</option>
                            <option :value="0">I</option>
                            <option :value="1">II</option>
                            <option :value="2">III</option>
                            <option :value="3">IV</option>
                            <option :value="4">V</option>
                            <option :value="5">VI</option>
                            <option :value="6">VII</option>
                            <option :value="7">VIII</option>
                            <option :value="8">IX</option>
                            <option :value="9">X</option>
                        </select>
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Blood group</label>
                        <input v-model="quickEditForm.blood_group" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Blood group" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Occupation</label>
                        <input v-model="quickEditForm.occupation" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Occupation" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Place of Work</label>
                        <input v-model="quickEditForm.place_of_work" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Place of work" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Education</label>
                        <input v-model="quickEditForm.education" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Education" />
                    </div>
                    <div class="md:col-span-2 flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Bio</label>
                        <textarea v-model="quickEditForm.bio" rows="2" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Bio"></textarea>
                    </div>
                </div>
            </div>

            <!-- Tab Content: Contact -->
            <div v-show="editorTab === 'contact'" class="space-y-3.5 mt-4">
                <div class="grid grid-cols-1 gap-3.5 md:grid-cols-2">
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Phone</label>
                        <input v-model="quickEditForm.phone_no" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Phone" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Email</label>
                        <input v-model="quickEditForm.email_id" type="email" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Email" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Parish</label>
                        <input v-model="quickEditForm.church_parish" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Parish" />
                    </div>
                    <div class="flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Wedding anniversary</label>
                        <input v-model="quickEditForm.wedding_anniversary" type="date" class="w-full rounded-xl border border-slate-200 px-3 py-2 text-sm" />
                    </div>
                    <div class="md:col-span-2 flex flex-col gap-1">
                        <label class="text-xs font-semibold uppercase tracking-wide text-slate-500">Address</label>
                        <textarea v-model="quickEditForm.address" rows="2" class="rounded-xl border border-slate-200 px-3 py-2 text-sm" placeholder="Address"></textarea>
                    </div>
                </div>
            </div>

            <!-- Tab Content: Relationships -->
            <div v-show="editorTab === 'relationships'" class="space-y-4 mt-4">
                <div class="grid grid-cols-2 gap-2.5 sm:grid-cols-4">
                    <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!allowedActions.can_add_parent" :class="addRelationType === 'PARENT' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('PARENT')">{{ t('familyTree.editor.actions.parent') }}</button>
                    <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!canAddSpouseNow" :class="addRelationType === 'SPOUSE' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('SPOUSE')">{{ t('familyTree.editor.actions.spouse') }}</button>
                    <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!allowedActions.can_add_sibling" :class="addRelationType === 'SIBLING' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('SIBLING')">{{ t('familyTree.editor.actions.sibling') }}</button>
                    <button class="rounded-xl border px-3 py-2 text-xs font-bold transition-all duration-300 disabled:cursor-not-allowed disabled:opacity-50" :disabled="!allowedActions.can_add_child" :class="addRelationType === 'CHILD' ? 'border-brand-gold/60 bg-brand-gold/10 text-brand-gold' : 'border-slate-200 text-slate-700 hover:border-brand-gold/40 hover:text-brand-gold'" @click="setRelationType('CHILD')">{{ t('familyTree.editor.actions.child') }}</button>
                </div>
                <div class="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 text-xs text-slate-500 text-center">
                    Click a button above to add a new relative or link an existing one.
                </div>
                <button
                    v-if="lastLinkedRelation"
                    class="w-full rounded-xl border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700 transition-all duration-300 hover:bg-slate-50 active:scale-95 disabled:opacity-50"
                    :disabled="editorLoading"
                    @click="undoLastLinkedRelation"
                >
                    Undo last link
                </button>
            </div>

            <!-- Tab Content: Settings -->
            <div v-show="editorTab === 'settings'" class="space-y-4 mt-4">
                <div class="space-y-2 rounded-2xl border border-slate-200 bg-slate-50/60 p-3">
                    <div class="text-xs font-semibold uppercase tracking-wide text-slate-500">{{ t('familyTree.editor.accessOwnership') }}</div>
                    <div class="flex flex-wrap gap-2">
                        <span class="rounded-full bg-slate-100 px-2 py-1 text-[10px] font-bold uppercase text-slate-600" v-if="contextOwnership.has_account">{{ t('familyTree.editor.badges.hasAccount') }}</span>
                        <span class="rounded-full bg-green-100 px-2 py-1 text-[10px] font-bold uppercase text-green-700" v-if="contextOwnership.is_independent">{{ t('familyTree.editor.badges.independent') }}</span>
                        <span class="rounded-full bg-amber-100 px-2 py-1 text-[10px] font-bold uppercase text-amber-700" v-if="contextOwnership.created_by_me">{{ t('familyTree.editor.badges.managedByYou') }}</span>
                    </div>

                    <div v-if="canShowGiveAccess" class="space-y-2 mt-2">
                        <input v-model="accessUsername" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.giveAccess.username')" />
                        <input v-model="accessPassword" class="w-full rounded-xl border border-slate-200 bg-white px-3 py-2 text-sm" :placeholder="t('onboarding.giveAccess.password')" />
                        <button
                            class="w-full rounded-xl border border-brand-gold/40 px-3 py-2 text-xs font-bold text-brand-gold transition-all duration-300 hover:bg-brand-gold/5 active:scale-95 disabled:opacity-50"
                            :disabled="accessLoading"
                            @click="giveAccessFromPanel"
                        >
                            {{ accessLoading ? t('onboarding.giveAccess.creating') : t('onboarding.managed.giveAccess') }}
                        </button>
                    </div>

                    <button
                        v-if="canGoIndependent"
                        class="w-full mt-2 rounded-xl border border-slate-200 px-3 py-2 text-xs font-bold text-slate-700 transition-all duration-300 hover:bg-slate-50 active:scale-95 disabled:opacity-50"
                        :disabled="accessLoading"
                        @click="goIndependentFromPanel"
                    >
                        {{ t('familyTree.editor.becomeIndependent') }}
                    </button>

                    <button
                        class="w-full mt-2 rounded-xl border border-brand-gold/40 px-3 py-2 text-xs font-bold text-brand-gold transition-all duration-300 hover:bg-brand-gold/5 active:scale-95 disabled:opacity-50"
                        :disabled="inviteLoading"
                        @click="generateInviteLink"
                    >
                        {{ inviteLoading ? t('onboarding.giveAccess.creating') : t('nav.inviteMember') }}
                    </button>
                    <div v-if="inviteLink" class="mt-2 rounded-xl border border-slate-200 bg-white p-2">
                        <p class="break-all text-[11px] font-medium text-slate-600">{{ inviteLink }}</p>
                        <button
                            type="button"
                            class="mt-2 w-full rounded-lg border border-slate-200 px-2 py-1.5 text-xs font-bold text-slate-700 transition-colors hover:bg-slate-50"
                            @click="copyInviteLink"
                        >
                            {{ t('familyTree.editor.copyLink', 'Copy Link') }}
                        </button>
                    </div>
                </div>

                <button
                    class="w-full rounded-xl border border-red-200 px-3 py-2 text-xs font-bold text-red-600 transition-all duration-300 hover:bg-red-50 active:scale-95 disabled:opacity-50"
                    :disabled="editorLoading || !allowedActions.can_remove"
                    @click="removeSelectedMember"
                >
                    {{ t('familyTree.editor.removeSelected') }}
                </button>
            </div>

            <p v-if="quickEditError" class="mt-3 rounded-lg bg-red-50 px-3 py-2 text-xs font-medium text-red-700">{{ quickEditError }}</p>
            <p v-if="quickEditSuccess" class="mt-3 rounded-lg bg-green-50 px-3 py-2 text-xs font-medium text-green-700">{{ quickEditSuccess }}</p>

            <div v-show="editorTab !== 'settings' && editorTab !== 'relationships'" class="sticky bottom-0 mt-4 flex justify-end gap-2 border-t border-slate-100 bg-white/95 backdrop-blur pt-3">
                <button class="rounded-xl bg-brand-gold px-3 py-2 text-xs font-black text-white disabled:opacity-50 transition-all duration-300 hover:brightness-110 shadow-lg" :disabled="quickEditLoading" @click="saveQuickEditMember">
                    {{ quickEditLoading ? 'Saving...' : 'Save Changes' }}
                </button>
            </div>

            <Transition name="fade-slide">
                <p v-if="!allowedActions.can_manage" class="mt-3 rounded-lg bg-amber-50 px-3 py-2 text-xs font-semibold text-amber-700">{{ t('familyTree.editor.permissionHint') }}</p>
            </Transition>
            <Transition name="fade-slide">
                <p v-if="editorError" class="mt-3 rounded-lg bg-red-50 px-3 py-2 text-xs font-medium text-red-700">{{ editorError }}</p>
            </Transition>
            <Transition name="fade-slide">
                <p v-if="editorSuccess" class="mt-3 rounded-lg bg-green-50 px-3 py-2 text-xs font-medium text-green-700">{{ editorSuccess }}</p>
            </Transition>
        </div>

        <div v-else class="rounded-xl border border-dashed border-slate-200 bg-slate-50 p-4 text-xs text-slate-500">
            {{ t('familyTree.editor.pickMemberHint') }}
        </div>
     </div>
      </Transition>

            <ClientOnly>
                <Teleport to="body">
                    <div v-if="showCropperModal" class="fixed inset-0 z-[100] flex items-center justify-center bg-black/80 p-4 backdrop-blur-sm">
                        <div class="w-full max-w-lg overflow-hidden rounded-3xl bg-white shadow-2xl">
                            <div class="flex items-center justify-between border-b border-gray-100 bg-slate-50 p-4">
                                <h3 class="font-bold text-slate-800">Crop profile photo</h3>
                                <button class="text-slate-400 hover:text-slate-600" @click="cancelCrop">
                                    <svg class="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                                </button>
                            </div>
                            <div class="flex justify-center bg-slate-900 p-4">
                                <Cropper
                                    ref="cropperRef"
                                    class="h-96 w-full"
                                    :src="cropperTempImage || ''"
                                    :stencil-component="CircleStencil"
                                    :stencil-props="{ aspectRatio: 1 / 1 }"
                                />
                            </div>
                            <div class="flex justify-end gap-3 border-t border-gray-100 bg-white p-4">
                                <button class="rounded-xl px-6 py-2.5 font-bold text-slate-600 transition-colors hover:bg-slate-100" @click="cancelCrop">Cancel</button>
                                <button class="rounded-xl bg-brand-gold px-6 py-2.5 font-bold text-white shadow-lg shadow-brand-gold/30 transition-all hover:brightness-110" @click="cropImage">Set photo</button>
                            </div>
                        </div>
                    </div>
                </Teleport>
            </ClientOnly>
    </div>
</template>

<script setup lang="ts">
import { computed, watch, ref, onMounted, onUnmounted } from 'vue'
import { useHead, useRuntimeConfig, useRoute, useRouter } from '#imports'
import { useI18n } from 'vue-i18n'
import * as d3 from 'd3'
import { useFamilyStore } from '~/stores/family'
import type { FamilyMember } from '~/types/family'
import { useAuthStore } from '~/stores/auth'
import friendlyErrorMessage from '~/utils/errorNormalizer'
import MemberDetailsModal from '~/components/MemberDetailsModal.vue'
import MemberCard from '~/components/MemberCard.vue'
import { Cropper, CircleStencil } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

// --- Global D3 State ---
let globalZoom: any = null        
let globalSVG: any = null         
let globalNodeCoords = new Map<number, { x: number; y: number }>()

// --- Overview Structure Model (Diagram Hierarchy) ---
export interface OverviewBranchItem {
    id: string
    memberIdNum?: number
    romanId: string
    name: string
    nameMl: string
    title: string
    titleMl: string
    subtitle?: string
    subtitleMl?: string
    isFounder?: boolean
    isBranchHead?: boolean
    parentBranchTitle?: string
    parentMemberIdNum?: number
    memberCount?: number
}

const founderNode: OverviewBranchItem = {
    id: 'root',
    memberIdNum: 35,
    romanId: 'I 1',
    name: 'Chandy',
    nameMl: 'ചാണ്ടി',
    title: 'Root / Founder',
    titleMl: 'സ്ഥാപകൻ',
    subtitle: 'Founder · Wife: Mariyam',
    subtitleMl: 'സ്ഥാപകൻ · ഭാര്യ മറിയം',
    isFounder: true,
    memberCount: 169,
}

const thazheBranch = {
    header: {
        id: 'thazhe',
        memberIdNum: 33,
        romanId: 'II 1',
        name: 'Chandy Chandy',
        nameMl: 'ചാണ്ടി ചാണ്ടി',
        title: 'Thazhe (Lower) Branch',
        titleMl: 'താഴെ ശാഖ',
        isBranchHead: true,
        memberCount: 76,
    } as OverviewBranchItem,
    subBranches: [
        {
            id: 'kulathammakkal',
            memberIdNum: 196,
            romanId: 'III 1',
            name: 'Chandy Chandy',
            nameMl: 'ചാണ്ടി ചാണ്ടി',
            title: 'Kulathammakkal',
            titleMl: 'കുളത്താമ്മാക്കൽ',
            parentBranchTitle: 'Thazhe Branch',
            parentMemberIdNum: 33,
            memberCount: 23,
        },
        {
            id: 'thazhe-sub',
            memberIdNum: 31,
            romanId: 'III 2',
            name: 'Chandy Kurian',
            nameMl: 'ചാണ്ടി കുര്യൻ',
            title: 'Thazhe Sub-branch',
            titleMl: 'താഴെ ഉപശാഖ',
            parentBranchTitle: 'Thazhe Branch',
            parentMemberIdNum: 33,
            memberCount: 50,
        },
    ] as OverviewBranchItem[]
}

const karottuBranch = {
    header: {
        id: 'karottu',
        memberIdNum: 188,
        romanId: 'II 2',
        name: 'Chandy Kurian',
        nameMl: 'ചാണ്ടി കുര്യൻ',
        title: 'Karottu (Upper) Branch',
        titleMl: 'കരോട്ട് ശാഖ',
        isBranchHead: true,
        memberCount: 61,
    } as OverviewBranchItem,
    subBranches: [
        {
            id: 'akkare',
            romanId: 'III 4',
            name: 'Kurian Abraham',
            nameMl: 'കുര്യൻ എബ്രഹാം',
            title: 'Akkare',
            titleMl: 'അക്കരെ',
            parentBranchTitle: 'Karottu Branch',
            parentMemberIdNum: 188,
        },
        {
            id: 'mulekkunnu',
            memberIdNum: 218,
            romanId: 'III 5',
            name: 'Kurian Kora',
            nameMl: 'കുര്യൻ കോര',
            title: 'Mulekkunnu',
            titleMl: 'മുളേക്കുന്ന്',
            parentBranchTitle: 'Karottu Branch',
            parentMemberIdNum: 188,
            memberCount: 23,
        },
        {
            id: 'kuttikkal',
            romanId: 'III 6',
            name: 'Kurian Anthrayose',
            nameMl: 'കുര്യൻ അന്ത്രയോസ്',
            title: 'Kuttikkal',
            titleMl: 'കുറ്റിക്കൽ',
            parentBranchTitle: 'Karottu Branch',
            parentMemberIdNum: 188,
        },
        {
            id: 'karottu-sub',
            memberIdNum: 221,
            romanId: 'III 7',
            name: 'Kurian Chacko',
            nameMl: 'കുര്യൻ ചാക്കോ',
            title: 'Karottu Sub-branch',
            titleMl: 'കരോട്ട് ഉപശാഖ',
            parentBranchTitle: 'Karottu Branch',
            parentMemberIdNum: 188,
            memberCount: 36,
        },
    ] as OverviewBranchItem[]
}

const tharavaduBranch = {
    header: {
        id: 'tharavadu',
        memberIdNum: 189,
        romanId: 'II 3',
        name: 'Chandy Kora',
        nameMl: 'ചാണ്ടി കോര',
        title: 'Tharavadu (Ancestral Home) Branch',
        titleMl: 'തറവാട് ശാഖ',
        isBranchHead: true,
        memberCount: 26,
    } as OverviewBranchItem,
    subBranches: [
        {
            id: 'tharavadu-line-1',
            romanId: 'III 9',
            name: 'Kora Chandy',
            nameMl: 'കോര ചാണ്ടി',
            title: 'Tharavadu Line 1',
            titleMl: 'തറവാട് വരി 1',
            parentBranchTitle: 'Tharavadu Branch',
            parentMemberIdNum: 189,
        },
        {
            id: 'tharavadu-line-2',
            memberIdNum: 224,
            romanId: 'III 12',
            name: 'Kora Kurian',
            nameMl: 'കോര കുര്യൻ',
            title: 'Tharavadu Line 2',
            titleMl: 'തറവാട് വരി 2',
            parentBranchTitle: 'Tharavadu Branch',
            parentMemberIdNum: 189,
            memberCount: 24,
        },
    ] as OverviewBranchItem[]
}

const allOverviewItems: OverviewBranchItem[] = [
    founderNode,
    thazheBranch.header,
    ...thazheBranch.subBranches,
    karottuBranch.header,
    ...karottuBranch.subBranches,
    tharavaduBranch.header,
    ...tharavaduBranch.subBranches,
]

// Accurate branch banners for visual lineage tree cards
const branchBanners: Record<number, { title: string; color: string; isMain: boolean }> = {
    35: { title: 'KOLLAMPARAMPIL FOUNDER', color: '#D97706', isMain: true },
    33: { title: 'KOLLAMPARAMPIL THAZHE BRANCH', color: '#0F766E', isMain: true },
    196: { title: 'KULATHAMMAKKAL SUB-BRANCH', color: '#1D4ED8', isMain: false },
    31: { title: 'THAZHE SUB-BRANCH', color: '#1D4ED8', isMain: false },
    188: { title: 'KAROTTU BRANCH', color: '#0F766E', isMain: true },
    218: { title: 'MULEKKUNNU SUB-BRANCH', color: '#1D4ED8', isMain: false },
    221: { title: 'KAROTTU SUB-BRANCH', color: '#1D4ED8', isMain: false },
    189: { title: 'THARAVADU BRANCH', color: '#0F766E', isMain: true },
    224: { title: 'THARAVADU LINE 2', color: '#1D4ED8', isMain: false },
}

const historicalMetadata: Record<number, { dates?: string; spouse?: string; status?: string }> = {
    35: { dates: 'Founder', spouse: 'Mariam' },
    33: { dates: 'b. 1838', spouse: 'Anna' },
    196: { dates: '1867–1944', spouse: 'Sosamma' },
    31: { spouse: 'Aleyamma' },
    188: { spouse: 'Achamma' },
    218: { spouse: 'Sosamma' },
    221: { spouse: 'Sosamma' },
    189: { spouse: 'Mariam' },
    224: { spouse: 'Aleyamma' },
    201: { dates: '1898–1972', spouse: 'Sosamma' },
    202: { status: '† young' },
    203: { spouse: 'Cherian Mathew' },
    204: { dates: '1904–1987', spouse: 'Mariamma' },
    205: { dates: '1907–1994', spouse: 'Rachel' },
    206: { spouse: 'Chacko' },
}

const selectedBranchJump = ref<string>('overview')
const visualSubMode = ref<'overview' | 'lineage'>('overview')
const activeSubtreeRootId = ref<number | null>(null)
const activeBranchInfo = ref<OverviewBranchItem | null>(null)
const selectedHistoricalNode = ref<OverviewBranchItem | null>(null)

// Nodes & Links references defined early for computed helpers
const nodes = ref<FamilyMember[]>([])
const links = computed(() => familyStore.edges)

// Descendant lookup helper for branch focusing
const getDescendantIds = (rootMemberId: number): Set<number> => {
    const parentLinks = (links.value || []).filter((l: any) => l && l.type === 'parent')
    const spouseLinks = (links.value || []).filter((l: any) => l && l.type === 'spouse')

    const childrenMap = new Map<number, number[]>()
    for (const l of parentLinks) {
        const s = Number(l.source)
        const t = Number(l.target)
        if (!childrenMap.has(s)) childrenMap.set(s, [])
        childrenMap.get(s)!.push(t)
    }

    const spouseMap = new Map<number, number[]>()
    for (const l of spouseLinks) {
        const s = Number(l.source)
        const t = Number(l.target)
        if (!spouseMap.has(s)) spouseMap.set(s, [])
        if (!spouseMap.has(t)) spouseMap.set(t, [])
        spouseMap.get(s)!.push(t)
        spouseMap.get(t)!.push(s)
    }

    const result = new Set<number>()
    const queue = [rootMemberId]

    while (queue.length > 0) {
        const curr = queue.shift()!
        if (result.has(curr)) continue
        result.add(curr)

        for (const sp of spouseMap.get(curr) || []) {
            if (!result.has(sp)) {
                result.add(sp)
                for (const spChild of childrenMap.get(sp) || []) {
                    if (!result.has(spChild)) {
                        queue.push(spChild)
                    }
                }
            }
        }

        for (const ch of childrenMap.get(curr) || []) {
            if (!result.has(ch)) {
                queue.push(ch)
            }
        }
    }

    return result
}

const dynamicMemberCounts = computed(() => {
    const counts = new Map<number, number>()
    if (!nodes.value.length) {
        counts.set(35, 169)
        counts.set(33, 76)
        counts.set(196, 23)
        counts.set(31, 50)
        counts.set(188, 61)
        counts.set(218, 23)
        counts.set(221, 36)
        counts.set(189, 26)
        counts.set(224, 24)
        return counts
    }
    for (const id of [35, 33, 188, 189, 196, 31, 218, 221, 224]) {
        const desc = getDescendantIds(id)
        counts.set(id, desc.size)
    }
    return counts
})

const activeBranchHeaderTitle = computed(() => {
    const isMl = locale.value === 'ml'
    if (activeBranchInfo.value) {
        const info = activeBranchInfo.value
        const title = isMl ? info.titleMl : info.title
        const name = isMl ? info.nameMl : info.name
        return `${title} • ${info.romanId} ${name}`
    }
    if (activeSubtreeRootId.value) {
        const found = allOverviewItems.find(x => x.memberIdNum === activeSubtreeRootId.value)
        if (found) {
            const title = isMl ? found.titleMl : found.title
            const name = isMl ? found.nameMl : found.name
            return `${title} • ${found.romanId} ${name}`
        }
        const member = nodes.value.find((n: any) => n.id === activeSubtreeRootId.value)
        if (member) return getDisplayName(member)
    }
    return t('familyTree.labels.branchLineage')
})

const activeBranchMembersCount = computed(() => {
    if (activeSubtreeRootId.value) {
        return getDescendantIds(activeSubtreeRootId.value).size
    }
    return nodes.value.length
})

const viewBranchFamily = (item: OverviewBranchItem) => {
    if (!item) return
    if (item.memberIdNum) {
        activeSubtreeRootId.value = item.memberIdNum
        activeBranchInfo.value = item
        visualSubMode.value = 'lineage'
        selectedBranchJump.value = String(item.memberIdNum)
        setTimeout(() => {
            initGraph()
        }, 50)
    } else {
        selectedHistoricalNode.value = item
    }
}

const viewBranchFamilyById = (memberId: number) => {
    const item = allOverviewItems.find(x => x.memberIdNum === memberId)
    if (item) {
        viewBranchFamily(item)
    } else {
        activeSubtreeRootId.value = memberId
        visualSubMode.value = 'lineage'
        selectedBranchJump.value = String(memberId)
        setTimeout(() => {
            initGraph()
        }, 50)
    }
}

const switchToOverview = () => {
    visualSubMode.value = 'overview'
    activeSubtreeRootId.value = null
    activeBranchInfo.value = null
    selectedBranchJump.value = 'overview'
    selectedHistoricalNode.value = null
    setTimeout(() => {
        drawOverviewGraph()
    }, 50)
}

const switchToLineage = () => {
    visualSubMode.value = 'lineage'
    if (!activeSubtreeRootId.value) {
        activeSubtreeRootId.value = 35
        activeBranchInfo.value = founderNode
        selectedBranchJump.value = '35'
    }
    setTimeout(() => {
        initGraph()
    }, 50)
}

const jumpToBranch = () => {
    const val = selectedBranchJump.value
    if (val === 'overview') {
        switchToOverview()
        return
    }
    if (val === 'all' || val === '35') {
        visualSubMode.value = 'lineage'
        activeSubtreeRootId.value = 35
        activeBranchInfo.value = founderNode
        initGraph()
        return
    }
    if (val === 'akkare' || val === 'kuttikkal' || val === 'tharavadu-line-1') {
        const item = allOverviewItems.find(x => x.id === val)
        if (item) selectedHistoricalNode.value = item
        return
    }
    const targetId = Number(val)
    if (Number.isFinite(targetId)) {
        const item = allOverviewItems.find(x => x.memberIdNum === targetId)
        if (item) {
            viewBranchFamily(item)
        } else {
            visualSubMode.value = 'lineage'
            activeSubtreeRootId.value = targetId
            initGraph()
        }
    }
}

const zoomIn = () => {
    if (globalSVG && globalZoom) {
        globalSVG.transition().duration(250).call(globalZoom.scaleBy as any, 1.25)
    }
}

const zoomOut = () => {
    if (globalSVG && globalZoom) {
        globalSVG.transition().duration(250).call(globalZoom.scaleBy as any, 0.8)
    }
}

const resetZoom = () => {
    if (visualSubMode.value === 'overview') {
        drawOverviewGraph()
        return
    }
    if (globalSVG && globalZoom && chartContainer.value) {
        const width = chartContainer.value.clientWidth
        const height = chartContainer.value.clientHeight
        const coords = Array.from(globalNodeCoords.values())
        if (!coords.length) return
        const minX = Math.min(...coords.map(c => c.x))
        const maxX = Math.max(...coords.map(c => c.x))
        const minY = Math.min(...coords.map(c => c.y))
        const maxY = Math.max(...coords.map(c => c.y))
        const contentW = Math.max(1, maxX - minX + 320)
        const contentH = Math.max(1, maxY - minY + 320)
        const scale = Math.min(1.15, Math.max(0.32, Math.min((width - 40) / contentW, (height - 40) / contentH)))
        const centerX = (minX + maxX) / 2
        const centerY = (minY + maxY) / 2
        const tx = width / 2 - centerX * scale
        const ty = Math.max(40, height / 2 - centerY * scale)
        globalSVG.transition().duration(400).call(
            globalZoom.transform as any,
            d3.zoomIdentity.translate(tx, ty).scale(scale)
        )
    }
}

// --- Overview Structure Drawing (Consistent Card Design & Diagram Hierarchy) ---
const drawOverviewGraph = () => {
    if (!svgRef.value || !chartContainer.value) return
    const width = chartContainer.value.clientWidth
    const height = chartContainer.value.clientHeight
    if (width === 0 || height === 0) {
        setTimeout(drawOverviewGraph, 200)
        return
    }

    const svg = d3.select(svgRef.value) as d3.Selection<SVGSVGElement, unknown, null, undefined>
    svg.attr('viewBox', `0 0 ${width} ${height}`)
    svg.selectAll('*').remove()

    const g = svg.append('g').attr('class', 'overview-tree-group')
    const mobileTwoFingerOnly = isMobileViewport()

    const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.25, 3.5])
        .filter((event: any) => {
            if (event.type === 'wheel') return Boolean(event.ctrlKey || event.metaKey)
            const isTouchEvent = String(event.type || '').startsWith('touch')
            if (!mobileTwoFingerOnly || !isTouchEvent) return true
            if (event.type === 'touchend' || event.type === 'touchcancel') return true
            return Number(event.touches?.length || 0) >= 2
        })
        .on('zoom', (event) => {
            g.attr('transform', event.transform)
        })
    svg.call(zoom)

    globalZoom = zoom
    globalSVG = svg

    const isMl = locale.value === 'ml'

    // Consistent Card Dimensions across the whole diagram
    const cardW = 260
    const branchH = 70
    const subCardH = 64
    const rootW = 276
    const rootH = 76

    // Columns - all 3 columns aligned with balanced spacing
    const centerX = width / 2
    const rootY = 60
    const colSpacing = 310
    const col1X = centerX - colSpacing // Thazhe
    const col2X = centerX              // Karottu
    const col3X = centerX + colSpacing // Tharavadu

    const busY = rootY + rootH / 2 + 30
    const branchY = busY + 44
    const subCardGap = 80
    const subCardStartY = branchY + branchH / 2 + 46

    // 1. Draw Links
    const linksGroup = g.append('g').attr('class', 'overview-links parent-links')

    // Root to Bus and branch drops
    const rootBottomY = rootY + rootH / 2
    let rootPath = `M ${centerX} ${rootBottomY} V ${busY}`
    rootPath += ` M ${col1X} ${busY} H ${col3X}`
    rootPath += ` M ${col1X} ${busY} V ${branchY - branchH / 2}`
    rootPath += ` M ${col2X} ${busY} V ${branchY - branchH / 2}`
    rootPath += ` M ${col3X} ${busY} V ${branchY - branchH / 2}`

    linksGroup.append('path')
        .attr('d', rootPath)
        .attr('fill', 'none')
        .attr('stroke', '#A08050')
        .attr('stroke-width', 2)
        .attr('stroke-linecap', 'round')
        .attr('stroke-linejoin', 'round')

    // Junction dots at bus joints
    const junctions = [
        { x: centerX, y: busY },
        { x: col1X, y: busY },
        { x: col3X, y: busY },
    ]
    for (const pt of junctions) {
        linksGroup.append('circle')
            .attr('cx', pt.x)
            .attr('cy', pt.y)
            .attr('r', 3.5)
            .attr('fill', '#A08050')
            .attr('stroke', '#FFFFFF')
            .attr('stroke-width', 1.5)
    }

    // Branch columns spines & horizontal arms
    const columnsData = [
        { colX: col1X, branch: thazheBranch, subCount: thazheBranch.subBranches.length },
        { colX: col2X, branch: karottuBranch, subCount: karottuBranch.subBranches.length },
        { colX: col3X, branch: tharavaduBranch, subCount: tharavaduBranch.subBranches.length },
    ]

    const spineOffset = cardW / 2 + 18 // exactly 18px to the left of the card column

    for (const col of columnsData) {
        const branchBottomY = branchY + branchH / 2
        const bracketY = branchBottomY + 18
        const spineX = col.colX - spineOffset
        const lastSubY = subCardStartY + (col.subCount - 1) * subCardGap

        let colPath = `M ${col.colX} ${branchBottomY} V ${bracketY} H ${spineX} V ${lastSubY}`
        for (let i = 0; i < col.subCount; i++) {
            const subY = subCardStartY + i * subCardGap
            const cardLeftEdge = col.colX - cardW / 2
            colPath += ` M ${spineX} ${subY} H ${cardLeftEdge}`
        }

        linksGroup.append('path')
            .attr('d', colPath)
            .attr('fill', 'none')
            .attr('stroke', '#CBD5E1')
            .attr('stroke-width', 1.8)
            .attr('stroke-linecap', 'round')
            .attr('stroke-linejoin', 'round')

        // Small junction dot at branch bracket turn
        linksGroup.append('circle')
            .attr('cx', spineX)
            .attr('cy', bracketY)
            .attr('r', 3)
            .attr('fill', '#94A3B8')
            .attr('stroke', '#FFFFFF')
            .attr('stroke-width', 1.2)
    }

    // 2. Nodes rendering (Unified Design System)
    const nodesGroup = g.append('g').attr('class', 'overview-nodes nodes')

    const renderCard = (container: any, item: any, x: number, y: number, w: number, h: number, type: 'root' | 'branch' | 'sub') => {
        const cardG = container.append('g')
            .attr('class', 'overview-card node')
            .attr('data-member-id', item.memberIdNum || item.id)
            .attr('transform', `translate(${x}, ${y})`)
            .style('cursor', 'pointer')
            .on('click', () => {
                viewBranchFamily(item)
            })

        const rx = 12

        // Unified Card Background
        const rect = cardG.append('rect')
            .attr('x', -w / 2)
            .attr('y', -h / 2)
            .attr('width', w)
            .attr('height', h)
            .attr('rx', rx)
            .attr('fill', '#FFFFFF')
            .attr('stroke', type === 'root' ? '#A08050' : type === 'branch' ? '#94A3B8' : '#E2E8F0')
            .attr('stroke-width', type === 'root' ? 2 : 1.2)
            .style('filter', 'drop-shadow(0 3px 12px rgba(15, 23, 42, 0.06))')
            .style('transition', 'all 0.2s cubic-bezier(0.4, 0, 0.2, 1)')

        cardG.on('mouseenter', function() {
            rect.attr('stroke', '#A08050')
                .attr('stroke-width', 2)
                .style('filter', 'drop-shadow(0 6px 20px rgba(160, 128, 80, 0.2))')
        }).on('mouseleave', function() {
            rect.attr('stroke', type === 'root' ? '#A08050' : type === 'branch' ? '#94A3B8' : '#E2E8F0')
                .attr('stroke-width', type === 'root' ? 2 : 1.2)
                .style('filter', 'drop-shadow(0 3px 12px rgba(15, 23, 42, 0.06))')
        })

        const count = item.memberIdNum ? (dynamicMemberCounts.value.get(item.memberIdNum) || item.memberCount) : null

        if (type === 'root') {
            // Founder Pill at top
            const tagW = 76
            const tagH = 16
            const tagY = -h / 2 + 11
            cardG.append('rect')
                .attr('x', -tagW / 2)
                .attr('y', tagY - tagH / 2)
                .attr('width', tagW)
                .attr('height', tagH)
                .attr('rx', tagH / 2)
                .attr('fill', '#FEF3C7')
                .attr('stroke', 'rgba(160, 128, 80, 0.4)')
                .attr('stroke-width', 0.8)

            cardG.append('text')
                .text(isMl ? 'സ്ഥാപകൻ' : 'FOUNDER')
                .attr('x', 0)
                .attr('y', tagY + 3)
                .attr('text-anchor', 'middle')
                .attr('fill', '#92400E')
                .attr('font-size', '8px')
                .attr('font-weight', '800')
                .attr('letter-spacing', '0.04em')

            // Line 1: Main Name
            const mainName = isMl ? `${item.romanId} ${item.nameMl}` : `${item.romanId} ${item.name}`
            cardG.append('text')
                .text(mainName)
                .attr('x', 0)
                .attr('y', 2)
                .attr('text-anchor', 'middle')
                .attr('fill', '#0F172A')
                .attr('font-size', '13.5px')
                .attr('font-weight', '800')

            // Line 2: Subtitle
            const subTitle = isMl ? 'ഭാര്യ: മറിയം' : 'Wife: Mariyam'
            cardG.append('text')
                .text(subTitle)
                .attr('x', 0)
                .attr('y', 18)
                .attr('text-anchor', 'middle')
                .attr('fill', '#64748B')
                .attr('font-size', '10.5px')
                .attr('font-weight', '500')

            // Line 3: Member Count Chip
            const countStr = count ? `${count} ${isMl ? 'അംഗങ്ങൾ' : 'members'}` : (isMl ? '169 അംഗങ്ങൾ' : '169 members')
            cardG.append('text')
                .text(`${countStr}  →`)
                .attr('x', 0)
                .attr('y', h / 2 - 6)
                .attr('text-anchor', 'middle')
                .attr('fill', '#A08050')
                .attr('font-size', '8.5px')
                .attr('font-weight', '700')

        } else if (type === 'branch') {
            // Line 1: Branch Title
            const title = isMl ? item.titleMl : item.title
            cardG.append('text')
                .text(title)
                .attr('x', 0)
                .attr('y', -h / 2 + 20)
                .attr('text-anchor', 'middle')
                .attr('fill', '#0F172A')
                .attr('font-size', '13px')
                .attr('font-weight', '800')

            // Line 2: Branch Head
            const personName = isMl ? `${item.romanId} ${item.nameMl}` : `${item.romanId} ${item.name}`
            cardG.append('text')
                .text(personName)
                .attr('x', 0)
                .attr('y', -h / 2 + 38)
                .attr('text-anchor', 'middle')
                .attr('fill', '#475569')
                .attr('font-size', '11.5px')
                .attr('font-weight', '600')

            // Line 3: Count badge
            const countStr = count ? `${count} ${isMl ? 'അംഗങ്ങൾ' : 'members'}` : ''
            if (countStr) {
                cardG.append('text')
                    .text(`${countStr}  →`)
                    .attr('x', 0)
                    .attr('y', h / 2 - 8)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#0284C7')
                    .attr('font-size', '8.5px')
                    .attr('font-weight', '700')
            }

        } else {
            // Sub-branch Card
            // Line 1: Sub-branch Title
            const title = isMl ? item.titleMl : item.title
            cardG.append('text')
                .text(title)
                .attr('x', 0)
                .attr('y', -h / 2 + 20)
                .attr('text-anchor', 'middle')
                .attr('fill', '#0F172A')
                .attr('font-size', '12.5px')
                .attr('font-weight', '800')

            // Line 2: Person Name
            const personName = isMl ? `${item.romanId} ${item.nameMl}` : `${item.romanId} ${item.name}`
            cardG.append('text')
                .text(personName)
                .attr('x', 0)
                .attr('y', -h / 2 + 37)
                .attr('text-anchor', 'middle')
                .attr('fill', '#475569')
                .attr('font-size', '11px')
                .attr('font-weight', '500')

            // Line 3: Badge chip
            if (count) {
                cardG.append('text')
                    .text(`${count} ${isMl ? 'അംഗങ്ങൾ' : 'members'}  →`)
                    .attr('x', 0)
                    .attr('y', h / 2 - 8)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#15803D')
                    .attr('font-size', '8px')
                    .attr('font-weight', '700')
            } else {
                cardG.append('text')
                    .text(isMl ? 'പാരമ്പര്യം' : 'Historical Line')
                    .attr('x', 0)
                    .attr('y', h / 2 - 8)
                    .attr('text-anchor', 'middle')
                    .attr('fill', '#94A3B8')
                    .attr('font-size', '8px')
                    .attr('font-weight', '600')
            }
        }
    }

    // Render Root
    renderCard(nodesGroup, founderNode, centerX, rootY, rootW, rootH, 'root')

    // Render 3 Branch Headers (Centered at col1X, col2X, col3X)
    renderCard(nodesGroup, thazheBranch.header, col1X, branchY, cardW, branchH, 'branch')
    renderCard(nodesGroup, karottuBranch.header, col2X, branchY, cardW, branchH, 'branch')
    renderCard(nodesGroup, tharavaduBranch.header, col3X, branchY, cardW, branchH, 'branch')

    // Render Sub-branches (Exact same colX centers for perfect vertical alignment!)
    for (let i = 0; i < thazheBranch.subBranches.length; i++) {
        const sub = thazheBranch.subBranches[i]
        const subY = subCardStartY + i * subCardGap
        renderCard(nodesGroup, sub, col1X, subY, cardW, subCardH, 'sub')
    }

    for (let i = 0; i < karottuBranch.subBranches.length; i++) {
        const sub = karottuBranch.subBranches[i]
        const subY = subCardStartY + i * subCardGap
        renderCard(nodesGroup, sub, col2X, subY, cardW, subCardH, 'sub')
    }

    for (let i = 0; i < tharavaduBranch.subBranches.length; i++) {
        const sub = tharavaduBranch.subBranches[i]
        const subY = subCardStartY + i * subCardGap
        renderCard(nodesGroup, sub, col3X, subY, cardW, subCardH, 'sub')
    }

    // Auto fit overview bounds into viewport
    const minX = col1X - cardW / 2 - 32
    const maxX = col3X + cardW / 2 + 15
    const minY = rootY - rootH / 2 - 15
    const maxY = subCardStartY + 3 * subCardGap + subCardH / 2 + 25

    const contentWidth = maxX - minX
    const contentHeight = maxY - minY
    const padding = isMobileViewport() ? 20 : 40

    const scale = Math.min(1.05, Math.max(0.35, Math.min((width - padding * 2) / contentWidth, (height - padding * 2) / contentHeight)))
    const tx = (width - contentWidth * scale) / 2 - minX * scale
    const ty = (height - contentHeight * scale) / 2 - minY * scale

    svg.call(zoom.transform as any, d3.zoomIdentity.translate(tx, ty).scale(scale))
}

const renderVisualTree = () => {
    if (viewMode.value !== 'visual') return
    if (visualSubMode.value === 'overview') {
        drawOverviewGraph()
    } else {
        initGraph()
    }
}

const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string
const { t, locale, te } = useI18n()

const familyStore = useFamilyStore()
const auth = useAuthStore()
const router = useRouter()

// --- Refs & UI State ---
const route = useRoute()

useHead(() => ({
    title: t('familyTree.meta.title'),
    meta: [
        { name: 'description', content: t('familyTree.meta.description') }
    ],
    link: [
        { rel: 'canonical', href: `${config.public.siteUrl || 'http://localhost:3000'}${route.path}` }
    ]
}))

const resolveInitialViewMode = (): 'visual' | 'grid' => {
    const requested = Array.isArray(route.query.view) ? route.query.view[0] : route.query.view
    if (requested === 'grid' || requested === 'visual') return requested
    return 'visual'
}

const resolveInitialEditMode = (): boolean => {
    const requested = Array.isArray(route.query.edit) ? route.query.edit[0] : route.query.edit
    return requested === '1' || requested === 'true'
}

const isMobileViewport = () => {
    if (typeof window === 'undefined') return false
    return window.matchMedia('(max-width: 767px)').matches
}

// View mode can be visual graph or directory grid
const viewMode = ref<'visual' | 'grid'>(resolveInitialViewMode())
const activeBranch = ref<string | null>(null)
const overviewData = computed(() => familyStore.overviewData)
const editMode = ref(resolveInitialEditMode())
const editorTab = ref<'profile' | 'details' | 'contact' | 'relationships' | 'settings'>('profile')
const isEditorSheetOpen = ref(true)
const isMobileView = ref(false)
const showMobileTreeHelp = ref(false)
const MOBILE_EDITOR_MIN_VH = 34
const MOBILE_EDITOR_MAX_VH = 88
const MOBILE_EDITOR_DEFAULT_VH = 58
const mobileEditorSheetVh = ref(MOBILE_EDITOR_DEFAULT_VH)
const isResizingEditorSheet = ref(false)
const loading = computed(() => familyStore.loading)
const svgRef = ref<SVGSVGElement | null>(null)
const chartContainer = ref<HTMLDivElement | null>(null)
const selectedMember = ref<FamilyMember | null>(null)

const clampMobileEditorHeight = (value: number) => {
    return Math.max(MOBILE_EDITOR_MIN_VH, Math.min(MOBILE_EDITOR_MAX_VH, value))
}

const mobileEditorSheetStyle = computed(() => {
    if (!isMobileViewport()) return {}
    const h = clampMobileEditorHeight(mobileEditorSheetVh.value)
    return {
        height: `${h}vh`,
        maxHeight: `${h}vh`,
        minHeight: `${MOBILE_EDITOR_MIN_VH}vh`,
    }
})

const adjustMobileZoom = (direction: 'in' | 'out') => {
    if (!svgRef.value || !chartContainer.value || !globalZoom || !globalSVG) return
    const current = d3.zoomTransform(svgRef.value)
    const factor = direction === 'in' ? 1.24 : 1 / 1.24
    const minScale = 0.35
    const maxScale = 4
    const nextScale = Math.max(minScale, Math.min(maxScale, current.k * factor))
    if (Math.abs(nextScale - current.k) < 0.0001) return

    const cx = chartContainer.value.clientWidth / 2
    const cy = chartContainer.value.clientHeight / 2
    const nextX = cx - ((cx - current.x) * nextScale) / current.k
    const nextY = cy - ((cy - current.y) * nextScale) / current.k
    const nextTransform = d3.zoomIdentity.translate(nextX, nextY).scale(nextScale)
    globalSVG.transition().duration(180).call(globalZoom.transform as any, nextTransform)
}

// Directory UI state
const searchQuery = ref('')
const filterLocation = ref('')
const filterOccupation = ref('')
const filterGender = ref('')
const filterBloodGroup = ref('')

const uniqueBloodGroups = computed(() => {
    const groups = new Set((nodes.value || []).map((n: any) => n.blood_group).filter(Boolean))
    return Array.from(groups).sort()
})
const searchResults = ref<FamilyMember[]>([])
const communityRoles = ref<Array<{ id: number; name: string; priority: number }>>([])

const addRelationType = ref<'PARENT' | 'SPOUSE' | 'SIBLING' | 'CHILD'>('CHILD')
const addRelativeMode = ref<'create' | 'link'>('create')
const addRelativeForm = ref({
    first_name: '',
    last_name: '',
    name_ml: '',
    family_name: '',
    nickname: '',
    member_id: '',
    gender: 'M' as 'M' | 'F' | 'O',
    age: '',
    date_of_birth: '',
    wedding_anniversary: '',
    blood_group: '',
    occupation: '',
    place_of_work: '',
    education: '',
    committee_role: '',
    phone_no: '',
    email_id: '',
    address: '',
    bio: '',
    church_parish: '',
    is_deceased: false,
    date_of_death: '',
})

const addRelativeAvatar = ref<File | null>(null)
const addRelativeAvatarPreview = ref<string | null>(null)
const addRelativeUseDob = ref(true)
const showCropperModal = ref(false)
const cropperTempImage = ref<string | null>(null)
const cropperRef = ref<any>(null)
const cropperTarget = ref<'addRelative' | 'quickEdit'>('addRelative')
const linkSearchQuery = ref('')
const linkSearchLoading = ref(false)
const linkSearchResults = ref<any[]>([])
const selectedLinkTarget = ref<any>(null)
const isAddingConnection = ref(false)
const selectedConnectionNodeId = ref<string | null>(null)
const selectedConnectionDir = ref<'top' | 'bottom' | 'left' | 'right' | null>(null)

// Hierarchical branches computed property
const hierarchicalBranches = computed(() => {
    if (!overviewData.value?.branches) return [];
    
    // Create a lookup for branch data and clean the name
    const cleanName = (name: string) => name.replace(/Kollamparampil\s*/i, '').trim();
    
    const branchMap = new Map(overviewData.value.branches.map(b => [b.name, { ...b, cleanName: cleanName(b.name) }]));
    
    const getBranch = (name: string) => {
        // Try exact match or match ignoring Kollamparampil
        let b = branchMap.get(name);
        if (!b) {
            const possibleNames = Array.from(branchMap.keys()).filter(k => k.includes(name));
            if (possibleNames.length > 0) b = branchMap.get(possibleNames[0]);
        }
        return b || { id: name, name: name, cleanName: cleanName(name), member_count: 0 };
    };

    const thazhe = getBranch('Thazhe branch');
    const karottu = getBranch('Karottu branch');
    const tharavadu = getBranch('Tharavadu branch');
    
    return [
        {
            ...thazhe,
            subBranches: [
                getBranch('Kulathamackal branch')
            ].filter(b => b.member_count !== undefined) // keep even if 0, but only if it's a real branch object
        },
        {
            ...karottu,
            subBranches: [
                getBranch('Akkare branch'),
                getBranch('Mulekkunnu branch'),
                getBranch('Kuttickal branch')
            ]
        },
        {
            ...tharavadu,
            subBranches: []
        }
    ];
});
const nameLookupLoadingAdd = ref(false)
const nameLookupLoadingQuick = ref(false)
let linkSearchDebounce: ReturnType<typeof setTimeout> | null = null
const editorLoading = ref(false)
const editorError = ref('')
const editorSuccess = ref('')

const contextOwnership = ref({
    is_independent: false,
    has_account: false,
    created_by_me: false,
    is_self: false,
})

const allowedActions = ref({
    can_manage: false,
    can_add_parent: false,
    can_add_spouse: false,
    can_add_sibling: false,
    can_add_child: false,
    can_remove: false,
})

const accessUsername = ref('')
const accessPassword = ref('')
const accessLoading = ref(false)
const inviteLoading = ref(false)
const inviteLink = ref('')

const quickEditOpen = ref(false)
const quickEditLoading = ref(false)
const quickEditError = ref('')
const quickEditSuccess = ref('')
const quickEditMemberId = ref<number | null>(null)
const quickEditAvatar = ref<File | null>(null)
const quickEditAvatarPreview = ref<string | null>(null)

const clearQuickEditAvatar = () => {
    quickEditAvatar.value = null
    quickEditAvatarPreview.value = null
}
const quickEditForm = ref({
    first_name: '',
    last_name: '',
    member_id: '',
    name_ml: '',
    family_name: '',
    nickname: '',
    gender: 'M' as 'M' | 'F' | 'O',
    age: '',
    date_of_birth: '',
    blood_group: '',
    occupation: '',
    place_of_work: '',
    education: '',
    committee_role: '',
    phone_no: '',
    email_id: '',
    wedding_anniversary: '',
    church_parish: '',
    address: '',
    bio: '',
    is_deceased: false,
    date_of_death: '',
    generation: null as number | null,
    branch: '',
})
const lastLinkedRelation = ref<null | { anchorId: number; targetId: number; relationType: 'PARENT' | 'SPOUSE' | 'SIBLING' | 'CHILD' }>(null)

const canShowGiveAccess = computed(() => {
    if (!selectedMember.value) return false
    return contextOwnership.value.created_by_me && !contextOwnership.value.has_account && !contextOwnership.value.is_independent
})

const canGoIndependent = computed(() => {
    if (!selectedMember.value) return false
    return contextOwnership.value.is_self && !contextOwnership.value.is_independent
})

const selectedMemberHasSpouse = computed(() => {
    const memberId = selectedMember.value?.id
    if (!memberId) return false
    return links.value.some((l: any) => l.type === 'spouse' && (l.source === memberId || l.target === memberId))
})

const selectedMemberHouseholdMembers = computed(() => {
    const member = selectedMember.value as any
    if (!member) return [] as any[]
    const byId = new Map((nodes.value || []).map((n: any) => [n.id, n]))
    const memberId = member.id
    const spouseLink = (links.value || []).find(
        (l: any) => l.type === 'spouse' && (l.source === memberId || l.target === memberId)
    )
    const spouseId = spouseLink ? (spouseLink.source === memberId ? spouseLink.target : spouseLink.source) : null
    const spouse = spouseId ? byId.get(spouseId) : null
    const household = [member, spouse].filter(Boolean)
    if (household.length < 2) return household
    const primary = member.gender === 'F' && spouse?.gender === 'M' ? spouse : member
    const partner = primary === member ? spouse : member
    return partner ? [primary, partner].filter(Boolean) : household
})

const householdTitle = computed(() => {
    if (!selectedMember.value) return ''
    const members = selectedMemberHouseholdMembers.value
    if (members.length > 1) {
        return members.map((person: any) => person.name).join(' & ')
    }
    return selectedMember.value.name
})

const canEditSelected = computed(() => {
    return editMode.value && selectedMember.value !== null && (allowedActions.value.can_manage || contextOwnership.value.is_self)
})

const selectHouseholdMember = (member: any) => {
    selectedMember.value = member
}

const selectedMemberParents = computed(() => {
    const memberId = selectedMember.value?.id
    if (!memberId) return [] as any[]
    const parentIds = links.value
        .filter((l: any) => l.type === 'parent' && l.target === memberId)
        .map((l: any) => l.source)
    return nodes.value.filter((n: any) => parentIds.includes(n.id))
})

const selectedMemberHasFather = computed(() => {
    return selectedMemberParents.value.some((p: any) => p.gender === 'M')
})

const selectedMemberHasMother = computed(() => {
    return selectedMemberParents.value.some((p: any) => p.gender === 'F')
})

const canAddSpouseNow = computed(() => {
    return allowedActions.value.can_add_spouse && !selectedMemberHasSpouse.value
})

const selectedTargetAlreadyLinked = computed(() => {
    if (addRelativeMode.value !== 'link' || !selectedMember.value || !selectedLinkTarget.value) return false
    const anchorId = selectedMember.value.id
    const targetId = selectedLinkTarget.value.id

    if (addRelationType.value === 'PARENT') {
        return links.value.some((l: any) => l.type === 'parent' && l.source === targetId && l.target === anchorId)
    }
    if (addRelationType.value === 'CHILD') {
        return links.value.some((l: any) => l.type === 'parent' && l.source === anchorId && l.target === targetId)
    }
    if (addRelationType.value === 'SPOUSE') {
        return links.value.some((l: any) => l.type === 'spouse' && ((l.source === anchorId && l.target === targetId) || (l.source === targetId && l.target === anchorId)))
    }
    if (addRelationType.value === 'SIBLING') {
        return links.value.some((l: any) => l.type === 'sibling' && ((l.source === anchorId && l.target === targetId) || (l.source === targetId && l.target === anchorId)))
    }
    return false
})

interface LevelTheme {
    accent: string       // Refined theme color
    darkAccent: string   // Darker legible tone for text & icons
    border: string       // Delicate border tone
    cardFill: string     // Clean background
    headerWash: string   // Subtle soft header tint
    badgeBg: string      // Pill background
    badgeText: string    // Pill text color
    avatarRing: string   // Avatar ring stroke
    avatarBg: string     // Avatar placeholder bg
    label: string        // Generation label
}

const levelPalette: LevelTheme[] = [
    { accent: '#D97706', darkAccent: '#78350F', border: '#D97706', cardFill: '#FFFBEB', headerWash: '#FEF3C7', badgeBg: '#FEF3C7', badgeText: '#92400E', avatarRing: '#D97706', avatarBg: '#FEF3C7', label: 'Generation I' },
    { accent: '#0D9488', darkAccent: '#115E59', border: '#0D9488', cardFill: '#F0FDFA', headerWash: '#CCFBF1', badgeBg: '#CCFBF1', badgeText: '#115E59', avatarRing: '#0D9488', avatarBg: '#CCFBF1', label: 'Generation II' },
    { accent: '#2563EB', darkAccent: '#1E40AF', border: '#2563EB', cardFill: '#EFF6FF', headerWash: '#DBEAFE', badgeBg: '#DBEAFE', badgeText: '#1E40AF', avatarRing: '#2563EB', avatarBg: '#DBEAFE', label: 'Generation III' },
    { accent: '#7C3AED', darkAccent: '#5B21B6', border: '#7C3AED', cardFill: '#F5F3FF', headerWash: '#EDE9FE', badgeBg: '#EDE9FE', badgeText: '#5B21B6', avatarRing: '#7C3AED', avatarBg: '#EDE9FE', label: 'Generation IV' },
    { accent: '#E11D48', darkAccent: '#9F1239', border: '#E11D48', cardFill: '#FFF1F2', headerWash: '#FFE4E6', badgeBg: '#FFE4E6', badgeText: '#9F1239', avatarRing: '#E11D48', avatarBg: '#FFE4E6', label: 'Generation V' },
    { accent: '#0891B2', darkAccent: '#155E75', border: '#0891B2', cardFill: '#ECFEFF', headerWash: '#CFFAFE', badgeBg: '#CFFAFE', badgeText: '#155E75', avatarRing: '#0891B2', avatarBg: '#CFFAFE', label: 'Generation VI' },
    { accent: '#EA580C', darkAccent: '#9A3412', border: '#EA580C', cardFill: '#FFF7ED', headerWash: '#FFEDD5', badgeBg: '#FFEDD5', badgeText: '#9A3412', avatarRing: '#EA580C', avatarBg: '#FFEDD5', label: 'Generation VII' },
    { accent: '#4F46E5', darkAccent: '#3730A3', border: '#4F46E5', cardFill: '#EEF2FF', headerWash: '#E0E7FF', badgeBg: '#E0E7FF', badgeText: '#3730A3', avatarRing: '#4F46E5', avatarBg: '#E0E7FF', label: 'Generation VIII' },
]

const getLevelTheme = (level: number): LevelTheme => {
    const idx = Math.max(0, Math.floor(level)) % levelPalette.length
    return levelPalette[idx]!
}

const branchPalette = levelPalette.map(t => t.accent)

const duplicateRelationWarning = computed(() => {
    if (selectedTargetAlreadyLinked.value) {
        return t('familyTree.editor.warnings.alreadyLinked')
    }

    if (addRelationType.value === 'SPOUSE' && selectedMemberHasSpouse.value) {
        return t('familyTree.editor.warnings.spouseExists')
    }

    if (addRelationType.value === 'PARENT') {
        if (selectedMemberParents.value.length >= 2) {
            return t('familyTree.editor.warnings.parentCap')
        }
        const pendingParentGender = addRelativeMode.value === 'link'
            ? (selectedLinkTarget.value?.gender || 'O')
            : addRelativeForm.value.gender
        if (pendingParentGender === 'M' && selectedMemberHasFather.value) {
            return t('familyTree.editor.warnings.fatherExists')
        }
        if (pendingParentGender === 'F' && selectedMemberHasMother.value) {
            return t('familyTree.editor.warnings.motherExists')
        }
    }

    return ''
})

const canSubmitAddRelative = computed(() => {
    if (!allowedActions.value.can_manage || !!duplicateRelationWarning.value) return false
    if (addRelativeMode.value === 'link') {
        return !!selectedLinkTarget.value
    }
    const fullName = `${addRelativeForm.value.first_name} ${addRelativeForm.value.last_name}`.trim()
    return fullName.length > 0
})

const resetAddRelativeForm = () => {
    addRelativeForm.value = {
        first_name: '',
        last_name: '',
        name_ml: '',
        family_name: '',
        nickname: '',
        member_id: '',
        gender: 'M',
        age: '',
        date_of_birth: '',
        wedding_anniversary: '',
        blood_group: '',
        occupation: '',
        place_of_work: '',
        education: '',
        committee_role: '',
        phone_no: '',
        email_id: '',
        address: '',
        bio: '',
        church_parish: '',
        is_deceased: false,
        date_of_death: '',
    }
    addRelativeUseDob.value = true
    addRelativeAvatar.value = null
    addRelativeAvatarPreview.value = null
}

const openCropper = (file: File, target: 'addRelative' | 'quickEdit') => {
    cropperTarget.value = target
    if (cropperTempImage.value) {
        URL.revokeObjectURL(cropperTempImage.value)
    }
    cropperTempImage.value = URL.createObjectURL(file)
    showCropperModal.value = true
}

const onAddRelativeAvatarChange = (event: Event) => {
    const target = event.target as HTMLInputElement
    const file = target.files?.[0] || null
    if (!file) return
    openCropper(file, 'addRelative')
    target.value = ''
}

const clearAddRelativeAvatar = () => {
    addRelativeAvatar.value = null
    addRelativeAvatarPreview.value = null
}

const cropImage = () => {
    const result = cropperRef.value?.getResult?.()
    if (!result?.canvas) return

    result.canvas.toBlob((blob: Blob | null) => {
        if (!blob) return
        const file = new File([blob], 'member_profile.jpg', { type: 'image/jpeg' })
        
        if (cropperTarget.value === 'addRelative') {
            addRelativeAvatar.value = file
            addRelativeAvatarPreview.value = URL.createObjectURL(file)
        } else {
            quickEditAvatar.value = file
            quickEditAvatarPreview.value = URL.createObjectURL(file)
        }
        
        showCropperModal.value = false
        if (cropperTempImage.value) {
            URL.revokeObjectURL(cropperTempImage.value)
            cropperTempImage.value = null
        }
    }, 'image/jpeg')
}

const cancelCrop = () => {
    showCropperModal.value = false
    if (cropperTempImage.value) {
        URL.revokeObjectURL(cropperTempImage.value)
        cropperTempImage.value = null
    }
}

const fetchMalayalamEquivalent = async (name: string): Promise<string | null> => {
    const query = String(name || '').trim()
    if (!query) return null

    try {
        const url = `https://inputtools.google.com/request?text=${encodeURIComponent(query)}&itc=ml-t-i0-und&num=1`
        const res = await fetch(url)
        if (!res.ok) return null
        const data = await res.json().catch(() => null) as any
        if (!Array.isArray(data) || data[0] !== 'SUCCESS') return null

        const suggestions = data?.[1]?.[0]?.[1]
        if (Array.isArray(suggestions) && suggestions.length > 0) {
            const translated = String(suggestions[0] || '').trim()
            return translated || null
        }
        return null
    } catch {
        return null
    }
}

const lookupMalayalamNameForAddRelative = async () => {
    const fullName = `${addRelativeForm.value.first_name} ${addRelativeForm.value.last_name}`.trim()
    if (!fullName) {
        editorError.value = 'Enter first and last name before Malayalam lookup.'
        return
    }

    nameLookupLoadingAdd.value = true
    const translated = await fetchMalayalamEquivalent(fullName)
    nameLookupLoadingAdd.value = false

    if (!translated) {
        editorError.value = 'Malayalam lookup failed. Try again.'
        return
    }

    addRelativeForm.value.name_ml = translated
    editorError.value = ''
}

const lookupMalayalamNameForQuickEdit = async () => {
    const fullName = `${quickEditForm.value.first_name} ${quickEditForm.value.last_name}`.trim()
    if (!fullName) {
        quickEditError.value = 'Enter first and last name before Malayalam lookup.'
        return
    }

    nameLookupLoadingQuick.value = true
    const translated = await fetchMalayalamEquivalent(fullName)
    nameLookupLoadingQuick.value = false

    if (!translated) {
        quickEditError.value = 'Malayalam lookup failed. Try again.'
        return
    }

    quickEditForm.value.name_ml = translated
    quickEditError.value = ''
}

// Computed data and member directory helpers

// When user presses Enter in search, auto-focus the first result
const performSearch = () => {
    if (viewMode.value !== 'visual') return
  if (searchResults.value.length > 0) {
    focusOnMember(searchResults.value[0])
  }
}

const sortedMembers = computed(() => {
   let list = [...nodes.value].sort((a,b) => a.name.localeCompare(b.name))
   
   if (searchQuery.value) {
       const q = searchQuery.value.toLowerCase()
       list = list.filter(m => m.name.toLowerCase().includes(q) || (m.nickname || '').toLowerCase().includes(q))
   }
   
   if (filterLocation.value) {
       const l = filterLocation.value.toLowerCase()
       list = list.filter(m => 
           (m.address || '').toLowerCase().includes(l) || 
           (m.location || '').toLowerCase().includes(l) || 
           (m.place_of_work || '').toLowerCase().includes(l) || 
           (m.church_parish || '').toLowerCase().includes(l)
       )
   }
   
   if (filterOccupation.value) {
       const o = filterOccupation.value.toLowerCase()
       list = list.filter(m => (m.occupation || '').toLowerCase().includes(o))
   }
   
   if (filterGender.value) {
       list = list.filter(m => m.gender === filterGender.value)
   }
   
   if (filterBloodGroup.value) {
       list = list.filter(m => m.blood_group === filterBloodGroup.value)
   }
   
   return list
})

const getPartnerForMember = (member: any) => {
    if (!links.value || !nodes.value || !member) return null
    const memberId = Number(member.id)
    const spouseLink = links.value.find(
        (l: any) => l.type === 'spouse' && (Number(l.source) === memberId || Number(l.target) === memberId)
    )
    if (!spouseLink) return null
    const spouseId = Number(spouseLink.source) === memberId ? Number(spouseLink.target) : Number(spouseLink.source)
    return nodes.value.find((n: any) => Number(n.id) === spouseId) || null
}

const selectedMemberForModal = computed(() => {
    if (!selectedMember.value) return null

    const member = selectedMember.value as any
    const byId = new Map((nodes.value || []).map((n: any) => [n.id, n]))
    const memberId = member.id
    const spouseLink = (links.value || []).find(
        (l: any) => l.type === 'spouse' && (l.source === memberId || l.target === memberId)
    )
    const spouseId = spouseLink ? (spouseLink.source === memberId ? spouseLink.target : spouseLink.source) : null
    const spouse = spouseId ? byId.get(spouseId) : null
    const householdMembers = selectedMemberHouseholdMembers.value
    const primaryMember = householdMembers[0] || member
    const partnerMember = householdMembers[1] || spouse || null

    const children = (links.value || [])
        .filter((l: any) => l.type === 'parent' && l.source === memberId)
        .map((l: any) => byId.get(l.target))
        .filter(Boolean)
        .map((c: any) => ({ name: c.name, age: c.age }))

    return {
        ...primaryMember,
        displayName: primaryMember?.name || member.name,
        member_id: primaryMember?.member_id || primaryMember?.id,
        spouse: partnerMember?.name || member.spouse || null,
        partner: partnerMember
            ? {
                ...partnerMember,
                spouse: primaryMember?.name || member.name,
            }
            : null,
        householdMembers: householdMembers.map((person: any) => ({
            ...person,
            spouse: person.id === primaryMember?.id ? partnerMember?.name || null : primaryMember?.name || null,
        })),
        children,
    }
})

const horizontalScale = ref(1)

const applyHorizontalCompression = (scale = 1, duration = 300) => {
    horizontalScale.value = scale
    if (!svgRef.value) return
    try {
        const el = svgRef.value as any
        el.style.transformOrigin = 'center top'
        el.style.transition = `transform ${duration}ms cubic-bezier(.2,.9,.2,1)`
        el.style.transform = scale && scale !== 1 ? `scaleX(${scale})` : ''
        window.setTimeout(() => {
            if (el) el.style.transition = ''
        }, duration + 20)
    } catch (e) {
    }
}

const toggleHorizontalCompression = () => {
    const next = horizontalScale.value === 1 ? 0.78 : 1
    applyHorizontalCompression(next, 340)
}

const resolveImage = (path: string | null) => {
    if (!path) return null
    if (path.startsWith('http') || path.startsWith('data:')) return path
    const cleanPath = path.startsWith('/') ? path : `/${path}`
    return `${apiBase}${cleanPath}`
}

const computeAgeFromDob = (dob?: string | null): number | null => {
    if (!dob) return null
    const birth = new Date(dob)
    if (Number.isNaN(birth.getTime())) return null

    const now = new Date()
    let years = now.getFullYear() - birth.getFullYear()
    const beforeBirthday =
        now.getMonth() < birth.getMonth() ||
        (now.getMonth() === birth.getMonth() && now.getDate() < birth.getDate())

    if (beforeBirthday) years -= 1
    return years >= 0 ? years : null
}

const getDisplayAge = (member: any): string => {
    if (member?.age !== null && member?.age !== undefined && member?.age !== '') {
        return String(member.age)
    }
    const derived = computeAgeFromDob(member?.date_of_birth)
    return derived !== null ? String(derived) : '?'
}

const getDisplayName = (member: any): string => {
    const baseName = String(member?.name || '').trim()
    const localizedNameKey = `memberNames.${member?.id}`

    if (locale.value === 'ml' && member?.name_ml) {
        const malayalamName = String(member.name_ml).trim()
        if (malayalamName) return malayalamName
    }

    if (locale.value !== 'en' && member?.nickname) {
        const nickname = String(member.nickname).trim()
        if (nickname) return nickname
    }

    if (member?.name_en && locale.value === 'en') {
        return String(member.name_en).trim()
    }

    if (member?.id && te(localizedNameKey)) {
        return String(t(localizedNameKey)).trim()
    }

    return baseName || t('familyTree.labels.member')
}

const resolveLoggedInMemberId = (): number | null => {
    const rawMember = (auth.user as any)?.member
    const direct = Number(rawMember)
    if (Number.isFinite(direct) && direct > 0) return direct

    if (rawMember && typeof rawMember === 'object') {
        const nested = Number((rawMember as any).id)
        if (Number.isFinite(nested) && nested > 0) return nested
    }

    return null
}

watch(searchQuery, (val) => {
    if (!val || viewMode.value !== 'visual') {
        searchResults.value = []
        return
    }
    const q = val.toLowerCase()
    searchResults.value = nodes.value.filter((n: any) => n.name.toLowerCase().includes(q)).slice(0, 5)
})

const focusOnMember = (targetMember: any, options?: { select?: boolean }) => {
    searchQuery.value = '' 
    searchResults.value = []
    const shouldSelect = options?.select ?? true
    
    if (!targetMember) return

    if (visualSubMode.value === 'overview') {
        visualSubMode.value = 'lineage'
        activeSubtreeRootId.value = null
        selectedBranchJump.value = '35'
        initGraph()
        setTimeout(() => {
            focusOnMemberInCanvas(targetMember, shouldSelect)
        }, 150)
        return
    }
    focusOnMemberInCanvas(targetMember, shouldSelect)
}

const focusOnMemberInCanvas = (targetMember: any, shouldSelect: boolean) => {
    if (!globalZoom || !globalSVG) return

    const coords = globalNodeCoords.get(targetMember.id)
    const found = Boolean(coords)
    const targetX = coords?.x || 0
    const targetY = coords?.y || 0

    if (found) {
        const container = chartContainer.value
        if (container) {
            const width = container.clientWidth
            const height = container.clientHeight
            const scale = isMobileViewport() ? 0.72 : 0.88
            globalSVG.transition().duration(1500).call(
                globalZoom.transform as any, 
                d3.zoomIdentity.translate(width/2 - targetX*scale, height/2 - targetY*scale).scale(scale)
            )
        }
        if (shouldSelect) {
            selectedMember.value = targetMember
        }
    }
}

const openMember = (m: FamilyMember) => { 
    selectedMember.value = m
}

const openQuickEditForSelected = () => {
    if (!selectedMember.value || !editMode.value || !canEditSelected.value) return
    const member = selectedMember.value as any
    const parts = String(member.name || '').trim().split(' ').filter(Boolean)
    quickEditMemberId.value = member.id
    quickEditForm.value = {
        first_name: parts[0] || '',
        last_name: parts.slice(1).join(' ') || '',
        member_id: member.member_id || '',
        name_ml: member.name_ml || '',
        family_name: member.family_name || '',
        nickname: member.nickname || '',
        gender: (member.gender || 'M') as 'M' | 'F' | 'O',
        age: member.age !== undefined && member.age !== null ? String(member.age) : '',
        date_of_birth: member.date_of_birth || '',
        blood_group: member.blood_group || '',
        occupation: member.occupation || '',
        place_of_work: member.place_of_work || '',
        education: member.education || '',
        committee_role: member.committee_role || '',
        phone_no: member.phone_no || '',
        email_id: member.email_id || '',
        wedding_anniversary: member.wedding_anniversary || '',
        church_parish: member.church_parish || '',
        address: member.location || member.address || '',
        bio: member.bio || '',
        is_deceased: Boolean(member.is_deceased),
        date_of_death: member.date_of_death || '',
        generation: member.generation !== undefined ? member.generation : null,
        branch: member.branch || '',
    }
    quickEditError.value = ''
    quickEditSuccess.value = ''
    quickEditAvatar.value = null
    quickEditAvatarPreview.value = member.profile_pic || null
    // quickEditOpen.value = true
}

const onQuickEditAvatarChange = (event: Event) => {
    const target = event.target as HTMLInputElement
    const file = target.files?.[0] || null
    if (!file) return
    openCropper(file, 'quickEdit')
    target.value = ''
}

const saveQuickEditMember = async () => {
    if (!quickEditMemberId.value || !selectedMember.value) return
    quickEditLoading.value = true
    quickEditError.value = ''
    quickEditSuccess.value = ''

    try {
        const csrfHeaders = await withCsrfHeaders()
        const headers = {
            Accept: 'application/json',
            ...(csrfHeaders as Record<string, string> || {}),
        }
        const fd = new FormData()
        const fullName = `${quickEditForm.value.first_name} ${quickEditForm.value.last_name}`.trim()

        fd.append('first_name', quickEditForm.value.first_name || '')
        fd.append('last_name', quickEditForm.value.last_name || '')
        fd.append('member_id', quickEditForm.value.member_id || '')
        fd.append('name_ml', quickEditForm.value.name_ml || '')
        fd.append('family_name', quickEditForm.value.family_name || '')
        fd.append('nickname', quickEditForm.value.nickname || '')
        if (!quickEditForm.value.first_name && !quickEditForm.value.last_name && fullName) fd.append('name', fullName)
        fd.append('nickname', quickEditForm.value.nickname || '')
        fd.append('gender', quickEditForm.value.gender || 'O')
        fd.append('date_of_birth', quickEditForm.value.date_of_birth || '')
        if (quickEditForm.value.age) {
            fd.append('age', quickEditForm.value.age)
        }
        fd.append('blood_group', quickEditForm.value.blood_group || '')
        fd.append('occupation', quickEditForm.value.occupation || '')
        fd.append('place_of_work', quickEditForm.value.place_of_work || '')
        fd.append('education', quickEditForm.value.education || '')
        fd.append('committee_role', quickEditForm.value.committee_role || '')
        fd.append('phone_no', quickEditForm.value.phone_no || '')
        fd.append('email_id', quickEditForm.value.email_id || '')
        fd.append('wedding_anniversary', quickEditForm.value.wedding_anniversary || '')
        
        fd.append('church_parish', quickEditForm.value.church_parish || '')
        fd.append('address', quickEditForm.value.address || '')
        fd.append('bio', quickEditForm.value.bio || '')
        fd.append('is_deceased', quickEditForm.value.is_deceased ? 'true' : 'false')
        fd.append('date_of_death', quickEditForm.value.is_deceased ? (quickEditForm.value.date_of_death || '') : '')
        if (quickEditForm.value.generation !== null) {
            fd.append('generation', String(quickEditForm.value.generation))
        } else {
            fd.append('generation', '')
        }
        fd.append('branch', quickEditForm.value.branch || '')
        if (quickEditAvatar.value) fd.append('profile_pic', quickEditAvatar.value)

        let endpoint = `${apiBase}/api/families/managed/${quickEditMemberId.value}/`
        let method: 'PUT' | 'POST' = 'PUT'

        if (contextOwnership.value.is_self) {
            endpoint = `${apiBase}/api/families/profile/`
            method = 'POST'
        }

        const res = await fetch(endpoint, {
            method,
            headers,
            credentials: 'include',
            body: fd,
        })

        const payload = await res.json().catch(() => ({}))
        if (!res.ok) {
            quickEditError.value = friendlyErrorMessage(payload, res.status)
            return
        }

        quickEditSuccess.value = 'Member details updated.'
        await familyStore.fetchFamily(activeBranch.value || '')
        await auth.fetchProfile()
        const refreshed = nodes.value.find((n: any) => n.id === quickEditMemberId.value)
        if (refreshed) {
            selectedMember.value = refreshed as FamilyMember
            await loadMemberContext(refreshed.id)
        }
        setTimeout(() => {
            initGraph()
            if (refreshed) {
                focusOnMember(refreshed, { select: true })
            }
        }, 120)
    } catch (err) {
        quickEditError.value = friendlyErrorMessage(err)
        console.error(err)
    } finally {
        quickEditLoading.value = false
    }
}

const setRelationType = (value: 'PARENT' | 'SPOUSE' | 'SIBLING' | 'CHILD') => {
    if (value === 'SPOUSE' && selectedMemberHasSpouse.value) {
        editorError.value = t('familyTree.editor.errors.spouseAlreadyLinked')
        return
    }
    addRelationType.value = value
    resetAddRelativeForm()
    if (selectedMember.value) {
        quickEditMemberId.value = selectedMember.value.id
        quickEditOpen.value = true
    }
}

function getCookie(name: string) {
    if (typeof document === 'undefined') return null
    const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
    return matches ? matches[2] : null
}

const withCsrfHeaders = async (): Promise<HeadersInit | undefined> => {
    const csrfRes = await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
    const csrfData = await csrfRes.json().catch(() => ({}))
    const csrftoken = getCookie('csrftoken') || csrfData.csrfToken
    return csrftoken ? { 'X-CSRFToken': String(csrftoken) } : undefined
}

const fetchCommunityRoles = async () => {
    try {
        const res = await fetch(`${apiBase}/api/profiles/community-roles/`, { credentials: 'include' })
        if (!res.ok) return
        const data = await res.json().catch(() => []) as any[]
        communityRoles.value = Array.isArray(data)
            ? data
                .filter((item) => item && item.name)
                .map((item) => ({
                    id: Number(item.id),
                    name: String(item.name),
                    priority: Number(item.priority || 100),
                }))
            : []
    } catch (err) {
        console.error('Failed to load community roles', err)
        communityRoles.value = []
    }
}

const loadMemberContext = async (memberId: number) => {
    if (!auth.user) return
    try {
        const res = await fetch(`${apiBase}/api/families/member-context/${memberId}/`, { credentials: 'include' })
        if (!res.ok) {
            if (res.status === 401 || res.status === 403) {
                contextOwnership.value = {
                    is_independent: false,
                    has_account: false,
                    created_by_me: false,
                    is_self: false,
                }
                allowedActions.value = {
                    can_manage: false,
                    can_add_parent: false,
                    can_add_spouse: false,
                    can_add_sibling: false,
                    can_add_child: false,
                    can_remove: false,
                }
            }
            return
        }
        const data = await res.json()
        contextOwnership.value = data.ownership_status || contextOwnership.value
        const allowed = data.allowed_actions || allowedActions.value
        if (data.ownership_status?.is_self) {
            allowed.can_manage = true
            allowed.can_add_parent = true
            allowed.can_add_spouse = true
            allowed.can_add_sibling = true
            allowed.can_add_child = true
            allowed.can_remove = true
        }
        allowedActions.value = allowed
    } catch (err) {
        console.error('Failed to load member context', err)
    }
}

const resetLinkTarget = () => {
    selectedLinkTarget.value = null
    linkSearchResults.value = []
}

const selectLinkTarget = (member: any) => {
    selectedLinkTarget.value = member
    linkSearchQuery.value = member.name || ''
    linkSearchResults.value = []
}

const searchExistingMembers = async () => {
    const query = linkSearchQuery.value.trim()
    if (addRelativeMode.value !== 'link' || query.length < 2) {
        linkSearchResults.value = []
        return
    }

    linkSearchLoading.value = true
    try {
        const anchorId = selectedMember.value?.id
        const params = new URLSearchParams({ q: query })
        if (anchorId) params.set('exclude_id', String(anchorId))

        const res = await fetch(`${apiBase}/api/families/member-search/?${params.toString()}`, {
            credentials: 'include',
        })
        if (!res.ok) {
            linkSearchResults.value = []
            return
        }

        const payload = await res.json().catch(() => ({ results: [] }))
        const results = Array.isArray(payload.results) ? payload.results : []
        linkSearchResults.value = results
    } catch (err) {
        linkSearchResults.value = []
        console.error('Failed to search existing members', err)
    } finally {
        linkSearchLoading.value = false
    }
}

const onLinkSearchInput = () => {
    selectedLinkTarget.value = null
    if (linkSearchDebounce) {
        clearTimeout(linkSearchDebounce)
    }
    linkSearchDebounce = setTimeout(() => {
        searchExistingMembers()
    }, 250)
}

const addRelativeFromPanel = async () => {
    if (!selectedMember.value) return
    const anchorMemberId = selectedMember.value.id
    if (!allowedActions.value.can_manage) {
        editorError.value = t('familyTree.editor.errors.managePermission')
        return
    }
    const fullName = `${addRelativeForm.value.first_name} ${addRelativeForm.value.last_name}`.trim()
    if (addRelativeMode.value === 'create' && !fullName) {
        editorError.value = t('familyTree.editor.errors.relativeNameRequired')
        return
    }
    if (addRelativeMode.value === 'link' && !selectedLinkTarget.value) {
        editorError.value = t('familyTree.editor.errors.selectExistingMember')
        return
    }
    if (duplicateRelationWarning.value) {
        editorError.value = duplicateRelationWarning.value
        return
    }

    editorLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''
    const linkedTarget = selectedLinkTarget.value

    try {
        const csrfHeaders = await withCsrfHeaders()
        const endpoint = addRelativeMode.value === 'link'
            ? `${apiBase}/api/families/tree-edit/${selectedMember.value.id}/link-existing/`
            : `${apiBase}/api/families/tree-edit/${selectedMember.value.id}/add-relative/`
        let res: Response
        if (addRelativeMode.value === 'link' && selectedLinkTarget.value) {
            const body = {
                target_member_id: selectedLinkTarget.value.id,
                relation_type: addRelationType.value,
                anniversary_date: null,
            }
            const headers = {
                'Content-Type': 'application/json',
                ...(csrfHeaders ? (csrfHeaders as Record<string, string>) : {}),
            }
            res = await fetch(endpoint, {
                method: 'POST',
                headers,
                credentials: 'include',
                body: JSON.stringify(body),
            })
        } else {
            const formData = new FormData()
            formData.append('relation_type', addRelationType.value)
            formData.append('name', fullName)
            formData.append('first_name', addRelativeForm.value.first_name)
            formData.append('last_name', addRelativeForm.value.last_name)
            if (addRelativeForm.value.name_ml) formData.append('name_ml', addRelativeForm.value.name_ml)
            if (addRelativeForm.value.family_name) formData.append('family_name', addRelativeForm.value.family_name)
            if (addRelativeForm.value.nickname) formData.append('nickname', addRelativeForm.value.nickname)
            if (addRelativeForm.value.member_id) formData.append('member_id', addRelativeForm.value.member_id)
            formData.append('gender', addRelativeForm.value.gender)
            if (addRelativeUseDob.value && addRelativeForm.value.date_of_birth) formData.append('date_of_birth', addRelativeForm.value.date_of_birth)
            if (!addRelativeUseDob.value && addRelativeForm.value.age) formData.append('age', addRelativeForm.value.age)
            if (addRelativeForm.value.blood_group) formData.append('blood_group', addRelativeForm.value.blood_group)
            if (addRelativeForm.value.occupation) formData.append('occupation', addRelativeForm.value.occupation)
            if (addRelativeForm.value.place_of_work) formData.append('place_of_work', addRelativeForm.value.place_of_work)
            if (addRelativeForm.value.education) formData.append('education', addRelativeForm.value.education)
            if (addRelativeForm.value.wedding_anniversary) formData.append('wedding_anniversary', addRelativeForm.value.wedding_anniversary)
            if (addRelativeForm.value.committee_role) formData.append('committee_role', addRelativeForm.value.committee_role)
            if (addRelativeForm.value.phone_no) formData.append('phone_no', addRelativeForm.value.phone_no)
            if (addRelativeForm.value.email_id) formData.append('email_id', addRelativeForm.value.email_id)
            if (addRelativeForm.value.address) formData.append('address', addRelativeForm.value.address)
            if (addRelativeForm.value.bio) formData.append('bio', addRelativeForm.value.bio)
            if (addRelativeForm.value.church_parish) formData.append('church_parish', addRelativeForm.value.church_parish)
            formData.append('is_deceased', addRelativeForm.value.is_deceased ? 'true' : 'false')
            if (addRelativeForm.value.is_deceased && addRelativeForm.value.date_of_death) formData.append('date_of_death', addRelativeForm.value.date_of_death)
            if (addRelativeAvatar.value) formData.append('profile_pic', addRelativeAvatar.value)

            res = await fetch(endpoint, {
                method: 'POST',
                headers: {
                    ...csrfHeaders,
                },
                credentials: 'include',
                body: formData,
            })
        }

        const payload = await res.json().catch(() => ({}))
        if (!res.ok) {
            editorError.value = payload.error || t('familyTree.editor.errors.addRelativeFailed')
            return
        }

        if (addRelativeMode.value === 'create') {
            resetAddRelativeForm()
            lastLinkedRelation.value = null
        } else {
            linkSearchQuery.value = ''
            resetLinkTarget()
            if (linkedTarget) {
                lastLinkedRelation.value = {
                    anchorId: anchorMemberId,
                    targetId: linkedTarget.id,
                    relationType: addRelationType.value,
                }
            }
        }
        editorSuccess.value = addRelativeMode.value === 'create'
            ? t('familyTree.editor.success.relativeAdded')
            : t('familyTree.editor.success.existingLinked')
        await familyStore.fetchFamily(activeBranch.value || '')
        await auth.fetchProfile()
        const anchor = nodes.value.find((n: any) => n.id === anchorMemberId)
        if (anchor) {
            selectedMember.value = anchor as FamilyMember
            await loadMemberContext(anchorMemberId)
        }
        setTimeout(() => {
            initGraph()
            if (anchor) {
                focusOnMember(anchor, { select: true })
            }
        }, 120)
    } catch (err) {
        editorError.value = t('familyTree.editor.errors.addRelativeFailed')
        console.error(err)
    } finally {
        editorLoading.value = false
    }
}

const undoLastLinkedRelation = async () => {
    if (!lastLinkedRelation.value) return
    if (!selectedMember.value || selectedMember.value.id !== lastLinkedRelation.value.anchorId) {
        editorError.value = 'Select the same member to undo the last link.'
        return
    }

    editorLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''

    try {
        const csrfHeaders = await withCsrfHeaders()
        const headers = {
            'Content-Type': 'application/json',
            ...(csrfHeaders ? (csrfHeaders as Record<string, string>) : {}),
        }
        const res = await fetch(`${apiBase}/api/families/tree-edit/${lastLinkedRelation.value.anchorId}/unlink-existing/`, {
            method: 'POST',
            headers,
            credentials: 'include',
            body: JSON.stringify({
                target_member_id: lastLinkedRelation.value.targetId,
                relation_type: lastLinkedRelation.value.relationType,
            }),
        })

        const payload = await res.json().catch(() => ({}))
        if (!res.ok) {
            editorError.value = payload.error || 'Unable to undo the last link.'
            return
        }

        lastLinkedRelation.value = null
        editorSuccess.value = 'Last link undone.'
        await familyStore.fetchFamily(activeBranch.value || '')
        await auth.fetchProfile()
        const refreshed = nodes.value.find((n: any) => n.id === selectedMember.value?.id)
        if (refreshed) {
            selectedMember.value = refreshed as FamilyMember
            await loadMemberContext(refreshed.id)
        }
        setTimeout(() => {
            initGraph()
            if (refreshed) {
                focusOnMember(refreshed, { select: true })
            }
        }, 120)
    } catch (err) {
        editorError.value = 'Unable to undo the last link.'
        console.error(err)
    } finally {
        editorLoading.value = false
    }
}

const generateInviteLink = async () => {
    inviteLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''
    try {
        const csrfHeaders = await withCsrfHeaders()
        const headers = csrfHeaders ? (csrfHeaders as Record<string, string>) : undefined
        const res = await fetch(`${apiBase}/api/auth/generate-invite-token/`, {
            method: 'POST',
            headers,
            credentials: 'include',
        })
        const payload = await res.json().catch(() => ({}))
        if (!res.ok) {
            editorError.value = payload.error || t('login.errors.inviteFailed')
            return
        }

        inviteLink.value = `${window.location.origin}/?token=${payload.token}`
        editorSuccess.value = t('login.alerts.inviteCopied')
    } catch (err) {
        editorError.value = t('login.errors.inviteError')
        console.error(err)
    } finally {
        inviteLoading.value = false
    }
}

const copyInviteLink = async () => {
    if (!inviteLink.value) return
    try {
        await navigator.clipboard.writeText(inviteLink.value)
        editorSuccess.value = t('login.alerts.inviteCopied')
    } catch (err) {
        editorError.value = t('login.errors.inviteError')
    }
}

const removeSelectedMember = async () => {
    if (!selectedMember.value) return
    if (!allowedActions.value.can_remove) {
        editorError.value = t('familyTree.editor.errors.removePermission')
        return
    }
    if (!confirm(t('familyTree.editor.confirmRemove', { name: selectedMember.value.name }))) return

    editorLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''

    try {
        const csrfHeaders = await withCsrfHeaders()
        const headers = csrfHeaders ? (csrfHeaders as Record<string, string>) : undefined
        const res = await fetch(`${apiBase}/api/families/tree-edit/${selectedMember.value.id}/remove/`, {
            method: 'DELETE',
            headers,
            credentials: 'include',
        })

        if (!res.ok) {
            const err = await res.json().catch(() => ({}))
            editorError.value = err.error || t('familyTree.editor.errors.removeFailed')
            return
        }

        editorSuccess.value = t('familyTree.editor.success.memberRemoved')
        selectedMember.value = null
        await familyStore.fetchFamily(activeBranch.value || '')
        await auth.fetchProfile()
        setTimeout(initGraph, 120)
    } catch (err) {
        editorError.value = t('familyTree.editor.errors.removeFailed')
        console.error(err)
    } finally {
        editorLoading.value = false
    }
}

const giveAccessFromPanel = async () => {
    if (!selectedMember.value) return
    if (!accessUsername.value.trim() || !accessPassword.value.trim()) {
        editorError.value = t('onboarding.giveAccess.errors.requiredFields')
        return
    }

    accessLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''
    const result = await auth.giveAccess(selectedMember.value.id, accessUsername.value.trim(), accessPassword.value.trim())
    accessLoading.value = false

    if (!result.ok) {
        editorError.value = result.error || t('familyTree.editor.errors.giveAccessFailed')
        return
    }

    editorSuccess.value = result.data?.message || 'Access granted.'
    accessUsername.value = ''
    accessPassword.value = ''
    await loadMemberContext(selectedMember.value.id)
    await familyStore.fetchFamily(activeBranch.value || '')
}

const goIndependentFromPanel = async () => {
    accessLoading.value = true
    editorError.value = ''
    editorSuccess.value = ''
    const result = await auth.goIndependent()
    accessLoading.value = false

    if (!result.ok) {
        editorError.value = result.error || t('familyTree.editor.errors.independenceFailed')
        return
    }

    editorSuccess.value = result.data?.message || t('familyTree.editor.success.profileIndependent')
    if (selectedMember.value) {
        await loadMemberContext(selectedMember.value.id)
    }
}

const openEditorSheet = () => {
    if (isMobileViewport()) {
        mobileEditorSheetVh.value = clampMobileEditorHeight(mobileEditorSheetVh.value || MOBILE_EDITOR_DEFAULT_VH)
    }
    isEditorSheetOpen.value = true
}

const closeEditorSheet = () => {
    isEditorSheetOpen.value = false
}

let editorResizeStartY = 0
let editorResizeStartHeight = MOBILE_EDITOR_DEFAULT_VH

const onEditorResizeMove = (event: PointerEvent) => {
    if (!isResizingEditorSheet.value || !isMobileViewport()) return
    event.preventDefault()
    const deltaVh = ((editorResizeStartY - event.clientY) / Math.max(1, window.innerHeight)) * 100
    mobileEditorSheetVh.value = clampMobileEditorHeight(editorResizeStartHeight + deltaVh)
}

const stopEditorResize = () => {
    isResizingEditorSheet.value = false
    window.removeEventListener('pointermove', onEditorResizeMove)
    window.removeEventListener('pointerup', stopEditorResize)
    window.removeEventListener('pointercancel', stopEditorResize)
}

const startEditorResize = (event: PointerEvent) => {
    if (!isMobileViewport()) return
    isResizingEditorSheet.value = true
    editorResizeStartY = event.clientY
    editorResizeStartHeight = mobileEditorSheetVh.value
    window.addEventListener('pointermove', onEditorResizeMove, { passive: false })
    window.addEventListener('pointerup', stopEditorResize)
    window.addEventListener('pointercancel', stopEditorResize)
}

const handleResize = () => {
    isMobileView.value = isMobileViewport()
    if (!isMobileView.value) {
        showMobileTreeHelp.value = false
    }
    mobileEditorSheetVh.value = clampMobileEditorHeight(mobileEditorSheetVh.value)
    if (viewMode.value === 'visual' && visualSubMode.value === 'overview') {
        drawOverviewGraph()
    }
}

const toggleEditMode = () => {
    const next = !editMode.value
    editMode.value = next
    if (next) {
        openEditorSheet()
    }

    const query: Record<string, string> = {}
    if (viewMode.value) query.view = viewMode.value
    if (next) {
        query.edit = '1'
        if (selectedMember.value?.id) query.focus = String(selectedMember.value.id)
    }

    router.replace({ path: '/familytree', query })
}

const focusFromQuery = () => {
    const qFocus = Array.isArray(route.query.focus) ? route.query.focus[0] : route.query.focus
    const focusId = qFocus ? parseInt(qFocus) : NaN

    if (!focusId || Number.isNaN(focusId)) {
        const meId = resolveLoggedInMemberId()
        if (!meId) return
        const me = nodes.value.find((n: any) => n.id === meId)
        if (!me) return
        setTimeout(() => focusOnMember(me, { select: false }), 120)
        return
    }

    const member = nodes.value.find((n: any) => n.id === focusId)
    if (!member) return
    selectedMember.value = member as FamilyMember
    setTimeout(() => focusOnMember(member), 120)
}

const selectBranch = async (branchId: string) => {
    activeBranch.value = branchId
    await familyStore.fetchFamily(branchId)
    nodes.value = [...familyStore.flatList()]
    setTimeout(() => {
        if (viewMode.value === 'visual') {
            initGraph()
        }
    }, 50)
}

const backToOverview = () => {
    activeBranch.value = null
    if (svgRef.value) {
        d3.select(svgRef.value).selectAll('*').remove()
    }
    familyStore.fetchOverview()
}

// --- D3 Tree Rendering Pipeline ---
const initGraph = () => {
    if (!nodes.value.length || !svgRef.value || !chartContainer.value) return

    const width = chartContainer.value.clientWidth
    const height = chartContainer.value.clientHeight
    if (width === 0 || height === 0) {
        setTimeout(initGraph, 250)
        return
    }

    const svg = d3.select(svgRef.value) as d3.Selection<SVGSVGElement, unknown, null, undefined>
    svg.attr('viewBox', `0 0 ${width} ${height}`)
    svg.selectAll('*').remove()

    const g = svg.append('g')
    const mobileTwoFingerOnly = isMobileViewport()
    const zoom = d3.zoom<SVGSVGElement, unknown>()
        .scaleExtent([0.32, 4])
        .wheelDelta((event: any) => {
            if (!(event.ctrlKey || event.metaKey)) return 0
            const factor = event.deltaMode === 1 ? 0.04 : 0.002
            return Math.max(-0.22, Math.min(0.22, -event.deltaY * factor))
        })
        .filter((event: any) => {
            if (event.type === 'wheel') return Boolean(event.ctrlKey || event.metaKey)
            const isTouchEvent = String(event.type || '').startsWith('touch')
            if (!mobileTwoFingerOnly || !isTouchEvent) return true
            if (event.type === 'touchend' || event.type === 'touchcancel') return true
            return Number(event.touches?.length || 0) >= 2
        })
        .on('zoom', (event) => {
            g.attr('transform', event.transform)
        })
    svg.call(zoom)

    globalZoom = zoom
    globalSVG = svg

    const isCompactMobileCard = isMobileViewport()
    const cardWidth = isCompactMobileCard ? 130 : 152
    const cardHeight = isCompactMobileCard ? 62 : 74
    const siblingGap = isCompactMobileCard ? 18 : 32
    const levelGap = isCompactMobileCard ? 165 : 185
    const topOffset = isCompactMobileCard ? 85 : 110
    const spouseGap = 0
    const cardHalfWidth = cardWidth / 2
    const spouseCenterOffset = 0

    const targetNodeIds = activeSubtreeRootId.value
        ? getDescendantIds(activeSubtreeRootId.value)
        : null

    const visibleNodeMap = new Map<number, any>()
    const duplicateNodeIds = new Set<number>()
    for (const node of nodes.value) {
        const id = Number((node as any)?.id)
        if (!Number.isFinite(id)) continue
        if (targetNodeIds && !targetNodeIds.has(id)) continue
        if (visibleNodeMap.has(id)) {
            duplicateNodeIds.add(id)
            continue
        }
        visibleNodeMap.set(id, node)
    }
    if (duplicateNodeIds.size && import.meta.dev) {
        console.warn('Duplicate family tree node ids ignored:', Array.from(duplicateNodeIds))
    }

    const visibleNodes = Array.from(visibleNodeMap.values())
    const membersById = new Map<number, any>(visibleNodes.map((node: any) => [Number(node.id), node]))
    const nodeIdSet = new Set<number>(visibleNodes.map((node: any) => Number(node.id)))

    type GraphLink = { source: number; target: number }

    const dedupeLinks = (items: Array<{ source: number; target: number; key: string }>): GraphLink[] => {
        const map = new Map<string, GraphLink>()
        for (const item of items) {
            if (!Number.isFinite(item.source) || !Number.isFinite(item.target) || item.source === item.target) continue
            if (!map.has(item.key)) {
                map.set(item.key, { source: item.source, target: item.target })
            }
        }
        return Array.from(map.values())
    }

    const parentLinks = dedupeLinks(
        links.value
            .filter((link: any) => link && link.type === 'parent')
            .map((link: any) => {
                const source = Number(link.source)
                const target = Number(link.target)
                return {
                    source,
                    target,
                    key: `${source}->${target}`,
                }
            })
    )

    const spouseLinks = dedupeLinks(
        links.value
            .filter((link: any) => link && link.type === 'spouse')
            .map((link: any) => {
                const source = Number(link.source)
                const target = Number(link.target)
                const key = source < target ? `${source}-${target}` : `${target}-${source}`
                return { source, target, key }
            })
    )

    const siblingLinks = dedupeLinks(
        links.value
            .filter((link: any) => link && link.type === 'sibling')
            .map((link: any) => {
                const source = Number(link.source)
                const target = Number(link.target)
                const key = source < target ? `${source}-${target}` : `${target}-${source}`
                return { source, target, key }
            })
    )

    const spouseByMember = new Map<number, number>()

    for (const link of spouseLinks) {
        if (!nodeIdSet.has(link.source) || !nodeIdSet.has(link.target)) continue
        if (!spouseByMember.has(link.source)) spouseByMember.set(link.source, link.target)
        if (!spouseByMember.has(link.target)) spouseByMember.set(link.target, link.source)
    }

    const activeSpouseLinks = spouseLinks.filter(
        (link) => spouseByMember.get(link.source) === link.target && spouseByMember.get(link.target) === link.source
    )

    const componentAdjacency = new Map<number, Set<number>>()
    const addComponentEdge = (a: number, b: number) => {
        if (!nodeIdSet.has(a) || !nodeIdSet.has(b) || a === b) return
        if (!componentAdjacency.has(a)) componentAdjacency.set(a, new Set<number>())
        if (!componentAdjacency.has(b)) componentAdjacency.set(b, new Set<number>())
        componentAdjacency.get(a)!.add(b)
        componentAdjacency.get(b)!.add(a)
    }

    for (const link of parentLinks) addComponentEdge(link.source, link.target)
    for (const link of activeSpouseLinks) addComponentEdge(link.source, link.target)
    for (const link of siblingLinks) addComponentEdge(link.source, link.target)

    const componentGroups: any[][] = []
    const visitedComponentNodes = new Set<number>()
    for (const node of visibleNodes) {
        const startId = Number(node.id)
        if (visitedComponentNodes.has(startId)) continue

        const componentIds: number[] = []
        const queue = [startId]
        visitedComponentNodes.add(startId)

        while (queue.length) {
            const id = queue.shift()!
            componentIds.push(id)
            for (const nextId of componentAdjacency.get(id) || []) {
                if (visitedComponentNodes.has(nextId)) continue
                visitedComponentNodes.add(nextId)
                queue.push(nextId)
            }
        }

        componentGroups.push(
            componentIds
                .map((id) => membersById.get(id))
                .filter(Boolean)
                .sort((a, b) => String(a.name || '').localeCompare(String(b.name || ''))),
        )
    }
    componentGroups.sort((a, b) => {
        const aFamily = Math.min(...a.map((node) => Number(node.family_id || node.id)))
        const bFamily = Math.min(...b.map((node) => Number(node.family_id || node.id)))
        return aFamily - bFamily || String(a[0]?.name || '').localeCompare(String(b[0]?.name || ''))
    })

    type LayoutUnit = {
        key: string
        memberIds: number[]
        children: LayoutUnit[]
    }

    const buildComponentLayout = (componentNodes: any[], startX: number) => {
        const componentNodeIds = new Set<number>(componentNodes.map((node) => Number(node.id)))
        const unitByKey = new Map<string, LayoutUnit>()
        const unitKeyByMember = new Map<number, string>()

        const orderedComponentIds = componentNodes
            .map((node) => Number(node.id))
            .filter((id) => Number.isFinite(id))
            .sort((a, b) => a - b)

        const getUnitKey = (id: number) => {
            const spouseId = spouseByMember.get(id)
            if (spouseId && componentNodeIds.has(spouseId)) {
                const first = Math.min(id, spouseId)
                const second = Math.max(id, spouseId)
                return `${first}+${second}`
            }
            return String(id)
        }

        for (const id of orderedComponentIds) {
            const key = getUnitKey(id)
            if (!unitByKey.has(key)) {
                const memberIds = key.split('+').map(Number).filter((memberId) => componentNodeIds.has(memberId))
                unitByKey.set(key, { key, memberIds, children: [] })
            }
            unitKeyByMember.set(id, key)
        }

        const childKeysByUnit = new Map<string, Set<string>>()
        const parentKeysByUnit = new Map<string, Set<string>>()
        const addUnitEdge = (parentKey: string, childKey: string) => {
            if (!unitByKey.has(parentKey) || !unitByKey.has(childKey) || parentKey === childKey) return
            if (!childKeysByUnit.has(parentKey)) childKeysByUnit.set(parentKey, new Set<string>())
            if (!parentKeysByUnit.has(childKey)) parentKeysByUnit.set(childKey, new Set<string>())
            childKeysByUnit.get(parentKey)!.add(childKey)
            parentKeysByUnit.get(childKey)!.add(parentKey)
        }

        for (const link of parentLinks) {
            if (!componentNodeIds.has(link.source) || !componentNodeIds.has(link.target)) continue
            const parentKey = unitKeyByMember.get(link.source)
            const childKey = unitKeyByMember.get(link.target)
            if (parentKey && childKey) addUnitEdge(parentKey, childKey)
        }

        const nameForUnit = (unit: LayoutUnit) => {
            return unit.memberIds
                .map((id) => String(membersById.get(id)?.name || ''))
                .join(' ')
        }

        const unitSort = (a: LayoutUnit, b: LayoutUnit) => {
            const aName = nameForUnit(a)
            const bName = nameForUnit(b)
            return aName.localeCompare(bName) || a.key.localeCompare(b.key)
        }

        const sortedUnits = Array.from(unitByKey.values()).sort(unitSort)
        const roots = sortedUnits.filter((unit) => !parentKeysByUnit.has(unit.key) || parentKeysByUnit.get(unit.key)!.size === 0)
        if (!roots.length && sortedUnits.length) roots.push(sortedUnits[0]!)

        const attached = new Set<string>()
        const cloneAsTree = (unit: LayoutUnit, path = new Set<string>()): LayoutUnit => {
            attached.add(unit.key)
            const nextPath = new Set(path)
            nextPath.add(unit.key)
            const childUnits: LayoutUnit[] = []
            for (const key of Array.from(childKeysByUnit.get(unit.key) || [])) {
                const child = unitByKey.get(key)
                if (!child || nextPath.has(child.key) || attached.has(child.key)) continue
                childUnits.push(child)
            }
            childUnits.sort(unitSort)

            return {
                key: unit.key,
                memberIds: unit.memberIds,
                children: childUnits.map((child) => cloneAsTree(child, nextPath)),
            }
        }

        const forestRoots = roots.map((root) => cloneAsTree(root))
        for (const unit of sortedUnits) {
            if (!attached.has(unit.key)) forestRoots.push(cloneAsTree(unit))
        }

        const hierarchy = d3.hierarchy<LayoutUnit>(
            { key: 'component-root', memberIds: [], children: forestRoots },
            (unit) => unit.children,
        )

        const nodeSpacingX = cardWidth + siblingGap * 0.92
        const treeLayout = d3.tree<LayoutUnit>()
            .nodeSize([nodeSpacingX, levelGap])
            .separation((a, b) => {
                const aWidth = 1
                const bWidth = 1
                const siblingMultiplier = a.parent === b.parent ? 1.05 : 1.15
                return siblingMultiplier * Math.max(aWidth, bWidth)
            })

        const laidOut = treeLayout(hierarchy)
        const realNodes = laidOut.descendants().filter((node) => node.depth > 0)
        const coords = new Map<number, { x: number; y: number }>()
        // Map member id -> member object for quick lookup of generation override
        const memberById = new Map<number, any>((nodes.value || []).map((n: any) => [n.id, n]))
        const minTreeX = Math.min(0, ...realNodes.map((node) => node.x))
        const maxTreeX = Math.max(0, ...realNodes.map((node) => node.x))
        const xOffset = startX - minTreeX + cardWidth

        for (const treeNode of realNodes) {
            const x = xOffset + treeNode.x
            const members = treeNode.data.memberIds
            const depthIndex = Math.max(0, treeNode.depth - 1)
            const y = topOffset + depthIndex * levelGap
            for (const memberId of members) {
                if (memberId !== undefined) coords.set(memberId, { x, y })
            }
        }

        return {
            coords,
            width: Math.max(maxTreeX - minTreeX + cardWidth * 2, cardWidth * 2),
            height: topOffset + Math.max(1, laidOut.height) * levelGap + cardHeight,
        }
    }

    const componentGap = isCompactMobileCard ? 120 : 180
    const nodeCanvasCoords = new Map<number, { x: number; y: number }>()
    const componentLayouts = new Map<number, { coords: Map<number, { x: number; y: number }>; width: number; height: number }>()
    const componentIndexByNodeId = new Map<number, number>()

    let familyCursorX = 80
    for (let componentIndex = 0; componentIndex < componentGroups.length; componentIndex += 1) {
        const componentNodes = componentGroups[componentIndex] || []
        const layout = buildComponentLayout(componentNodes, familyCursorX)
        componentLayouts.set(componentIndex, layout)
        for (const node of componentNodes) {
            const coord = layout.coords.get(Number(node.id))
            if (coord) nodeCanvasCoords.set(Number(node.id), coord)
            if (coord) componentIndexByNodeId.set(Number(node.id), componentIndex)
        }
        familyCursorX += layout.width + componentGap
    }

    globalNodeCoords = nodeCanvasCoords

    const bounds = Array.from(nodeCanvasCoords.values()).reduce(
        (acc, coord) => ({
            minX: Math.min(acc.minX, coord.x),
            maxX: Math.max(acc.maxX, coord.x),
            minY: Math.min(acc.minY, coord.y),
            maxY: Math.max(acc.maxY, coord.y),
        }),
        { minX: Infinity, maxX: -Infinity, minY: Infinity, maxY: -Infinity }
    )

    if (Number.isFinite(bounds.minX) && Number.isFinite(bounds.maxX) && Number.isFinite(bounds.minY) && Number.isFinite(bounds.maxY)) {
        const padding = cardWidth * 2
        const contentWidth = Math.max(1, (bounds.maxX - bounds.minX) + padding * 2)
        const contentHeight = Math.max(1, (bounds.maxY - bounds.minY) + padding * 2)
        const scaleX = (width * 0.92) / contentWidth
        const scaleY = (height * 0.92) / contentHeight
        const scale = Math.max(0.15, Math.min(0.7, scaleX, scaleY))
        const centerX = (bounds.minX + bounds.maxX) / 2
        const centerY = (bounds.minY + bounds.maxY) / 2
        const fittedTransform = d3.zoomIdentity.translate(
            width / 2 - centerX * scale,
            height / 2 - centerY * scale,
        ).scale(scale)
        svg.call(zoom.transform as any, fittedTransform)
    }

    type ParentOverlayLink = {
        source: { x: number; y: number }
        target: { x: number; y: number }
        childId: number
        parentIds: number[]
        crossFamily: boolean
        branchColor?: string
    }

    const renderedNodes = (() => {
        const rendered: Array<{ key: string; members: any[]; primary: any; partner: any | null; x: number; y: number; branchIndex: number }> = []
        const seen = new Set<string>()

        const childCountByMemberId = new Map<number, number>()
        for (const link of parentLinks) {
            childCountByMemberId.set(link.source, (childCountByMemberId.get(link.source) || 0) + 1)
        }

        for (const node of visibleNodes) {
            const id = Number(node.id)
            if (seen.has(String(id))) continue
            const spouseId = spouseByMember.get(id)
            const spouse = spouseId !== undefined ? membersById.get(spouseId) : null
            const hasCouple = Boolean(spouse && spouseId !== undefined && nodeIdSet.has(spouseId) && !seen.has(String(spouseId)))

            if (hasCouple) {
                const primary = node.gender === 'F' && spouse.gender === 'M' ? spouse : node
                const partner = primary === node ? spouse : node
                const pairIds = [Number(primary.id), Number(partner.id)].sort((a, b) => a - b)
                const key = `couple-${pairIds[0]}-${pairIds[1]}`
                seen.add(String(primary.id))
                seen.add(String(partner.id))
                const primaryCoord = nodeCanvasCoords.get(Number(primary.id))
                const partnerCoord = nodeCanvasCoords.get(Number(partner.id))
                const coupleNodeY = ((primaryCoord?.y || 0) + (partnerCoord?.y || 0)) / 2
                const coupleMemberGen = primary.generation ?? partner.generation
                const coupleLevel = (coupleMemberGen !== null && coupleMemberGen !== undefined)
                    ? Math.max(0, Number(coupleMemberGen))
                    : Math.max(0, Math.round((coupleNodeY - topOffset) / levelGap))
                const coupleChildCount = Math.max(
                    childCountByMemberId.get(Number(primary.id)) || 0,
                    childCountByMemberId.get(Number(partner.id)) || 0
                )
                rendered.push({
                    key,
                    members: [primary, partner],
                    primary,
                    partner,
                    x: ((primaryCoord?.x || 0) + (partnerCoord?.x || 0)) / 2,
                    y: coupleNodeY,
                    branchIndex: componentIndexByNodeId.get(Number(primary.id)) || componentIndexByNodeId.get(Number(partner.id)) || 0,
                    level: coupleLevel,
                    childCount: coupleChildCount,
                })
                continue
            }

            seen.add(String(id))
            const coord = nodeCanvasCoords.get(id)
            const nodeY = coord?.y || topOffset
            const memberGen = node.generation
            const level = (memberGen !== null && memberGen !== undefined)
                ? Math.max(0, Number(memberGen))
                : Math.max(0, Math.round((nodeY - topOffset) / levelGap))
            rendered.push({
                key: `single-${id}`,
                members: [node],
                primary: node,
                partner: null,
                x: coord?.x || width / 2,
                y: nodeY,
                branchIndex: componentIndexByNodeId.get(id) || 0,
                level,
                childCount: childCountByMemberId.get(id) || 0,
            })
        }

        return rendered
    })()

    const renderedNodeCoords = new Map<number, { x: number; y: number }>()
    for (const node of renderedNodes) {
        for (const member of node.members) {
            const memberId = Number(member?.id)
            if (!Number.isFinite(memberId)) continue
            renderedNodeCoords.set(memberId, { x: node.x, y: node.y })
        }
    }

    const getRenderCoord = (id: number) => renderedNodeCoords.get(id) || nodeCanvasCoords.get(id)

    const parentLinksByChild = new Map<number, GraphLink[]>()
    for (const link of parentLinks) {
        if (!nodeCanvasCoords.has(link.source) || !nodeCanvasCoords.has(link.target)) continue
        if (!parentLinksByChild.has(link.target)) parentLinksByChild.set(link.target, [])
        parentLinksByChild.get(link.target)!.push(link)
    }

    const parentOverlayData: ParentOverlayLink[] = []
    for (const [childId, childParentLinks] of parentLinksByChild.entries()) {
        const pending = [...childParentLinks].sort((a, b) => a.source - b.source)

        while (pending.length) {
            const link = pending.shift()!
            const spouseIndex = pending.findIndex((candidate) => spouseByMember.get(link.source) === candidate.source)
            const target = getRenderCoord(childId)!

            if (spouseIndex >= 0) {
                const spouseLink = pending.splice(spouseIndex, 1)[0]!
                const firstParent = getRenderCoord(link.source)!
                const secondParent = getRenderCoord(spouseLink.source)!
                const childCoupleCoord = nodeCanvasCoords.get(childId)
                const childCoupleNode = membersById.get(childId)
                const childCoupleGen = childCoupleNode?.generation
                const childCoupleLevel = (childCoupleGen !== null && childCoupleGen !== undefined)
                    ? Math.max(0, Number(childCoupleGen))
                    : Math.max(0, Math.round(((childCoupleCoord?.y || topOffset) - topOffset) / levelGap))
                parentOverlayData.push({
                    source: {
                        x: (firstParent.x + secondParent.x) / 2,
                        y: (firstParent.y + secondParent.y) / 2,
                    },
                    target,
                    childId,
                    parentIds: [link.source, spouseLink.source],
                    crossFamily:
                        membersById.get(link.source)?.family_id !== membersById.get(childId)?.family_id ||
                        membersById.get(spouseLink.source)?.family_id !== membersById.get(childId)?.family_id,
                    branchColor: getLevelTheme(childCoupleLevel).accent,
                })
                continue
            }

            const childSingleCoord = nodeCanvasCoords.get(childId)
            const childSingleNode = membersById.get(childId)
            const childSingleGen = childSingleNode?.generation
            const childSingleLevel = (childSingleGen !== null && childSingleGen !== undefined)
                ? Math.max(0, Number(childSingleGen))
                : Math.max(0, Math.round(((childSingleCoord?.y || topOffset) - topOffset) / levelGap))
            parentOverlayData.push({
                source: getRenderCoord(link.source)!,
                target,
                childId,
                parentIds: [link.source],
                crossFamily: membersById.get(link.source)?.family_id !== membersById.get(childId)?.family_id,
                branchColor: getLevelTheme(childSingleLevel).accent,
            })
        }
    }

    const parentGroups = new Map<string, ParentOverlayLink[]>()
    for (const item of parentOverlayData) {
        const key = `${Math.round(item.source.x)}:${Math.round(item.target.x)}`
        if (!parentGroups.has(key)) parentGroups.set(key, [])
        parentGroups.get(key)!.push(item)
    }

    for (const group of parentGroups.values()) {
        const size = group.length
        for (let i = 0; i < group.length; i++) {
            ;(group[i] as any)._groupIndex = i
            ;(group[i] as any)._groupSize = size
        }
    }

    const spouseOverlayData = activeSpouseLinks
        .filter((link) => getRenderCoord(link.source) && getRenderCoord(link.target))
        .map((link) => {
            const coordA = getRenderCoord(link.source)!
            const lvl = Math.max(0, Math.round(((coordA.y || topOffset) - topOffset) / levelGap))
            return {
                a: coordA,
                b: getRenderCoord(link.target)!,
                crossFamily: membersById.get(link.source)?.family_id !== membersById.get(link.target)?.family_id,
                branchColor: getLevelTheme(lvl).accent,
            }
        })

    g.append('g')
        .attr('class', 'parent-links')
        .selectAll('path')
        .data(parentOverlayData)
        .join('path')
        .attr('fill', 'none')
        .attr('stroke', (d: any) => d.crossFamily ? '#948375' : d.branchColor || '#7D7065')
        .attr('stroke-width', 1.8)
        .attr('stroke-opacity', 0.82)
        .attr('stroke-dasharray', (d) => d.crossFamily ? '4,4' : null)
        .attr('stroke-linecap', 'round')
        .attr('stroke-opacity', (d) => d.crossFamily ? 0.6 : 1)
        .attr('data-child-id', (d) => d.childId)
        .attr('data-parent-ids', (d) => d.parentIds.join(','))
        .attr('d', (d: any) => {
            const sourceY = d.source.y + cardHeight / 2
            const banner = branchBanners[d.childId]
            const bannerOffset = banner ? (banner.isMain ? 44 : 36) : 0
            const targetY = d.target.y - cardHeight / 2 - bannerOffset
            const midY = sourceY + 22
            return `M ${d.source.x} ${sourceY} V ${midY} H ${d.target.x} V ${targetY}`
        })
        .attr('stroke', '#64748B')
        .attr('stroke-width', 1.6)

    g.append('g')
        .attr('class', 'spouse-links')
        .selectAll('path')
        .data(spouseOverlayData)
        .join('path')
        .attr('fill', 'none')
        .attr('stroke', (d: any) => d.crossFamily ? '#A69684' : d.branchColor || '#8A7B6E')
        .attr('stroke-width', 1.8)
        .attr('stroke-opacity', 0.8)
        .attr('stroke-dasharray', (d) => d.crossFamily ? '6,6' : '6,4')
        .attr('stroke-linecap', 'round')
        .attr('stroke-linejoin', 'round')
        .attr('stroke-opacity', (d) => d.crossFamily ? 0.6 : 1)
        .attr('d', (d) => {
            const leftFirst = d.a.x <= d.b.x
            const startX = leftFirst ? d.a.x + cardHalfWidth : d.a.x - cardHalfWidth
            const endX = leftFirst ? d.b.x - cardHalfWidth : d.b.x + cardHalfWidth
            const startY = d.a.y - 10
            const endY = d.b.y - 10
            const midX = startX + (endX - startX) * 0.5
            const dx = Math.min(60, Math.abs(endX - startX) * 0.35)
            const sign = leftFirst ? 1 : -1
            const c1x = midX - dx * sign
            const c2x = midX + dx * sign
            return `M ${startX} ${startY} C ${c1x} ${startY} ${c2x} ${endY} ${endX} ${endY}`
        })

    // Background Level Guides (Clean, Non-Intrusive)
    const uniqueLevels = Array.from(new Set(renderedNodes.map((n: any) => n.level ?? 0))).sort((a: number, b: number) => a - b)
    if (uniqueLevels.length > 0 && Number.isFinite(bounds.minX) && Number.isFinite(bounds.maxX)) {
        const guideGroup = g.append('g').attr('class', 'level-guides')
        guideGroup.lower()

        const leftX = bounds.minX - 160
        const rightX = bounds.maxX + 160

        for (const lvl of uniqueLevels) {
            const theme = getLevelTheme(lvl)
            const lvlY = topOffset + lvl * levelGap

            // Subtle dashed separator line
            guideGroup.append('line')
                .attr('x1', leftX)
                .attr('x2', rightX)
                .attr('y1', lvlY)
                .attr('y2', lvlY)
                .attr('stroke', '#CBD5E1')
                .attr('stroke-width', 1.2)
                .attr('stroke-dasharray', '4,4')
                .attr('stroke-opacity', 0.6)

            // Refined minimalist level badge on left
            const tagW = 74
            const tagH = 22
            const tagX = leftX - 10
            const tagY = lvlY - tagH / 2

            guideGroup.append('rect')
                .attr('x', tagX)
                .attr('y', tagY)
                .attr('width', tagW)
                .attr('height', tagH)
                .attr('rx', tagH / 2)
                .attr('fill', '#FFFFFF')
                .attr('stroke', theme.border)
                .attr('stroke-width', 1.2)
                .style('filter', 'drop-shadow(0 2px 5px rgba(0,0,0,0.04))')

            guideGroup.append('text')
                .attr('x', tagX + tagW / 2)
                .attr('y', lvlY + 3.5)
                .attr('text-anchor', 'middle')
                .attr('fill', theme.darkAccent)
                .attr('font-size', '10px')
                .attr('font-weight', '800')
                .attr('letter-spacing', '0.04em')
                .text(`LEVEL ${lvl + 1}`)
        }
    }

    const nodeGroup = g.append('g')
        .attr('class', 'nodes')
        .selectAll('.node')
        .data(renderedNodes)
        .join('g')
        .attr('class', 'node')
        .attr('data-member-ids', (d: any) => d.members.map((m: any) => Number(m.id)).join(','))
        .attr('transform', (d: any) => `translate(${d.x},${d.y})`)

    nodeGroup.each(function(this: any, d: any) {
        renderCard(d3.select(this), 0, d, getLevelTheme(d.level ?? 0))
    })

}

function renderCard(selection: d3.Selection<any, any, any, any>, dx=0, d: any, levelThemeInput?: LevelTheme | string) {
    if (!d) return
    const compact = isMobileViewport()
    const members = Array.isArray(d.members) && d.members.length ? d.members.filter(Boolean) : [d.primary || d]
    const primary = d.primary || members[0] || d
    const partner = d.partner || members[1] || null
    
    // Historical metadata & spouse lookup
    const meta = historicalMetadata[primary.id] || (partner ? historicalMetadata[partner.id] : undefined)
    const partnerName = partner ? getDisplayName(partner) : (meta?.spouse || '')
    const isCouple = Boolean(partner || meta?.spouse)
    
    const cardWidth = compact ? 130 : 152
    const cardHeight = compact ? 62 : 74
    const cardRadius = 8
    
    const group = selection.append("g").attr("transform", `translate(${dx}, 0)`)
    
    const levelIndex = (d.primary?.generation !== null && d.primary?.generation !== undefined)
      ? Math.max(0, Number(d.primary.generation))
      : (d.level ?? Math.max(0, Math.round((d.y - topOffset) / levelGap)))
    const currentTheme = (typeof levelThemeInput === 'object' && levelThemeInput !== null)
      ? levelThemeInput
      : getLevelTheme(levelIndex)

    const primaryName = getDisplayName(primary)
    
    // Lifespan / Status string
    let dateStr = ''
    if (meta?.dates) {
        dateStr = meta.dates
    } else if (meta?.status) {
        dateStr = meta.status
    } else {
        const bYear = primary.date_of_birth ? new Date(primary.date_of_birth).getFullYear() : null
        const dYear = primary.date_of_death ? new Date(primary.date_of_death).getFullYear() : null
        if (bYear && dYear) {
            dateStr = `${bYear}–${dYear}`
        } else if (bYear) {
            dateStr = `b. ${bYear}`
        } else if (dYear) {
            dateStr = `d. ${dYear}`
        } else if (primary.is_deceased || partner?.is_deceased) {
            dateStr = 'Deceased'
        }
    }
    
    // Child count for this card
    const childCount = Number(d.childCount || 0)
    const romanGenerations = ['I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX']
    const nextGenIndex = Math.min(romanGenerations.length - 1, levelIndex + 1)
    const nextGenLabel = romanGenerations[nextGenIndex]

    // 1. Branch Banner Pill (if this member is a branch or sub-branch head)
    const banner = branchBanners[primary.id] || (partner ? branchBanners[partner.id] : undefined)
    if (banner) {
        const bannerW = compact ? (banner.isMain ? 240 : 190) : (banner.isMain ? 280 : 220)
        const bannerH = banner.isMain ? 32 : 26
        const bannerY = -cardHeight / 2 - (banner.isMain ? 34 : 28)
        
        const bannerG = group.append("g").attr("class", "branch-banner")
        
        bannerG.append("rect")
            .attr("x", -bannerW / 2)
            .attr("y", bannerY - bannerH / 2)
            .attr("width", bannerW)
            .attr("height", bannerH)
            .attr("rx", banner.isMain ? 10 : 8)
            .attr("fill", banner.color)
            .attr("stroke", "rgba(255,255,255,0.3)")
            .attr("stroke-width", 1.2)
            .style("filter", "drop-shadow(0 4px 14px rgba(0,0,0,0.5))")
            
        bannerG.append("text")
            .text(banner.title)
            .attr("x", 0)
            .attr("y", bannerY + (banner.isMain ? 4.5 : 4))
            .attr("text-anchor", "middle")
            .attr("fill", "#FFFFFF")
            .attr("font-size", banner.isMain ? (compact ? "11px" : "12.5px") : (compact ? "10px" : "11px"))
            .attr("font-weight", "800")
            .attr("letter-spacing", "0.8px")
            .style("pointer-events", "none")
            
        // Connector from banner bottom to card top
        bannerG.append("line")
            .attr("x1", 0).attr("x2", 0)
            .attr("y1", bannerY + bannerH / 2)
            .attr("y2", -cardHeight / 2)
            .attr("stroke", "rgba(148, 163, 184, 0.7)")
            .attr("stroke-width", 1.6)
    }

    // 2. Main Card Surface (Light mode generation fill with top accent bar)
    const cardG = group.append("g")
        .style("cursor", "pointer")
        .on("click", () => openMember(primary))

    // Card background
    cardG.append("rect")
        .attr("x", -cardWidth / 2)
        .attr("y", -cardHeight / 2)
        .attr("width", cardWidth)
        .attr("height", cardHeight)
        .attr("rx", cardRadius)
        .attr("fill", currentTheme.cardFill)
        .attr("stroke", currentTheme.border)
        .attr("stroke-width", 1.5)
        .style("filter", "drop-shadow(0 4px 12px rgba(15,23,42,0.06))")

    // Top color accent bar showing generation level
    cardG.append("path")
        .attr("d", `M ${-cardWidth/2 + cardRadius} ${-cardHeight/2} h ${cardWidth - cardRadius*2} a ${cardRadius} ${cardRadius} 0 0 1 ${cardRadius} ${cardRadius} v 2 h ${-cardWidth} v -2 a ${cardRadius} ${cardRadius} 0 0 1 ${cardRadius} ${-cardRadius} Z`)
        .attr("fill", currentTheme.accent)

    // 3. Card Typography (Deep crisp dark slate text for light mode)
    const primaryY = isCouple
        ? (dateStr ? -cardHeight / 2 + 20 : -cardHeight / 2 + 27)
        : (dateStr ? -cardHeight / 2 + 28 : -cardHeight / 2 + 37)

    cardG.append("text")
        .text(primaryName)
        .attr("x", 0)
        .attr("y", primaryY)
        .attr("text-anchor", "middle")
        .attr("fill", "#0F172A")
        .attr("font-size", compact ? "11.5px" : "12.5px")
        .attr("font-weight", "700")

    if (isCouple) {
        cardG.append("text")
            .text(`& ${partnerName}`)
            .attr("x", 0)
            .attr("y", primaryY + 14)
            .attr("text-anchor", "middle")
            .attr("fill", "#334155")
            .attr("font-size", compact ? "10px" : "11px")
            .attr("font-weight", "600")
    }

    if (dateStr) {
        const dateY = isCouple ? primaryY + 28 : primaryY + 15
        cardG.append("text")
            .text(dateStr)
            .attr("x", 0)
            .attr("y", dateY)
            .attr("text-anchor", "middle")
            .attr("fill", "#64748B")
            .attr("font-size", compact ? "9px" : "10px")
            .attr("font-weight", "500")
    }

    // 4. Red Child Badge Pill (e.g. "6 children in Gen V")
    if (childCount > 0) {
        const badgeW = compact ? 88 : 98
        const badgeH = 15
        const badgeY = cardHeight / 2 - badgeH / 2 - 4
        
        const badgeG = cardG.append("g")
        badgeG.append("rect")
            .attr("x", -badgeW / 2)
            .attr("y", badgeY - badgeH / 2)
            .attr("width", badgeW)
            .attr("height", badgeH)
            .attr("rx", badgeH / 2)
            .attr("fill", "#BE123C")
            .attr("stroke", "rgba(255,255,255,0.25)")
            .attr("stroke-width", 0.8)
            
        badgeG.append("text")
            .text(`${childCount} children in Gen ${nextGenLabel}`)
            .attr("x", 0)
            .attr("y", badgeY + 3.5)
            .attr("text-anchor", "middle")
            .attr("fill", "#FFFFFF")
            .attr("font-size", compact ? "7.5px" : "8.5px")
            .attr("font-weight", "700")
    }
}

onMounted(async () => {
    window.addEventListener('resize', handleResize)
    handleResize()
    if (isMobileViewport() && editMode.value) {
        isEditorSheetOpen.value = false
    }
    const profile = await auth.fetchProfile()
    if (!profile) {
        auth.clearAuth()
        router.replace({ path: '/', query: { login: '1', next: route.path } })
        return
    }
    await Promise.all([
        familyStore.fetchFamily(''),
        fetchCommunityRoles(),
    ])
    nodes.value = [...familyStore.flatList()]
    const hasFounder = nodes.value.some((n: any) => n.id === 35 || n.name === 'Chandy')
    if (!hasFounder) {
        visualSubMode.value = 'lineage'
    } else if (route.query.branch) {
        selectedBranchJump.value = String(route.query.branch)
        jumpToBranch()
    }
    setTimeout(() => {
        if (viewMode.value === 'visual') {
            renderVisualTree()
        }
    }, 100)
    mobileEditorSheetVh.value = clampMobileEditorHeight(MOBILE_EDITOR_DEFAULT_VH)
})

onUnmounted(() => {
    stopEditorResize()
    window.removeEventListener('resize', handleResize)
    globalNodeCoords = new Map<number, { x: number; y: number }>()
    if (linkSearchDebounce) {
        clearTimeout(linkSearchDebounce)
    }
})

watch([nodes, links], () => {
    if (viewMode.value === 'visual') {
        setTimeout(renderVisualTree, 100)
    }
}, { deep: true })

watch(viewMode, (newVal) => {
    if (newVal === 'visual') {
        setTimeout(renderVisualTree, 50)
    }
})

watch(locale, () => {
    if (viewMode.value === 'visual') {
        setTimeout(renderVisualTree, 100)
    }
})

watch(
    () => selectedMember.value?.id,
    async (memberId) => {
        if (lastLinkedRelation.value && memberId !== lastLinkedRelation.value.anchorId) {
            lastLinkedRelation.value = null
        }
        linkSearchQuery.value = ''
        resetLinkTarget()
        if (!memberId) return
        await loadMemberContext(memberId)
        if (editMode.value) {
            openQuickEditForSelected()
        }
    }
)

watch(addRelativeMode, (mode) => {
    editorError.value = ''
    editorSuccess.value = ''
    if (mode === 'create') {
        linkSearchQuery.value = ''
        resetLinkTarget()
    } else {
        resetAddRelativeForm()
    }
})

watch(
    () => route.query,
    () => {
        editMode.value = resolveInitialEditMode()
        if (editMode.value) {
            isEditorSheetOpen.value = true
            if (isMobileViewport()) {
                mobileEditorSheetVh.value = MOBILE_EDITOR_DEFAULT_VH
            }
        } else {
            isEditorSheetOpen.value = false
        }
        focusFromQuery()
    },
    { deep: true }
)
</script>

<style scoped>
.fade-scale-enter-active,
.fade-scale-leave-active {
    transition: opacity 0.22s ease, transform 0.22s ease;
}

.fade-scale-enter-from,
.fade-scale-leave-to {
    opacity: 0;
    transform: translateY(-4px) scale(0.985);
}

.fade-slide-enter-active,
.fade-slide-leave-active {
    transition: opacity 0.24s ease, transform 0.24s ease;
}

.fade-slide-enter-from,
.fade-slide-leave-to {
    opacity: 0;
    transform: translateY(6px);
}

.slide-up-editor-enter-active,
.slide-up-editor-leave-active {
    transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.26s ease;
}

.slide-up-editor-enter-from,
.slide-up-editor-leave-to {
    opacity: 0;
    transform: translateY(14px) scale(0.99);
}

@media (max-width: 767px) {
    .quick-edit-sheet input,
    .quick-edit-sheet select,
    .quick-edit-sheet textarea,
    .editor-sheet input,
    .editor-sheet select,
    .editor-sheet textarea {
        min-height: 44px;
        padding-top: 0.625rem;
        padding-bottom: 0.625rem;
        font-size: 0.95rem;
    }

    .quick-edit-sheet button,
    .editor-sheet button {
        min-height: 42px;
    }

    .quick-edit-sheet {
        padding-left: 0.9rem;
        padding-right: 0.9rem;
    }

    .editor-sheet {
        padding-left: 0.9rem;
        padding-right: 0.9rem;
    }
}
</style>
