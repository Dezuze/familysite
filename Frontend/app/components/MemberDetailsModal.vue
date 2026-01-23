<template>
  <Transition name="fade">
    <div v-if="member" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <div class="absolute inset-0 bg-black/80 backdrop-blur-sm" @click="$emit('close')"></div>
      
      <div class="relative bg-white rounded-2xl w-full max-w-4xl shadow-2xl border border-slate-200 overflow-hidden flex flex-col md:flex-row max-h-[90vh]">
        
        <!-- Close Button (Mobile) -->
        <button @click="$emit('close')" class="absolute top-4 right-4 z-10 p-2 bg-black/10 hover:bg-black/20 rounded-full text-slate-600 md:hidden">
            <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>

        <!-- Left Side: Image & Age -->
        <div class="w-full md:w-1/3 bg-slate-50 p-8 flex flex-col items-center justify-center border-r border-slate-100 relative">
             <div class="w-48 h-48 rounded-full border-4 border-white overflow-hidden shadow-xl mb-6 ring-1 ring-slate-200">
               <img 
                 :src="member.photo || `https://ui-avatars.com/api/?name=${member.name}&background=cbd5e1&color=fff`" 
                 class="w-full h-full object-cover"
               />
             </div>
             
             <h2 class="text-2xl font-serif font-bold text-slate-800 text-center mb-2">{{ member.name }}</h2>
             <span class="px-4 py-1 rounded-full bg-white text-slate-600 text-sm font-bold shadow-sm border border-slate-200">
               Age: {{ member.age }}
             </span>
             
             <div class="mt-6 flex gap-2">
                <span v-if="member.gender=='M'" class="text-blue-600 text-xs uppercase font-bold tracking-wider bg-blue-50 px-2 py-1 rounded-md">Male</span>
                <span v-if="member.gender=='F'" class="text-pink-600 text-xs uppercase font-bold tracking-wider bg-pink-50 px-2 py-1 rounded-md">Female</span>
                <span v-if="member.is_deceased" class="text-slate-500 text-xs uppercase font-bold tracking-wider bg-slate-200 px-2 py-1 rounded-md">Deceased</span>
             </div>
        </div>

        <!-- Right Side: Details -->
        <div class="w-full md:w-2/3 p-8 overflow-y-auto custom-scrollbar bg-white">
            <!-- Header & Close -->
            <div class="flex justify-between items-start mb-6">
                <div>
                    <h3 class="text-lg font-bold text-amber-600 uppercase tracking-widest">{{ member.committee_role || member.role || member.relation || 'Member' }}</h3>
                    <p class="text-xs text-slate-500">Profile Details</p>
                </div>
                <button @click="$emit('close')" class="hidden md:block p-2 text-slate-400 hover:text-slate-800 transition-colors">
                    <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>

            <!-- Details Grid -->
            <div class="grid grid-cols-2 gap-6 mb-8">
                <div>
                   <span class="text-xs text-slate-400 uppercase font-bold">{{ member.is_deceased ? 'Date of Death' : 'Date of Birth' }}</span>
                   <p class="text-slate-800 font-medium">
                       {{ member.is_deceased && member.date_of_death ? member.date_of_death : (member.date_of_birth || 'N/A') }}
                   </p>
                </div>
                <div>
                   <span class="text-xs text-slate-400 uppercase font-bold">Blood Group</span>
                   <p class="text-slate-800 font-medium">{{ member.blood_group || 'N/A' }}</p>
                </div>
                <div>
                   <span class="text-xs text-slate-400 uppercase font-bold">Occupation</span>
                   <p class="text-slate-800 font-medium">{{ member.occupation || 'N/A' }}</p>
                </div>
                <div v-if="member.place_of_work">
                   <span class="text-xs text-slate-400 uppercase font-bold">Workplace</span>
                   <p class="text-slate-800 font-medium">{{ member.place_of_work }}</p>
                </div>
                <div v-if="member.church_parish">
                   <span class="text-xs text-slate-400 uppercase font-bold">Parish</span>
                   <p class="text-slate-800 font-medium">{{ member.church_parish }}</p>
                </div>
                <div>
                   <span class="text-xs text-slate-400 uppercase font-bold">Spouse</span>
                   <p class="text-slate-800 font-medium">{{ member.spouse || 'N/A' }}</p>
                </div>
                <div>
                   <span class="text-xs text-slate-400 uppercase font-bold">Location</span>
                   <p class="text-slate-800 font-medium">{{ member.location || member.address || 'N/A' }}</p>
                </div>
                <div>
                   <span class="text-xs text-slate-400 uppercase font-bold">Education</span>
                   <p class="text-slate-800 font-medium">{{ member.education || 'N/A' }}</p>
                </div>
                <div v-if="member.email_id">
                   <span class="text-xs text-slate-400 uppercase font-bold">Email</span>
                   <p class="text-slate-800 font-medium break-all">{{ member.email_id }}</p>
                </div>
                <div v-if="member.phone_no">
                   <span class="text-xs text-slate-400 uppercase font-bold">Phone</span>
                   <p class="text-slate-800 font-medium">{{ member.phone_no }}</p>
                </div>
            </div>

            <!-- Bio -->
            <div v-if="member.bio" class="mb-8">
                <span class="text-xs text-slate-400 uppercase font-bold block mb-2">Biography</span>
                <p class="text-slate-600 text-sm leading-relaxed bg-slate-50 p-4 rounded-lg border border-slate-100 italic">
                    "{{ member.bio }}"
                </p>
            </div>
            
            <!-- Children Table -->
            <div v-if="member.children && member.children.length > 0">
                <span class="text-xs text-slate-400 uppercase font-bold block mb-3">Children</span>
                <div class="overflow-hidden rounded-lg border border-slate-200">
                    <table class="w-full text-sm text-left text-slate-600">
                        <thead class="text-xs text-slate-500 uppercase bg-slate-50">
                            <tr>
                                <th class="px-4 py-2 font-medium">Name</th>
                                <th class="px-4 py-2 font-medium w-24">Age</th>
                            </tr>
                        </thead>
                        <tbody class="divide-y divide-slate-100">
                            <tr v-for="child in member.children" :key="child.name" class="bg-white hover:bg-slate-50 transition-colors">
                                <td class="px-4 py-2 font-medium text-slate-800">{{ child.name }}</td>
                                <td class="px-4 py-2 text-slate-500">{{ child.age }}</td>
                            </tr>
                        </tbody>
                    </table>
                </div>
            </div>
            <div v-else class="text-slate-400 text-sm italic">
                No children listed.
            </div>

        </div>

      </div>
    </div>
  </Transition>
</template>

<script setup>
defineProps({
  member: Object
})
defineEmits(['close'])
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
