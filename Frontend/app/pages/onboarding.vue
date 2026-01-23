<template>
  <div class="min-h-screen bg-[#F5F5F7] text-slate-900 pt-32 pb-16 px-4 flex flex-col items-center font-sans">
    
    <div class="max-w-3xl w-full">
        <!-- Progress Steps -->
        <div class="flex items-center justify-center mb-10 gap-4">
             <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-300', step >= 1 ? 'bg-slate-900 text-white shadow-lg scale-110' : 'bg-white text-slate-400 border border-slate-200']">1</div>
             <div class="h-0.5 w-12 bg-slate-200"></div>
             <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-xs font-semibold transition-all duration-300', step >= 2 ? 'bg-slate-900 text-white shadow-lg scale-110' : 'bg-white text-slate-400 border border-slate-200']">2</div>
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
                               <div class="absolute bottom-2 right-2 bg-slate-900 text-white rounded-full p-2.5 shadow-lg z-10 pointer-events-none group-hover:bg-blue-600 transition-colors">
                                   <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.572L16.732 3.732z"></path></svg>
                               </div>
                            </div>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">First Name</label>
                                <input v-model="form.first_name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400" placeholder="John">
                            </div>
                            <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Last Name</label>
                                <input v-model="form.last_name" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400" placeholder="Doe">
                            </div>
                        </div>

                         <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                            <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Nickname</label>
                                <input v-model="form.nickname" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400" placeholder="Johnny">
                            </div>
                             <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Gender</label>
                                <select v-model="form.gender" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all appearance-none cursor-pointer">
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
                                    <select v-model="form.blood_group" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all appearance-none cursor-pointer">
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
                                <input v-model="form.place_of_work" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400" placeholder="TechPark, Kochi">
                            </div>
                         </div>

                         <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                             <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Education</label>
                                <input v-model="form.education" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400" placeholder="B.Tech Computer Science">
                            </div>
                             <div class="group">
                                <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Parish / Church</label>
                                <input v-model="form.church_parish" type="text" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-blue-500 focus:ring-4 focus:ring-blue-500/10 outline-none transition-all placeholder:text-slate-400" placeholder="St. Mary's Forane Church">
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

                        <button v-if="step < 2" type="button" @click="step++" class="bg-slate-900 hover:bg-black text-white px-8 py-3.5 rounded-2xl font-bold shadow-lg shadow-slate-900/20 transition-all hover:scale-[1.02] active:scale-95 flex items-center gap-2">
                            Next Step
                            <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                        </button>
                        <button v-else type="submit" :disabled="loading" class="bg-blue-600 hover:bg-blue-700 text-white px-8 py-3.5 rounded-2xl font-bold shadow-lg shadow-blue-600/30 transition-all hover:scale-[1.02] active:scale-95 disabled:opacity-50 disabled:cursor-not-allowed">
                            {{ loading ? 'Saving Changes...' : 'Save Profile' }}
                        </button>
                    </div>

                </form>
            </div>
        </div>
    </div>
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
                  <button @click="cropImage" class="px-6 py-2.5 rounded-xl font-bold text-white bg-blue-600 hover:bg-blue-700 shadow-lg shadow-blue-500/30 transition-all active:scale-95">Set Profile Photo</button>
              </div>
          </div>
      </div>
    </Teleport>
  </ClientOnly>
</template>

<script setup>
import { ref, onMounted } from 'vue'
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
    avatar: null 
})
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
             form.value.avatar = u.photo
             avatarPreview.value = u.photo
        }
    }
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

const saveProfile = async () => {
    loading.value = true
    try {
        const formData = new FormData()
        // Append all fields
        Object.keys(form.value).forEach(key => {
            if (key !== 'avatar' && form.value[key] !== null) {
                formData.append(key, form.value[key])
            }
        })
        // Append avatar if it's a File (not string URL)
        if (form.value.avatar instanceof File) {
             formData.append('profile_pic', form.value.avatar)
        }

        const res = await fetch(`${apiBase}/api/families/profile/`, {
            method: 'POST',
            body: formData,
            credentials: 'include'
        })
        
        if (res.ok) {
            const updated = await res.json()
            // Update local auth store with new basics
            auth.updateProfile({ 
                first_name: updated.first_name,
                last_name: updated.last_name,
                name: `${updated.first_name} ${updated.last_name}`,
            })
            router.push('/familytree')
        } else {
            alert('Failed to save profile. Please try again.')
        }
    } catch (e) {
        console.error(e)
        alert('Error saving profile')
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
