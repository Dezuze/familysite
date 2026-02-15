<template>
  <div class="min-h-screen bg-[#F5F5F7] text-slate-900 pt-32 pb-16 px-4 flex flex-col items-center font-sans">
    
    <div class="max-w-3xl w-full">
        <!-- Progress Steps -->
         <div class="flex items-center justify-center mb-10 gap-4">
              <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-300', step >= 1 ? 'bg-brand-gold text-white shadow-lg scale-110' : 'bg-white text-slate-400 border border-slate-200']">1</div>
              <div class="h-0.5 w-12 bg-slate-200"></div>
              <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-300', step >= 2 ? 'bg-brand-gold text-white shadow-lg scale-110' : 'bg-white text-slate-400 border border-slate-200']">2</div>
              <div class="h-0.5 w-12 bg-slate-200"></div>
              <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-300', step >= 3 ? 'bg-brand-gold text-white shadow-lg scale-110' : 'bg-white text-slate-400 border border-slate-200']">3</div>
         </div>

        <div class="bg-white/70 backdrop-blur-2xl p-8 md:p-12 rounded-[40px] shadow-[0_20px_40px_rgba(0,0,0,0.05)] border border-white/60 relative overflow-hidden transition-all duration-500">
            
            <div class="relative z-10 transition-all duration-500" v-auto-animate>
                <h1 class="text-3xl md:text-4xl font-bold mb-3 text-center text-slate-900 tracking-tight">Your Profile</h1>
                <p class="text-slate-500 text-center mb-12 text-base font-medium">Update your information for the family directory.</p>

                <form @submit.prevent="saveProfile" class="space-y-4">
                    
                    <!-- Step 1: Personal Info -->
                    <div v-if="step === 1" class="space-y-8 animate-fade-in">
                        <!-- Avatar Upload -->
                        <div class="flex justify-center mb-8">
                            <div class="relative w-36 h-36 group cursor-pointer transition-transform hover:scale-105">
                               <input type="file" @change="onFileChange" accept="image/*" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20" />
                               <div class="w-full h-full rounded-full bg-white shadow-xl border-4 border-white flex items-center justify-center overflow-hidden relative">
                                   <div v-if="!avatarPreview" class="absolute inset-0 bg-slate-100 flex flex-col items-center justify-center text-slate-400 group-hover:bg-slate-200 transition-colors">
                                       <svg class="w-10 h-10 mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                       <span class="text-xs font-semibold">Change Photo</span>
                                   </div>
                                   <img v-else :src="avatarPreview" class="w-full h-full object-cover" />
                               </div>
                                <div class="absolute bottom-2 right-2 bg-brand-gold text-white rounded-full p-2.5 shadow-lg z-10 pointer-events-none group-hover:brightness-110 transition-colors">
                                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                                </div>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">First Name</label>
                                 <input v-model="form.first_name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-brand-gold focus:ring-4 focus:ring-brand-gold/10 outline-none transition-all placeholder:text-slate-400" placeholder="John">
                            </div>
                            <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Last Name</label>
                                <input v-model="form.last_name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-brand-gold focus:ring-4 focus:ring-brand-gold/10 outline-none transition-all placeholder:text-slate-400" placeholder="Doe">
                            </div>
                        </div>

                         <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Nickname</label>
                                <input v-model="form.nickname" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400" placeholder="Johnny">
                            </div>
                             <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Gender</label>
                                 <select v-model="form.gender" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-brand-gold focus:ring-4 focus:ring-brand-gold/10 outline-none transition-all appearance-none cursor-pointer">
                                     <option value="M">Male</option>
                                     <option value="F">Female</option>
                                     <option value="O">Other</option>
                                 </select>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Date of Birth</label>
                                <input v-model="form.date_of_birth" type="date" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all cursor-text">
                            </div>
                            <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Blood Group</label>
                                <div class="relative">
                                     <select v-model="form.blood_group" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-brand-gold focus:ring-4 focus:ring-brand-gold/10 outline-none transition-all appearance-none cursor-pointer">
                                         <option>Unknown</option><option>A+</option><option>A-</option><option>B+</option><option>B-</option><option>O+</option><option>O-</option><option>AB+</option><option>AB-</option>
                                     </select>
                                    <div class="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none">
                                        <svg class="w-5 h-5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div>
                             <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Bio</label>
                             <textarea v-model="form.bio" rows="3" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400 resize-none" placeholder="Tell the family a bit about yourself..."></textarea>
                        </div>
                    </div>

                    <!-- Step 2: Contact & Additional -->
                    <div v-if="step === 2" class="space-y-8 animate-fade-in">
                         
                         <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                             <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Email</label>
                                <input v-model="form.email_id" type="email" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400" placeholder="john@example.com">
                             </div>
                             <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Phone Number</label>
                                <input v-model="form.phone_no" type="tel" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400" placeholder="+91 9876543210">
                             </div>
                         </div>

                         <div>
                            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Address</label>
                            <textarea v-model="form.address" rows="2" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400 resize-none" placeholder="Full residential address"></textarea>
                         </div>

                         <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                             <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Occupation</label>
                                <input v-model="form.occupation" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400" placeholder="Software Engineer">
                            </div>
                             <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Place of Work</label>
                                 <input v-model="form.place_of_work" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-brand-gold focus:ring-4 focus:ring-brand-gold/10 outline-none transition-all placeholder:text-slate-400" placeholder="TechPark, Kochi">
                            </div>
                         </div>
 
                         <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                             <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Education</label>
                                <input v-model="form.education" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-brand-gold focus:ring-4 focus:ring-brand-gold/10 outline-none transition-all placeholder:text-slate-400" placeholder="B.Tech Computer Science">
                            </div>
                             <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Parish / Church</label>
                                <input v-model="form.church_parish" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-brand-gold focus:ring-4 focus:ring-brand-gold/10 outline-none transition-all placeholder:text-slate-400" placeholder="St. Mary's Forane Church">
                            </div>
                         </div>

                         <!-- Parent Selection -->
                         <div class="group">
                             <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Link Parents</label>
                             <div class="space-y-4">
                                 <!-- Selected Parents Chips -->
                                 <div v-if="form.parents.length > 0" class="flex flex-wrap gap-2">
                                      <div v-for="pid in form.parents" :key="pid" class="flex items-center gap-2 bg-brand-gold/5 text-brand-gold px-3 py-1.5 rounded-full text-xs font-bold border border-brand-gold/10">
                                          {{ getMemberName(pid) }}
                                          <button @click="removeParent(pid)" type="button" class="text-brand-gold-dark hover:text-brand-gold transition-colors">
                                              <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                                          </button>
                                      </div>
                                 </div>
                                 
                                 <!-- Search Input -->
                                 <div class="relative">
                                     <input 
                                         v-model="parentSearch" 
                                         type="text" 
                                         class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400" 
                                         placeholder="Search parents to link..."
                                     >
                                     <!-- Search Results Dropdown -->
                                     <div v-if="filteredPotentialParents.length > 0" class="absolute z-30 w-full mt-2 bg-white border border-slate-200 rounded-2xl shadow-xl overflow-hidden py-2 animate-fade-in">
                                         <button 
                                             v-for="pm in filteredPotentialParents" 
                                             :key="pm.id" 
                                             @click="addParent(pm)" 
                                             type="button"
                                             class="w-full text-left px-6 py-3 hover:bg-slate-50 transition-colors flex items-center gap-3"
                                         >
                                             <div class="w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-xs font-bold text-slate-500 overflow-hidden">
                                                 <img v-if="pm.photo" :src="pm.photo.startsWith('http') ? pm.photo : apiBase+pm.photo" class="w-full h-full object-cover">
                                                 <span v-else>{{ pm.name.charAt(0) }}</span>
                                             </div>
                                             <div>
                                                 <div class="font-bold text-slate-800">{{ pm.name }}</div>
                                                 <div class="text-xs text-slate-500">{{ pm.relation }}</div>
                                             </div>
                                         </button>
                                     </div>
                                 </div>
                                 <p class="text-[10px] text-slate-400 font-medium ml-1 uppercase tracking-tight">Linking parents helps build the family tree automatically.</p>
                             </div>
                         </div>
                    </div>

                    <!-- Actions -->
                    <div class="pt-10 flex justify-between items-center">
                        <button v-if="step > 1" type="button" @click="step--" class="text-slate-500 hover:text-slate-800 font-semibold transition-colors flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-slate-100">
                            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
                            Back
                        </button>
                        <div v-else></div> <!-- spacer -->

                         <button v-if="step < 2" type="button" @click="step++" class="bg-brand-gold hover:brightness-110 text-white px-8 py-3.5 rounded-2xl font-bold shadow-lg shadow-brand-gold/20 transition-all hover:scale-[1.02] active:scale-95 flex items-center gap-2">
                             Next Step
                             <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                         </button>
                         <button v-else type="submit" :disabled="loading" class="bg-linear-to-b from-brand-gold to-brand-gold-dark hover:brightness-110 text-white px-8 py-3.5 rounded-2xl font-bold shadow-xl shadow-brand-gold/20 transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed">
                             {{ loading ? 'Saving Changes...' : 'Save & Continue' }}
                         </button>
                    </div>

                    <!-- Step 3: Managed Members (Children/Others) -->
                    <div v-if="step === 3" class="space-y-8 animate-fade-in">
                        <div class="flex justify-between items-center mb-6">
                            <div>
                                <h2 class="text-xl font-bold text-slate-800">Managed Members</h2>
                                <p class="text-sm text-slate-500">People you've added to the family tree.</p>
                            </div>
                            <button @click="openAddManaged" type="button" class="bg-brand-gold hover:bg-brand-gold/90 text-white px-4 py-2 rounded-xl font-bold text-sm shadow-lg shadow-brand-gold/20 transition-all flex items-center gap-2">
                                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                                Add Member
                            </button>
                        </div>

                         <!-- Managed Members List -->
                         <div v-if="managedMembers.length > 0" class="grid grid-cols-1 gap-4">
                             <div v-for="m in managedMembers" :key="m.id" class="bg-slate-50 border border-slate-200 p-4 rounded-2xl flex items-center justify-between group hover:border-brand-gold/50 transition-all">
                                <div class="flex items-center gap-4">
                                    <div class="w-12 h-12 rounded-full overflow-hidden bg-white border border-slate-200">
                                        <img v-if="m.photo || m.profile_pic" :src="resolveImage(m.photo || m.profile_pic)" class="w-full h-full object-cover">
                                        <div v-else class="w-full h-full flex items-center justify-center text-slate-400 font-bold uppercase">{{ m.name.charAt(0) }}</div>
                                    </div>
                                    <div>
                                        <div class="font-bold text-slate-800">{{ m.name }}</div>
                                        <div class="text-xs text-slate-500">{{ m.relation }} • {{ m.age || 0 }} years</div>
                                    </div>
                                </div>
                                 <div class="flex items-center gap-2">
                                     <button @click="editManagedMember(m)" type="button" class="p-2 text-slate-400 hover:text-brand-gold hover:bg-brand-gold/5 rounded-lg transition-all">
                                         <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"></path></svg>
                                     </button>
                                    <button @click="confirmDeleteManaged(m)" type="button" class="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all">
                                        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg>
                                    </button>
                                </div>
                            </div>
                        </div>
                        <div v-else class="text-center py-12 bg-slate-50 rounded-3xl border border-dashed border-slate-300">
                             <div class="text-slate-400 mb-2 font-medium">No members added yet</div>
                             <p class="text-xs text-slate-500">Add children or relatives who don't have an account.</p>
                        </div>

                        <!-- Step 3 Navigation -->
                        <div class="pt-6 flex justify-between items-center">
                            <button type="button" @click="step--" class="text-slate-500 hover:text-slate-800 font-semibold transition-colors flex items-center gap-2 px-4 py-2 rounded-lg hover:bg-slate-100">
                                <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
                                Back
                            </button>
                             <button @click="router.push('/')" type="button" class="bg-brand-gold hover:brightness-110 text-white px-8 py-3 rounded-2xl font-bold shadow-lg shadow-brand-gold/20 transition-all hover:scale-[1.02]">
                                 Finish & View Home
                             </button>
                        </div>
                    </div>

                </form>
            </div>
        </div>
    </div>

    <!-- MANAGED MEMBER MODAL -->
    <ClientOnly>
      <Teleport to="body">
        <div v-if="managedModal" class="fixed inset-0 z-40 bg-black/60 backdrop-blur-sm flex items-center justify-center p-4">
            <div class="bg-white rounded-[40px] w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col shadow-2xl animate-fade-up">
                <div class="p-6 border-b border-slate-100 flex justify-between items-center bg-slate-50 shrink-0">
                    <h3 class="text-2xl font-bold text-slate-800">{{ editingManagedId ? 'Edit Member' : 'Add New Member' }}</h3>
                    <button @click="managedModal = false" class="p-2 hover:bg-slate-200 rounded-full transition-colors text-slate-500">
                        <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                    </button>
                </div>

                <div class="overflow-y-auto p-8 flex-1">
                    <form @submit.prevent="saveManagedMember" class="space-y-6">
                        <!-- Avatar for Managed Member -->
                        <div class="flex justify-center mb-8">
                             <div class="relative w-28 h-28 group cursor-pointer transition-transform hover:scale-105">
                                <input type="file" @change="onManagedFileChange" accept="image/*" class="absolute inset-0 w-full h-full opacity-0 cursor-pointer z-20" />
                                <div class="w-full h-full rounded-full bg-white shadow-lg border-2 border-slate-100 flex items-center justify-center overflow-hidden relative">
                                    <div v-if="!managedAvatarPreview" class="absolute inset-0 bg-slate-50 flex flex-col items-center justify-center text-slate-400 group-hover:bg-slate-100 transition-colors">
                                        <svg class="w-8 h-8 mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"></path></svg>
                                        <span class="text-[10px] font-bold uppercase tracking-wider">Photo</span>
                                    </div>
                                    <img v-else :src="managedAvatarPreview" class="w-full h-full object-cover" />
                                </div>
                             </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label class="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">First Name</label>
                                 <input v-model="managedForm.first_name" required type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-slate-900 focus:bg-white focus:border-brand-gold outline-none transition-all">
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Last Name</label>
                                <input v-model="managedForm.last_name" required type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-slate-900 focus:bg-white focus:border-brand-gold outline-none transition-all">
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label class="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Relation</label>
                                 <select v-model="managedForm.relation" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-slate-900 focus:bg-white focus:border-brand-gold outline-none transition-all">
                                    <option>Child</option>
                                    <option>Spouse</option>
                                    <option>Parent</option>
                                    <option>Sibling</option>
                                    <option>Grandchild</option>
                                    <option>Other</option>
                                </select>
                            </div>
                            <div>
                                <label class="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Gender</label>
                                <select v-model="managedForm.gender" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-slate-900 focus:bg-white focus:border-brand-gold outline-none transition-all">
                                    <option value="M">Male</option>
                                    <option value="F">Female</option>
                                    <option value="O">Other</option>
                                </select>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div>
                                <label class="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Date of Birth</label>
                                <input v-model="managedForm.date_of_birth" type="date" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-slate-900 focus:bg-white focus:border-brand-gold outline-none transition-all">
                            </div>
                             <div>
                                <label class="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Blood Group</label>
                                <select v-model="managedForm.blood_group" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-slate-900 focus:bg-white focus:border-brand-gold outline-none transition-all">
                                    <option>Unknown</option><option>A+</option><option>A-</option><option>B+</option><option>B-</option><option>O+</option><option>O-</option><option>AB+</option><option>AB-</option>
                                </select>
                            </div>
                        </div>

                        <div>
                            <label class="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Occupation / School</label>
                             <input v-model="managedForm.occupation" type="text" placeholder="e.g. Student at Model School" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-slate-900 focus:bg-white focus:border-brand-gold outline-none transition-all">
                         </div>
 
                          <div>
                              <label class="block text-xs font-bold text-slate-500 uppercase mb-2 ml-1">Bio</label>
                              <textarea v-model="managedForm.bio" rows="2" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3 text-slate-900 focus:bg-white focus:border-brand-gold outline-none transition-all resize-none"></textarea>
                         </div>
                         
                         <div class="pt-6 flex gap-3">
                             <button @click="managedModal = false" type="button" class="flex-1 px-8 py-3.5 rounded-2xl font-bold text-slate-600 hover:bg-slate-50 transition-all border border-slate-200">Cancel</button>
                             <button type="submit" :disabled="loading" class="flex-1 bg-brand-gold hover:brightness-110 text-white px-8 py-3.5 rounded-2xl font-bold shadow-lg shadow-brand-gold/20 transition-all active:scale-95 disabled:opacity-50">
                                 {{ editingManagedId ? 'Update Member' : 'Add Member' }}
                             </button>
                        </div>
                    </form>
                </div>
            </div>
        </div>
      </Teleport>
    </ClientOnly>
  </div>

  <!-- CROPPER MODAL -->
  <ClientOnly>
    <Teleport to="body">
      <div v-if="showCropper" class="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
          <div class="bg-white rounded-3xl overflow-hidden w-full max-w-lg shadow-2xl animate-fade-up">
              <div class="p-4 border-b border-gray-100 flex justify-between items-center bg-slate-50">
                  <h3 class="font-bold text-slate-800">Adjust Photo</h3>
                  <button @click="cancelCrop" class="text-slate-400 hover:text-slate-600">
                      <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                  </button>
              </div>
              
              <div class="p-4 bg-slate-900 flex justify-center">
                  <Cropper
                      ref="cropperRef"
                      class="h-96 w-full"
                      :src="tempImage"
                      :stencil-component="CircleStencil"
                      :stencil-props="{
                          aspectRatio: 1/1,
                      }"
                  />
              </div>

              <div class="p-4 flex gap-3 justify-end bg-white border-t border-gray-100">
                   <button @click="cancelCrop" class="px-6 py-2.5 rounded-xl font-bold text-slate-600 hover:bg-slate-100 transition-colors">Cancel</button>
                   <button @click="cropImage" class="px-6 py-2.5 rounded-xl font-bold text-white bg-brand-gold hover:brightness-110 shadow-lg shadow-brand-gold/30 transition-all active:scale-95">Set Profile Photo</button>
              </div>
          </div>
      </div>
    </Teleport>
  </ClientOnly>
