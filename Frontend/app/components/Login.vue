<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '~/stores/auth'
import { Cropper, CircleStencil } from 'vue-advanced-cropper'
import 'vue-advanced-cropper/dist/style.css'
import 'vue-advanced-cropper/dist/theme.classic.css'

const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const open = ref(false)
const email = ref('')
const password = ref('')
const sponsorId = ref('')
const showPassword = ref(false)

const registering = ref(false)
const regName = ref('')
const regEmail = ref('')
const regPassword = ref('')
const showRegPassword = ref(false)
const regAvatar = ref<File | null>(null)
const avatarSrc = ref<string | null>(null)
const croppingAvatar = ref(false)
const cropper = ref<any>(null)
const error = ref('')

const menuOpen = ref(false)

// Check for referral link
onMounted(async () => {
  // Always refresh profile to pick up managed_members if they were added
  if (auth.isAuthenticated) {
      await auth.fetchProfile()
  }
  
  if (route.query.login) {
      open.value = true
  }
  if (route.query.register) {
      open.value = true
      registering.value = true
  }
  if (route.query.ref || route.query.token) {
      sponsorId.value = (route.query.token || route.query.ref) as string
      open.value = true
      registering.value = true
  }
})

const displayName = computed<string>(() => {
  const u = auth.user as { name?: string; email?: string } | null
  return (u?.name ?? u?.email) ?? ''
})

const initials = computed<string>(() => {
  const n = (displayName.value ?? '').trim()
  if (!n) return ''
  const parts = n.split(/\s+/).filter(Boolean)
  if (parts.length === 0) return ''
  if (parts.length === 1) return (parts[0] ?? '').slice(0, 2).toUpperCase()
  const a = parts[0]?.charAt(0) ?? ''
  const b = parts[parts.length - 1]?.charAt(0) ?? ''
  return (a + b).toUpperCase()
})

const passwordStrength = computed(() => {
  const p = regPassword.value
  let score = 0
  if (!p) return 0
  if (p.length > 7) score++
  if (/[A-Z]/.test(p)) score++
  if (/[0-9]/.test(p)) score++
  if (/[^A-Za-z0-9]/.test(p)) score++
  return score
})

const passwordStrengthColor = computed(() => {
  const s = passwordStrength.value
  if (s <= 1) return 'bg-red-500'
  if (s === 2) return 'bg-orange-500'
  if (s === 3) return 'bg-yellow-500'
  return 'bg-lime-500'
})

const passwordStrengthLabel = computed(() => {
  const s = passwordStrength.value
  if (s === 0) return ''
  if (s <= 1) return 'Weak'
  if (s === 2) return 'Fair'
  if (s === 3) return 'Good'
  return 'Strong'
})

const userPhoto = computed<string>(() => {
  const u = auth.user as any
  // Potential field names: profile_pic (from serializer), photo, image, picture
  const photo = u?.profile_pic || u?.photo || u?.image || u?.picture || ''
  if (!photo) return ''
  
  // If it's already a full URL or base64/blob, return it
  if (photo.startsWith('http') || photo.startsWith('data:') || photo.startsWith('blob:')) {
      return photo
  }
  
  // Prepend apiBase if it's a relative path
  const config = useRuntimeConfig()
  const apiBase = (config.public.apiBase as string) || 'http://localhost:8000'
  
  // Clean potential starting slashes to avoid double slashes with apiBase
  const cleanPath = photo.replace(/^\/+/, '')
  return `${apiBase}/${cleanPath}`
})

const toggle = () => (open.value = !open.value)
const close = () => {
  open.value = false
  error.value = ''
  registering.value = false
}

const submit = async () => {
  error.value = ''
  const res: any = await (auth as any).login(email.value, password.value)
  if (res && res.ok) {
    close()
  } else {
    const msg = (res && res.error) || 'Invalid email or password'
    error.value = typeof msg === 'string' ? msg : 'Invalid email or password'
  }
}

const logout = async () => {
  await (auth as any).logout()
  menuOpen.value = false
  router.push('/')
}

const openEdit = () => {
  menuOpen.value = false
  router.push('/onboarding')
}

function getCookie(name: string) {
  if (typeof document === 'undefined') return null
  const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
  return matches ? matches[2] : null
}

