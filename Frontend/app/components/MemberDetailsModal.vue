<template>
  <Transition name="fade">
    <div v-if="member" class="fixed inset-0 z-[200] flex items-center justify-center p-4 sm:p-6">
      <div class="absolute inset-0 bg-slate-900/40 backdrop-blur-sm transition-opacity" @click="$emit('close')"></div>
      
      <!-- Couple Card Layout -->
      <div v-if="isCoupleCard" class="relative bg-white/95 backdrop-blur-xl rounded-[2rem] w-full max-w-6xl shadow-[0_20px_60px_-15px_rgba(0,0,0,0.3)] border border-white/60 overflow-hidden max-h-[90vh] flex flex-col transform transition-all animate-in zoom-in-95 duration-300">
        
        <!-- Close Button -->
        <button @click="$emit('close')" class="absolute top-4 right-4 z-20 p-2.5 bg-white/50 backdrop-blur-md border border-white/80 hover:bg-white rounded-full text-slate-500 hover:text-slate-800 shadow-sm transition-all hover:scale-105">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>

        <!-- Photo Header: Husband and Wife -->
        <div class="relative bg-gradient-to-br from-brand-gold/15 via-slate-50/80 to-white px-8 pt-10 pb-8 flex gap-12 items-end justify-center border-b border-slate-100">
          <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-[0.03] mix-blend-multiply pointer-events-none"></div>
          
          <!-- Husband Photo -->
          <div class="flex flex-col items-center relative z-10 group">
            <div class="w-36 h-36 rounded-full border-4 border-white overflow-hidden shadow-2xl ring-4 ring-brand-gold/20 transition-transform duration-500 group-hover:scale-105">
              <img 
                :src="resolveImage(husband.photo) || `https://ui-avatars.com/api/?name=${husband.name}&background=cbd5e1&color=fff`" 
                :alt="husband.name"
                class="w-full h-full object-cover"
              />
            </div>
            <p class="mt-4 font-extrabold text-slate-800 text-base tracking-tight">{{ husband.name }}</p>
          </div>

          <!-- Wife Photo -->
          <div class="flex flex-col items-center relative z-10 group">
            <div class="w-36 h-36 rounded-full border-4 border-white overflow-hidden shadow-2xl ring-4 ring-pink-600/10 transition-transform duration-500 group-hover:scale-105">
              <img 
                :src="resolveImage(wife.photo) || `https://ui-avatars.com/api/?name=${wife.name}&background=cbd5e1&color=fff`" 
                :alt="wife.name"
                class="w-full h-full object-cover"
              />
            </div>
            <p class="mt-4 font-extrabold text-slate-800 text-base tracking-tight">{{ wife.name }}</p>
          </div>
        </div>

        <!-- Details Layout -->
        <div class="flex-1 flex flex-col md:flex-row overflow-hidden relative bg-slate-50/30">
          <div class="hidden md:block absolute left-1/2 top-8 bottom-8 w-px bg-gradient-to-b from-transparent via-slate-200 to-transparent -translate-x-1/2 z-10"></div>
          
          <!-- Husband Details -->
          <div class="w-full md:w-1/2 p-6 md:p-10 flex flex-col items-center md:items-start overflow-y-auto custom-scrollbar">
            <span class="px-3 py-1 rounded-full bg-white text-slate-500 text-[10px] font-bold uppercase tracking-widest shadow-sm border border-slate-200 mb-4 inline-block">
              {{ t('memberDetailsModal.labels.age') }}: {{ husband.age ?? t('memberDetailsModal.labels.notAvailable') }}
            </span>
            
              <div class="mb-6 flex gap-2 flex-wrap justify-center md:justify-start">
                <span v-if="husband.gender=='M'" class="text-brand-gold text-[10px] uppercase font-bold tracking-widest bg-brand-gold/10 border border-brand-gold/20 px-2.5 py-1 rounded-md">{{ t('memberDetailsModal.labels.male') }}</span>
                <span v-if="husband.gender=='F'" class="text-pink-600 text-[10px] uppercase font-bold tracking-widest bg-pink-50 border border-pink-200 px-2.5 py-1 rounded-md">{{ t('memberDetailsModal.labels.female') }}</span>
                <span v-if="husband.is_deceased" class="text-slate-500 text-[10px] uppercase font-bold tracking-widest bg-slate-100 border border-slate-200 px-2.5 py-1 rounded-md">{{ t('memberDetailsModal.labels.deceased') }}</span>
                <span v-if="husband.is_independent" class="text-blue-600 text-[10px] uppercase font-bold tracking-widest bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-md">Independent</span>
                <span v-if="husband.has_account" class="text-emerald-600 text-[10px] uppercase font-bold tracking-widest bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-md">Has Account</span>
              </div>
            <div class="w-full grid grid-cols-1 sm:grid-cols-2 gap-4">
              
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Member ID</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.member_id || husband.id || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="husband.name_ml" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Malayalam Name</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.name_ml }}</p>
            </div>
            <div v-if="husband.family_name" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Family / House Name</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.family_name }}</p>
            </div>
            <div v-if="husband.generation !== null && husband.generation !== undefined && husband.generation !== ''" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Generation</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.generation }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ husband.is_deceased ? t('memberDetailsModal.labels.dateOfDeath') : t('memberDetailsModal.labels.dateOfBirth') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.is_deceased && husband.date_of_death ? husband.date_of_death : (husband.date_of_birth || t('memberDetailsModal.labels.notAvailable')) }}</p>
            </div>
            <div v-if="husband.wedding_anniversary" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Wedding Anniversary</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.wedding_anniversary }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.bloodGroup') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.blood_group || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="husband.committee_role" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Community Role</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.committee_role }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.occupation') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.occupation || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="husband.place_of_work" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.workplace') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.place_of_work }}</p>
            </div>
            <div v-if="husband.church_parish" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.parish') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.church_parish }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.education') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.education || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.location') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.location || husband.address || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="husband.email_id" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.email') }}</span>
              <p class="font-semibold text-slate-800 mt-1 break-all">{{ husband.email_id }}</p>
            </div>
            <div v-if="husband.phone_no" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.phone') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ husband.phone_no }}</p>
            </div>
            </div>
          </div>

          <!-- Wife Details -->
          <div class="w-full md:w-1/2 p-6 md:p-10 flex flex-col items-center md:items-start overflow-y-auto custom-scrollbar">
            <span class="px-3 py-1 rounded-full bg-white text-slate-500 text-[10px] font-bold uppercase tracking-widest shadow-sm border border-slate-200 mb-4 inline-block">
              {{ t('memberDetailsModal.labels.age') }}: {{ wife.age ?? t('memberDetailsModal.labels.notAvailable') }}
            </span>
            
              <div class="mb-6 flex gap-2 flex-wrap justify-center md:justify-start">
                <span v-if="wife.gender=='M'" class="text-brand-gold text-[10px] uppercase font-bold tracking-widest bg-brand-gold/10 border border-brand-gold/20 px-2.5 py-1 rounded-md">{{ t('memberDetailsModal.labels.male') }}</span>
                <span v-if="wife.gender=='F'" class="text-pink-600 text-[10px] uppercase font-bold tracking-widest bg-pink-50 border border-pink-200 px-2.5 py-1 rounded-md">{{ t('memberDetailsModal.labels.female') }}</span>
                <span v-if="wife.is_deceased" class="text-slate-500 text-[10px] uppercase font-bold tracking-widest bg-slate-100 border border-slate-200 px-2.5 py-1 rounded-md">{{ t('memberDetailsModal.labels.deceased') }}</span>
                <span v-if="wife.is_independent" class="text-blue-600 text-[10px] uppercase font-bold tracking-widest bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-md">Independent</span>
                <span v-if="wife.has_account" class="text-emerald-600 text-[10px] uppercase font-bold tracking-widest bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-md">Has Account</span>
              </div>
            <div class="w-full grid grid-cols-1 sm:grid-cols-2 gap-4">
              
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Member ID</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.member_id || wife.id || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="wife.name_ml" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Malayalam Name</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.name_ml }}</p>
            </div>
            <div v-if="wife.family_name" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Family / House Name</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.family_name }}</p>
            </div>
            <div v-if="wife.generation !== null && wife.generation !== undefined && wife.generation !== ''" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Generation</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.generation }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ wife.is_deceased ? t('memberDetailsModal.labels.dateOfDeath') : t('memberDetailsModal.labels.dateOfBirth') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.is_deceased && wife.date_of_death ? wife.date_of_death : (wife.date_of_birth || t('memberDetailsModal.labels.notAvailable')) }}</p>
            </div>
            <div v-if="wife.wedding_anniversary" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Wedding Anniversary</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.wedding_anniversary }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.bloodGroup') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.blood_group || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="wife.committee_role" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Community Role</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.committee_role }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.occupation') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.occupation || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="wife.place_of_work" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.workplace') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.place_of_work }}</p>
            </div>
            <div v-if="wife.church_parish" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.parish') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.church_parish }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.education') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.education || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.location') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.location || wife.address || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="wife.email_id" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.email') }}</span>
              <p class="font-semibold text-slate-800 mt-1 break-all">{{ wife.email_id }}</p>
            </div>
            <div v-if="wife.phone_no" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.phone') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ wife.phone_no }}</p>
            </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Single Person Card Layout -->
      <div v-else class="relative bg-white/95 backdrop-blur-xl rounded-[2rem] w-full max-w-4xl shadow-[0_20px_60px_-15px_rgba(0,0,0,0.3)] border border-white/60 overflow-hidden max-h-[90vh] flex flex-col transform transition-all animate-in zoom-in-95 duration-300">
        
        <!-- Close Button -->
        <button @click="$emit('close')" class="absolute top-4 right-4 z-20 p-2.5 bg-white/50 backdrop-blur-md border border-white/80 hover:bg-white rounded-full text-slate-500 hover:text-slate-800 shadow-sm transition-all hover:scale-105 md:hidden">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>

        <!-- Photo Header -->
        <div class="relative bg-gradient-to-br from-brand-gold/15 via-slate-50/80 to-white px-8 pt-10 pb-8 flex flex-col items-center justify-center border-b border-slate-100">
          <div class="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-[0.03] mix-blend-multiply pointer-events-none"></div>
          
          <div class="relative z-10 group">
            <div class="w-40 h-40 rounded-full border-4 border-white overflow-hidden shadow-2xl ring-4 ring-brand-gold/20 transition-transform duration-500 group-hover:scale-105">
              <img 
                :src="resolveImage(member.photo) || `https://ui-avatars.com/api/?name=${member.name}&background=cbd5e1&color=fff`" 
                :alt="member.name"
                class="w-full h-full object-cover"
              />
            </div>
          </div>
          <p class="mt-5 font-extrabold text-slate-800 text-xl tracking-tight relative z-10">{{ member.name }}</p>
        </div>

        <!-- Details Section -->
        <div class="flex-1 flex flex-col overflow-hidden bg-slate-50/30">
          <div class="w-full p-6 md:p-10 flex flex-col overflow-y-auto custom-scrollbar">
            <!-- Header & Close -->
            <div class="flex flex-col md:flex-row justify-between items-start md:items-center mb-8 gap-4">
                <div>
                  <h3 class="text-sm font-black text-brand-gold uppercase tracking-widest">{{ t('memberDetailsModal.labels.member') }}</h3>
                  <p class="text-xs text-slate-400 mt-1">{{ t('memberDetailsModal.labels.profileDetails') }}</p>
                  <div class="mt-4 flex gap-2 flex-wrap">
                    <span class="px-3 py-1 rounded-full bg-white text-slate-500 text-[10px] font-bold uppercase tracking-widest shadow-sm border border-slate-200">
                      {{ t('memberDetailsModal.labels.age') }}: {{ member.age }}
                    </span>
                    <div class="mb-6 flex gap-2 flex-wrap justify-center md:justify-start">
                <span v-if="member.gender=='M'" class="text-brand-gold text-[10px] uppercase font-bold tracking-widest bg-brand-gold/10 border border-brand-gold/20 px-2.5 py-1 rounded-md">{{ t('memberDetailsModal.labels.male') }}</span>
                <span v-if="member.gender=='F'" class="text-pink-600 text-[10px] uppercase font-bold tracking-widest bg-pink-50 border border-pink-200 px-2.5 py-1 rounded-md">{{ t('memberDetailsModal.labels.female') }}</span>
                <span v-if="member.is_deceased" class="text-slate-500 text-[10px] uppercase font-bold tracking-widest bg-slate-100 border border-slate-200 px-2.5 py-1 rounded-md">{{ t('memberDetailsModal.labels.deceased') }}</span>
                <span v-if="member.is_independent" class="text-blue-600 text-[10px] uppercase font-bold tracking-widest bg-blue-50 border border-blue-200 px-2.5 py-1 rounded-md">Independent</span>
                <span v-if="member.has_account" class="text-emerald-600 text-[10px] uppercase font-bold tracking-widest bg-emerald-50 border border-emerald-200 px-2.5 py-1 rounded-md">Has Account</span>
              </div>
                  </div>
                </div>
                <div class="hidden md:flex items-center gap-3">
                  <button
                    v-if="canEdit"
                    @click="$emit('edit')"
                    class="rounded-xl border border-brand-gold/30 bg-brand-gold/5 px-4 py-2 text-xs font-bold uppercase tracking-wide text-brand-gold transition-all hover:bg-brand-gold hover:text-white shadow-sm hover:shadow-md"
                  >
                    Edit Member
                  </button>
                  <button @click="$emit('close')" class="p-2.5 bg-white border border-slate-200 hover:border-slate-300 rounded-full text-slate-400 hover:text-slate-700 shadow-sm transition-all hover:scale-105">
                    <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                  </button>
                </div>
            </div>

            <!-- Household Members -->
            <div v-if="member.householdMembers && member.householdMembers.length > 1" class="mb-10">
                <span class="text-[10px] text-slate-400 uppercase font-bold tracking-wider block mb-4">Household Members</span>
                <div class="grid gap-4 sm:grid-cols-2">
                    <div v-for="person in member.householdMembers" :key="person.id" class="rounded-xl border border-slate-100 bg-white p-5 shadow-sm hover:shadow-md transition-shadow">
                        <div class="text-sm font-extrabold text-slate-800">{{ person.name }}</div>
                        <div class="mt-3 grid grid-cols-2 gap-4 text-xs text-slate-600">
                            <div>
                                <span class="block text-[9px] font-bold uppercase tracking-wider text-slate-400">Member ID</span>
                                <p class="font-semibold mt-0.5">{{ person.member_id || person.id || t('memberDetailsModal.labels.notAvailable') }}</p>
                            </div>
                            <div>
                                <span class="block text-[9px] font-bold uppercase tracking-wider text-slate-400">{{ t('memberDetailsModal.labels.age') }}</span>
                                <p class="font-semibold mt-0.5">{{ person.age }}</p>
                            </div>
                            <div>
                                <span class="block text-[9px] font-bold uppercase tracking-wider text-slate-400">{{ t('memberDetailsModal.labels.bloodGroup') }}</span>
                                <p class="font-semibold mt-0.5">{{ person.blood_group || t('memberDetailsModal.labels.notAvailable') }}</p>
                            </div>
                            <div>
                                <span class="block text-[9px] font-bold uppercase tracking-wider text-slate-400">{{ t('memberDetailsModal.labels.occupation') }}</span>
                                <p class="font-semibold mt-0.5">{{ person.occupation || t('memberDetailsModal.labels.notAvailable') }}</p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Details Grid -->
            <div class="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-4 mb-10">
              <div v-if="member.spouse" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
                <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.spouse') }}</span>
                <p class="font-semibold text-slate-800 mt-1">{{ member.spouse }}</p>
              </div>
              
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Member ID</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.member_id || member.id || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="member.name_ml" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Malayalam Name</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.name_ml }}</p>
            </div>
            <div v-if="member.family_name" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Family / House Name</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.family_name }}</p>
            </div>
            <div v-if="member.generation !== null && member.generation !== undefined && member.generation !== ''" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Generation</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.generation }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ member.is_deceased ? t('memberDetailsModal.labels.dateOfDeath') : t('memberDetailsModal.labels.dateOfBirth') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.is_deceased && member.date_of_death ? member.date_of_death : (member.date_of_birth || t('memberDetailsModal.labels.notAvailable')) }}</p>
            </div>
            <div v-if="member.wedding_anniversary" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Wedding Anniversary</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.wedding_anniversary }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.bloodGroup') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.blood_group || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="member.committee_role" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">Community Role</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.committee_role }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.occupation') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.occupation || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="member.place_of_work" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.workplace') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.place_of_work }}</p>
            </div>
            <div v-if="member.church_parish" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.parish') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.church_parish }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.education') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.education || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.location') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.location || member.address || t('memberDetailsModal.labels.notAvailable') }}</p>
            </div>
            <div v-if="member.email_id" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.email') }}</span>
              <p class="font-semibold text-slate-800 mt-1 break-all">{{ member.email_id }}</p>
            </div>
            <div v-if="member.phone_no" class="bg-white rounded-xl p-4 shadow-sm border border-slate-100 hover:shadow-md hover:border-brand-gold/30 transition-all duration-300 group">
              <span class="block text-[10px] font-bold uppercase tracking-wider text-slate-400 group-hover:text-brand-gold/70 transition-colors">{{ t('memberDetailsModal.labels.phone') }}</span>
              <p class="font-semibold text-slate-800 mt-1 ">{{ member.phone_no }}</p>
            </div>
            </div>

            <!-- Bio -->
            <div v-if="member.bio" class="mb-10">
               <span class="text-[10px] text-slate-400 uppercase font-bold tracking-wider block mb-3">{{ t('memberDetailsModal.labels.biography') }}</span>
                <div class="relative bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
                    <svg class="absolute top-4 left-4 w-8 h-8 text-slate-100" fill="currentColor" viewBox="0 0 24 24"><path d="M14.017 21v-7.391c0-5.704 3.731-9.57 8.983-10.609l.995 2.151c-2.432.917-3.995 3.638-3.995 5.849h4v10h-9.983zm-14.017 0v-7.391c0-5.704 3.748-9.57 9-10.609l.996 2.151c-2.433.917-3.996 3.638-3.996 5.849h4v10h-10z"/></svg>
                    <p class="text-slate-600 text-sm leading-relaxed italic relative z-10 pl-8 pr-4">
                        {{ member.bio }}
                    </p>
                </div>
            </div>
            
            <!-- Children Table -->
            <div v-if="member.children && member.children.length > 0">
               <span class="text-[10px] text-slate-400 uppercase font-bold tracking-wider block mb-4">{{ t('memberDetailsModal.labels.children') }}</span>
                <div class="overflow-hidden rounded-2xl border border-slate-100 shadow-sm bg-white">
                    <table class="w-full text-sm text-left text-slate-600">
                        <thead class="text-[10px] text-slate-400 uppercase bg-slate-50/80 border-b border-slate-100 tracking-wider">
                            <tr>
                              <th class="px-6 py-3 font-bold">{{ t('memberDetailsModal.labels.name') }}</th>
                              <th class="px-6 py-3 font-bold w-28">{{ t('memberDetailsModal.labels.age') }}</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-50">
                            <tr v-for="child in member.children" :key="child.name" class="hover:bg-slate-50/50 transition-colors">
                                <td class="px-6 py-4 font-semibold text-slate-800">{{ child.name }}</td>
                                <td class="px-6 py-4 text-slate-500 font-medium">{{ child.age }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div v-else class="text-slate-400 text-xs italic bg-slate-50/50 rounded-xl p-4 border border-slate-100">
                {{ t('memberDetailsModal.labels.noChildren') }}
            </div>
          </div>
        </div>
      </div>
    </div>
  </Transition>
</template>

<script setup>
import { useRuntimeConfig } from '#imports'
import { useI18n } from 'vue-i18n'
import { computed } from 'vue'
const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'
const { t } = useI18n()

const props = defineProps({
  member: Object,
  canEdit: {
    type: Boolean,
    default: false,
  },
})
defineEmits(['close', 'edit'])

const isCoupleCard = computed(() => {
  return props.member?.partner ? true : false
})

const husband = computed(() => {
  if (!isCoupleCard.value) return null
  
  // If the main member is male, they are the husband
  if (props.member.gender === 'M') {
    return props.member
  }
  // Otherwise, the partner is the husband
  return props.member.partner
})

const wife = computed(() => {
  if (!isCoupleCard.value) return null
  
  // If the main member is female, they are the wife
  if (props.member.gender === 'F') {
    return props.member
  }
  // Otherwise, the partner is the wife
  return props.member.partner
})

const resolveImage = (path) => {
    if (!path) return null
    if (path.startsWith('http')) return path
    return `${apiBase}${path}`
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