</template>

<script setup>

import { useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import { useRuntimeConfig } from '#imports'
import { Cropper, CircleStencil } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'

const router = useRouter()
const auth = useAuthStore()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'

const step = ref(1)
const loading = ref(false)
const form = ref({
    first_name: '',
    last_name: '',
    nickname: '',
    gender: 'M',
    date_of_birth: '',
    bio: '',
    blood_group: 'Unknown',
    occupation: '',
    education: '',
    email_id: '',
    phone_no: '',
    address: '',
    place_of_work: '',
    church_parish: '',
    parents: [],
    avatar: null 
})

// Managed Members State
const managedMembers = ref([])
const managedModal = ref(false)
const editingManagedId = ref(null)
const managedForm = ref({
    first_name: '',
    last_name: '',
    gender: 'M',
    relation: 'Child',
    date_of_birth: '',
    blood_group: 'Unknown',
    occupation: '',
    bio: '',
    avatar: null
})
const managedAvatarPreview = ref(null)

const resolveImage = (path) => {
    if (!path) return undefined
    if (path.startsWith('http') || path.startsWith('blob:')) return path
    return `${apiBase}${path}`
}

const openAddManaged = () => {
    editingManagedId.value = null
    managedForm.value = {
        first_name: '',
        last_name: '',
        gender: 'M',
        relation: 'Child',
        date_of_birth: '',
        blood_group: 'Unknown',
        occupation: '',
        bio: '',
        avatar: null
    }
    managedAvatarPreview.value = null
    managedModal.value = true
}

const editManagedMember = (m) => {
    editingManagedId.value = m.id
    // Extract first/last name if possible
    let f = '', l = ''
    if (m.name) {
        const parts = m.name.split(' ')
        f = parts[0]
        if (parts.length > 1) l = parts.slice(1).join(' ')
    }
    
    managedForm.value = {
        first_name: f,
        last_name: l,
        gender: m.gender || 'M',
        relation: m.relation || 'Child',
        date_of_birth: m.date_of_birth || '',
        blood_group: m.blood_group || 'Unknown',
        occupation: m.occupation || '',
        bio: m.bio || '',
        avatar: m.photo || m.profile_pic
    }
    managedAvatarPreview.value = resolveImage(m.photo || m.profile_pic)
    managedModal.value = true
}

const onManagedFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
        // Simple upload for managed members
        managedForm.value.avatar = file
        managedAvatarPreview.value = URL.createObjectURL(file)
    }
}