const copyInvite = async () => {
    menuOpen.value = false
    try {
        const config = useRuntimeConfig()
        const apiBase = (config.public.apiBase as string) || 'http://localhost:8000'
        
        // Get CSRF Token
        await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
        const csrftoken = getCookie('csrftoken')

        const res = await fetch(`${apiBase}/api/auth/generate-invite-token/`, {
            method: 'POST',
            headers: {
                ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {})
            },
            credentials: 'include'
        })

        if (res.ok) {
            const data = await res.json()
            const link = `${window.location.origin}/?token=${data.token}`
            const message = `Hey! Join our family directory here: ${link}`
            await navigator.clipboard.writeText(message)
            alert('Invite link and message copied to clipboard! You can now paste it directly into WhatsApp.')
        } else {
            alert('Failed to generate invite token. Please make sure your profile is completed.')
        }
    } catch (e) {
        console.error("Invite generation failed", e)
        alert('Error generating invite.')
    }
}

const register = async () => {
  error.value = ''
  if (!regName.value || !regEmail.value || !regPassword.value || !sponsorId.value) {
    error.value = 'Please fill all fields, including Sponsor ID.'
    return
  }

  const formData = new FormData()
  formData.append('username', regName.value || regEmail.value)
  formData.append('email', regEmail.value)
  formData.append('invite_token', sponsorId.value)
  formData.append('password', regPassword.value)
  if (regAvatar.value) {
      formData.append('avatar', regAvatar.value)
  }

  const signupResult = await (auth as any).signup(formData)

  if (!signupResult || !signupResult.ok) {
    const err = signupResult?.error
    const msg = err?.error || err?.detail || 'Signup failed'
    error.value = typeof msg === 'string' ? msg : 'Signup failed'
    return
  }

  // Success 
  close()
  router.push('/onboarding')
}

const handleAvatarChange = (e: any) => {
  const file = e.target.files[0]
  if (file) {
    const reader = new FileReader()
    reader.onload = (event: any) => {
      avatarSrc.value = event.target.result
      croppingAvatar.value = true
    }
    reader.readAsDataURL(file)
  }
}

const cropImage = () => {
  if (cropper.value) {
    const { canvas } = cropper.value.getResult()
    canvas.toBlob((blob: Blob) => {
      if (blob) {
        regAvatar.value = new File([blob], 'avatar.jpg', { type: 'image/jpeg' })
        croppingAvatar.value = false
        // Update avatarSrc to the cropped version for preview
        avatarSrc.value = URL.createObjectURL(blob)
      }
    }, 'image/jpeg')
  }
}

const cancelCrop = () => {
  croppingAvatar.value = false
  avatarSrc.value = null
  regAvatar.value = null
}

defineExpose({ toggle })
</script>