const fetchManagedMembers = async () => {
    try {
        const res = await fetch(`${apiBase}/api/families/managed/`, { credentials: 'include' })
        if (res.ok) {
            managedMembers.value = await res.json()
        }
    } catch (e) {
        console.error("Failed to fetch managed members", e)
    }
}

const saveManagedMember = async () => {
    loading.value = true
    try {
        await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
        const csrftoken = getCookie('csrftoken')

        const formData = new FormData()
        Object.keys(managedForm.value).forEach(key => {
            if (key !== 'avatar' && managedForm.value[key] !== null) {
                formData.append(key, managedForm.value[key])
            }
        })
        
        if (managedForm.value.avatar instanceof File) {
            formData.append('profile_pic', managedForm.value.avatar)
        }

        const url = editingManagedId.value 
            ? `${apiBase}/api/families/managed/${editingManagedId.value}/`
            : `${apiBase}/api/families/managed/`
        
        const res = await fetch(url, {
            method: editingManagedId.value ? 'PUT' : 'POST',
            headers: {
                ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
            },
            body: formData,
            credentials: 'include'
        })

        if (res.ok) {
            await fetchManagedMembers()
            managedModal.value = false
        } else {
            const err = await res.json()
            alert('Failed to save member: ' + (err.error || 'Unknown error'))
        }
    } catch (e) {
        console.error(e)
        alert('Error saving managed member')
    } finally {
        loading.value = false
    }
}

const confirmDeleteManaged = async (m) => {
    if (confirm(`Are you sure you want to delete ${m.name}?`)) {
        try {
            await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
            const csrftoken = getCookie('csrftoken')
            const res = await fetch(`${apiBase}/api/families/managed/${m.id}/`, {
                method: 'DELETE',
                headers: {
                    ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
                },
                credentials: 'include'
            })
            if (res.ok) {
                await fetchManagedMembers()
            }
        } catch (e) {
            console.error(e)
        }
    }
}
const allMembers = ref([])
const parentSearch = ref('')
const filteredPotentialParents = computed(() => {
    if (!parentSearch.value) return []
    const q = parentSearch.value.toLowerCase()
    return allMembers.value.filter(m => 
        m.name.toLowerCase().includes(q) && 
        !form.value.parents.includes(m.id)
    ).slice(0, 5)
})

const addParent = (m) => {
    if (!form.value.parents.includes(m.id)) {
        form.value.parents.push(m.id)
    }
    parentSearch.value = ''
}

const removeParent = (id) => {
    form.value.parents = form.value.parents.filter(p => p !== id)
}

const getMemberName = (id) => {
    return allMembers.value.find(m => m.id === id)?.name || 'Unknown'
}
const avatarPreview = ref(null)

// Cropper State
const showCropper = ref(false)
const tempImage = ref(null)
const cropperRef = ref(null)