<template>
  <!-- LOGIN / AVATAR (keeps yellow bar) -->
  <div class="z-20 h-15 w-full lg:w-40 flex items-center
           transition-all duration-500 max-lg:rounded-full
           lg:rounded-br-[80px] lg:rounded-tr-[10px] bg-linear-to-b from-brand-gold to-brand-gold-dark shadow-lg">
    <div class="w-full">
      <div v-if="!auth.isAuthenticated">
        <button
          @click="toggle"
          class="w-full max-w-[280px] mx-auto lg:max-w-none lg:pl-10 font-bold text-white py-3 block
                 transition lg:rounded-br-[80px] lg:rounded-tr-[10px] lg:hover:rounded-br-[100px] lg:hover:rounded-tr-[10px] hover:brightness-110 active:scale-95"
        >
          Login
        </button>
      </div>

      <div v-else class="flex items-center lg:justify-end justify-center lg:pr-10 w-full h-full px-4 lg:px-0">
        <div class="relative flex items-center gap-3">
          <!-- Name (Visible on Mobile, slightly smaller to fit pill) -->
          <span class="text-white font-black text-xs lg:hidden drop-shadow-md truncate max-w-[120px]">{{ displayName }}</span>

          <button @click="menuOpen = !menuOpen" class="h-10 w-10 lg:h-11 lg:w-11 rounded-full bg-brand-gold border-2 border-white/50 text-white flex items-center justify-center font-bold overflow-hidden shrink-0 shadow-lg transition-transform active:scale-95">
             <img v-if="userPhoto" :src="userPhoto" alt="User" class="w-full h-full object-cover" @error="(e) => (e.target as any).style.display='none'" />
             <span v-else>{{ initials }}</span>
          </button>

          <div v-if="menuOpen" class="absolute z-50 top-14 lg:-left-24 left-1/2 lg:translate-x-0 -translate-x-1/2 w-72 bg-white rounded-2xl shadow-2xl p-3 text-sm text-slate-800 border border-slate-100 flex flex-col gap-1.5 animate-fade-in">
            <div class="px-3 py-2 font-black text-brand-gold-dark border-b border-slate-100 mb-2 text-center">{{ displayName }}</div>
            
            <button @click="copyInvite" class="w-full text-left px-3 py-2.5 hover:bg-slate-50 rounded-xl transition-all text-brand-gold font-bold flex items-center gap-2">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
                Invite Member
            </button>

            <button @click="router.push('/onboarding?step=3'); menuOpen = false" class="w-full text-left px-3 py-2.5 hover:bg-slate-50 rounded-xl transition-all flex items-center gap-2 font-semibold">
                <svg class="w-4 h-4 text-brand-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
                Add Family Member
            </button>

            <!-- Managed Members Section -->
            <div v-if="auth.isAuthenticated && (auth.user?.managed_members?.length || 0) > 0" class="border-t border-slate-100 mt-2 pt-2">
                <div class="px-3 py-1 text-[10px] font-bold text-slate-400 uppercase tracking-widest mb-1 flex justify-between items-center">
                    <span>Managed Members</span>
                    <span class="bg-slate-100 text-slate-500 px-1.5 rounded-full">{{ auth.user?.managed_members?.length || 0 }}</span>
                </div>
                <div class="max-h-48 overflow-y-auto custom-scrollbar">
                    <button 
                        v-for="m in (auth.user?.managed_members || [])" 
                        :key="m.id"
                        @click="router.push(`/onboarding?step=3&edit=${m.id}`); menuOpen = false"
                        class="w-full text-left px-3 py-2.5 hover:bg-slate-50 rounded-xl transition-all flex items-center gap-3 group"
                    >
                        <div class="w-9 h-9 rounded-xl bg-slate-100 overflow-hidden shrink-0 border border-slate-200 group-hover:border-brand-gold/30 transition-colors">
                            <img v-if="m.profile_pic" :src="m.profile_pic.startsWith('http') ? m.profile_pic : `${useRuntimeConfig().public.apiBase || 'http://localhost:8000'}${m.profile_pic}`" class="w-full h-full object-cover" />
                            <div v-else class="w-full h-full flex items-center justify-center text-slate-400 font-bold text-sm uppercase">{{ m.name.charAt(0) }}</div>
                        </div>
                        <div class="flex flex-col flex-1 truncate">
                            <span class="font-bold text-slate-700 group-hover:text-brand-gold transition-colors truncate">{{ m.name }}</span>
                            <span class="text-[10px] text-slate-400 font-medium">{{ m.relation }}</span>
                        </div>
                        <svg class="w-4 h-4 text-slate-300 group-hover:text-brand-gold transition-colors" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
                    </button>
                </div>
            </div>

            <div class="border-t border-slate-50 mt-1 pt-2">
                <button @click="openEdit" class="w-full text-left px-3 py-2.5 hover:bg-slate-50 rounded-xl transition-all flex items-center gap-2 font-semibold">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
                    Edit profile
                </button>
                <button @click="logout" class="w-full text-left px-3 py-2.5 hover:bg-red-50 rounded-xl transition-all text-red-600 flex items-center gap-2 font-semibold">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
                    Logout
                </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>

  <!-- BACKDROP -->
  <teleport to="body">
    <Transition name="fade">
      <div
        v-if="open"
        @click="close"
        class="fixed inset-0 z-40 bg-black/40 backdrop-blur-sm"
      />
    </Transition>

    <!-- LOGIN MODAL -->
    <Transition name="scale-fade">
      <div v-if="open" class="fixed z-50 top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 bg-white rounded-2xl p-6 w-80 shadow-xl">
      <template v-if="!registering">
        <h2 class="text-xl font-bold mb-4 text-brand-gold">Login</h2>
        <input
          v-model="email"
          type="email"
          placeholder="Email"
          class="w-full mb-3 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-brand-gold"
        />

        <div class="relative mb-3">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Password"
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-brand-gold pr-10"
          />
          <button
            @click.prevent="showPassword = !showPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            type="button"
          >
            <!-- Eye Icon -->
            <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
            <!-- Eye Slash Icon -->
            <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
               <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
            </svg>
          </button>
        </div>

        <div v-if="error" class="text-sm text-red-600 mb-2">{{ error }}</div>

        <button
          @click.prevent="submit"
          class="w-full bg-linear-to-b from-brand-gold to-brand-gold-dark py-2 rounded-lg text-white font-bold
                 transition hover:brightness-110 active:scale-95"
        >
          Continue
        </button>

        <div class="mt-4 text-center text-sm">
          <button @click="registering = true" class="text-brand-gold-dark font-medium">Create an account</button>
        </div>
      </template>

      <template v-else>
        <h2 class="text-xl font-bold mb-4 text-brand-gold">Create Account</h2>

        <div class="mb-4 text-xs text-gray-500">
           Enter your Invite Token to join.
        </div>

        <input v-model="sponsorId" placeholder="Invite Token" class="w-full mb-3 px-3 py-2 border rounded-lg border-brand-gold bg-brand-gold/5" />
        <input v-model="regName" placeholder="Full name" class="w-full mb-3 px-3 py-2 border rounded-lg" />
        <input v-model="regEmail" placeholder="Email" class="w-full mb-3 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-brand-gold" />
        
        <div class="mb-3">
            <label class="block text-xs text-gray-500 mb-1">Profile Photo (Optional)</label>
            
            <div v-if="avatarSrc && !croppingAvatar" class="relative group w-20 h-20 mx-auto mb-2">
                <img :src="avatarSrc" class="w-full h-full object-cover rounded-full border-2 border-brand-gold" />
                <button @click="avatarSrc = null; regAvatar = null" class="absolute -top-1 -right-1 bg-red-500 text-white rounded-full p-1 shadow-sm opacity-0 group-hover:opacity-100 transition-opacity">
                    <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                </button>
            </div>

            <input 
                v-if="!avatarSrc && !croppingAvatar"
                type="file" 
                @change="handleAvatarChange"
                accept="image/*"
                class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-brand-gold/5 file:text-brand-gold hover:file:bg-brand-gold/10"
            />

            <!-- Cropper Overlay moved outside for better stacking -->
        </div>
        
        <div class="relative mb-1">
          <input
            v-model="regPassword"
            :type="showRegPassword ? 'text' : 'password'"
            placeholder="Password"
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-brand-gold pr-10"
          />
          <button
            @click.prevent="showRegPassword = !showRegPassword"
            class="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700"
            type="button"
          >
            <svg v-if="!showRegPassword" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
              <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
              <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
            </svg>
             <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
               <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
            </svg>
          </button>
        </div>

        <!-- Password Strength Meter -->
        <div v-if="regPassword" class="mb-3">
          <div class="flex justify-between text-xs mb-1">
            <span class="text-gray-500">Security</span>
            <span :class="passwordStrength >= 3 ? 'text-brand-gold font-bold' : 'text-gray-500'">{{ passwordStrengthLabel }}</span>
          </div>
          <div class="h-1.5 w-full bg-gray-200 rounded-full overflow-hidden">
             <div 
               class="h-full transition-all duration-300 rounded-full" 
               :class="passwordStrengthColor" 
               :style="{ width: (passwordStrength / 4) * 100 + '%' }"
             ></div>
          </div>
        </div>

        <div v-if="error" class="text-sm text-red-600 mb-2">{{ error }}</div>

        <div class="flex gap-2">
          <button @click.prevent="register" class="flex-1 bg-linear-to-b from-brand-gold to-brand-gold-dark text-white py-2 rounded font-bold hover:brightness-110 active:scale-95 transition-all">Create</button>
          <button @click.prevent="registering = false" class="flex-1 bg-slate-100 py-2 rounded">Cancel</button>
        </div>
      </template>
    </div>
    </Transition>
    <!-- Cropper Overlay (Siblings with modals for best stacking) -->
    <Transition name="fade">
      <div v-if="croppingAvatar" class="fixed inset-0 z-60 bg-black/90 flex flex-col items-center justify-center p-4">
          <div class="w-full max-w-md bg-white rounded-2xl overflow-hidden shadow-2xl flex flex-col max-h-[90vh]">
              <div class="p-4 bg-slate-50 border-b border-slate-200 flex justify-between items-center shrink-0">
                  <span class="font-bold text-slate-800">Crop Profile Photo</span>
                  <button @click="cancelCrop" class="text-slate-400 hover:text-slate-600">
                       <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
                  </button>
              </div>
              <div class="bg-black flex-1 overflow-hidden min-h-[300px]">
                  <Cropper
                      ref="cropper"
                      class="h-full w-full"
                      :src="avatarSrc"
                      :stencil-component="CircleStencil"
                      :stencil-props="{
                          aspectRatio: 1/1
                      }"
                  />
              </div>
              <div class="p-4 flex gap-3 shrink-0">
                  <button @click="cropImage" class="flex-1 bg-brand-gold text-white py-2 rounded-lg font-bold hover:brightness-110 active:scale-95 transition-all">Apply Crop</button>
                  <button @click="cancelCrop" class="flex-1 bg-slate-100 text-slate-600 py-2 rounded-lg font-bold hover:bg-slate-200 active:scale-95 transition-all">Cancel</button>
              </div>
          </div>
      </div>
    </Transition>
  </teleport>
</template>

<style scoped>

</style>