onMounted(async () => {
    // 1. Try to fetch fresh profile data from backend
    let profileData = null
    try {
        const res = await fetch(`${apiBase}/api/families/profile/`, {
             headers: {
                 //'Authorization': ... // cookie based
             },
             credentials: 'include'
        })
        if (res.ok) {
            profileData = await res.json()
        }
    } catch (e) {
        console.error("Failed to fetch fresh profile", e)
    }

    // 3. Fetch all members for parent selection
    try {
        const res = await fetch(`${apiBase}/api/families/tree/`)
        if (res.ok) {
            const data = await res.json()
            allMembers.value = data.nodes || []
        }
    } catch (e) {
        console.error("Failed to fetch tree nodes", e)
    }

    // 2. Fallback to auth store
    const u = profileData || auth.user
    
    if (u) {
        form.value.first_name = u.first_name || ''
        form.value.last_name = u.last_name || ''
        if (!form.value.first_name && u.name) {
             const parts = u.name.split(' ')
             form.value.first_name = parts[0]
             if (parts.length > 1) form.value.last_name = parts.slice(1).join(' ')
        }

        form.value.nickname = u.nickname || ''
        form.value.gender = u.gender || 'M'
        form.value.date_of_birth = u.date_of_birth || ''
        form.value.bio = u.bio || ''
        form.value.blood_group = u.blood_group || 'Unknown'
        form.value.occupation = u.occupation || ''
        form.value.education = u.education || ''
        form.value.email_id = u.email_id || u.email || ''
        form.value.phone_no = u.phone_no || ''
        form.value.address = u.address || ''
        form.value.place_of_work = u.place_of_work || ''
        form.value.church_parish = u.church_parish || ''
        
        // Avatar preview
        if (u.profile_pic) {
            const url = u.profile_pic.startsWith('http') ? u.profile_pic : `${apiBase}${u.profile_pic}`
            form.value.avatar = url
            avatarPreview.value = url
        } else if (u.photo) {
             avatarPreview.value = u.photo
        }
    }

    // 4. Fetch managed members
    await fetchManagedMembers()
})

const onFileChange = (e) => {
    const file = e.target.files[0]
    if (file) {
        // Create URL for the file to show in cropper
        if (tempImage.value) {
            URL.revokeObjectURL(tempImage.value)
        }
        tempImage.value = URL.createObjectURL(file)
        showCropper.value = true
        
        // Reset input so same file can be selected again if needed
        e.target.value = '' 
    }
}

const cropImage = () => {
    if (!cropperRef.value) {
        console.error("Cropper reference is messing")
        return
    }
    const result = cropperRef.value.getResult()
    console.log("Cropper Result:", result)
    
    if (result && result.canvas) {
        result.canvas.toBlob((blob) => {
            if (!blob) {
                console.error("Failed to create blob")
                return
            }
            // Create a File from the Blob to simulate a real file upload
            const file = new File([blob], "profile_pic.jpg", { type: "image/jpeg" })
            form.value.avatar = file
            avatarPreview.value = URL.createObjectURL(file)
            console.log("Avatar updated:", file)
            
            // Close modal
            showCropper.value = false
        }, 'image/jpeg')
    } else {
        console.error("No canvas in result. Is the image loaded?")
    }
}

const cancelCrop = () => {
    showCropper.value = false
    tempImage.value = null
}

// Helper to get cookies for CSRF
function getCookie(name) {
    if (typeof document === 'undefined') return null
    const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
    return matches ? matches[2] : null
}

const saveProfile = async () => {
    loading.value = true
    try {
        // Fetch CSRF token first
        await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
        const csrftoken = getCookie('csrftoken')

        const formData = new FormData()
        // Append all fields
        Object.keys(form.value).forEach(key => {
            if (key !== 'avatar' && form.value[key] !== null) {
                formData.append(key, form.value[key])
            }
        })
        // Append parents as individual entries or comma separated
        if (form.value.parents.length > 0) {
            form.value.parents.forEach(pid => {
                formData.append('parents', pid)
            })
        }
        
        // Append avatar if it's a File (not string URL)
        if (form.value.avatar instanceof File) {
             formData.append('profile_pic', form.value.avatar)
        }

        const res = await fetch(`${apiBase}/api/families/profile/`, {
            method: 'POST',
            headers: {
                ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
            },
            body: formData,
            credentials: 'include'
        })
        
        if (res.ok) {
            const updated = await res.json()
            // Update local auth store with new basics
            auth.updateProfile({ 
                first_name: updated.first_name || '',
                last_name: updated.last_name || '',
                name: updated.name || `${updated.first_name} ${updated.last_name}`,
                profile_pic: updated.profile_pic
            })
            step.value = 3 // Go to managed members step
        } else {
            const errData = await res.json().catch(() => ({}))
            console.error("Save failed:", errData)
            alert(`Failed to save profile: ${errData.error || 'Please try again.'}`)
        }
    } catch (e) {
        console.error(e)
        alert('Error saving profile: ' + e.message)
    } finally {
        loading.value = false
    }
}
</script>

<style scoped>
@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}
.animate-fade-in {
    animation: fadeIn 0.4s ease-out forwards;
}
</style>
