<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

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
const error = ref('')

const menuOpen = ref(false)

// Check for referral link
onMounted(() => {
  if (route.query.ref) {
      sponsorId.value = route.query.ref as string
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
  // Check for various photo fields
  return u?.photo || u?.image || u?.profile_pic || ''
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

const copyInvite = () => {
    menuOpen.value = false
    const u = auth.user as any
    if (u && u.member_id) {
        const link = `${window.location.origin}/?ref=${u.member_id}`
        navigator.clipboard.writeText(link)
        alert('Invite link copied to clipboard!')
    } else {
        alert('Member ID not found.')
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
  formData.append('sponsor_id', sponsorId.value)
  formData.append('password', regPassword.value)
  if (regAvatar.value) {
      formData.append('avatar', regAvatar.value)
  }

  const signupResult = await (auth as any).signup(formData)

  if (!signupResult || !signupResult.ok) {
    const msg = (signupResult && signupResult.error && signupResult.error.error) || 'Signup failed'
    error.value = typeof msg === 'string' ? msg : 'Signup failed'
    return
  }

  // Success 
  close()
  router.push('/onboarding')
}

defineExpose({ toggle })
</script>

<template>
  <!-- LOGIN / AVATAR (keeps yellow bar) -->
  <div class="z-20 h-15 w-full lg:w-40 flex items-center
           transition-all duration-500 max-lg:rounded-4xl
           lg:rounded-br-[80px] lg:rounded-tr-[10px]"
       style="background: linear-gradient(to bottom, #A08050, #6d5030);">
    <div class="w-full">
      <div v-if="!auth.isAuthenticated">
        <button
          @click="toggle"
          class="w-full lg:pl-10 font-bold text-white py-3
                 transition lg:rounded-br-[80px] lg:rounded-tr-[10px] lg:hover:rounded-br-[100px] lg:hover:rounded-tr-[10px] hover:brightness-110 active:scale-95"
        >
          Login
        </button>
      </div>

      <div v-else class="flex items-center justify-end pr-4 w-full h-full">
        <div class="relative flex items-center gap-3">
          <!-- Name (Visible on Mobile, Hidden on Desktop to keep pill shape clean) -->
          <span class="text-white font-bold text-sm md:text-base lg:hidden drop-shadow-md">{{ displayName }}</span>

          <button @click="menuOpen = !menuOpen" class="h-10 w-10 rounded-full bg-[#1A3C3B] border-2 border-white/20 text-white flex items-center justify-center font-bold overflow-hidden shrink-0 shadow-md transition-transform active:scale-95">
             <img v-if="userPhoto" :src="userPhoto" alt="User" class="w-full h-full object-cover" />
             <span v-else>{{ initials }}</span>
          </button>

          <div v-if="menuOpen" class="absolute z-50 top-12 right-0 w-48 bg-white rounded-lg shadow-xl p-2 text-sm text-gray-800 border border-gray-100 flex flex-col gap-1">
            <div class="px-2 py-1.5 font-bold text-[#1A3C3B] border-b border-gray-100 mb-1 lg:block hidden">{{ displayName }}</div>
            <button @click="copyInvite" class="w-full text-left px-2 py-1.5 hover:bg-slate-100 rounded-md transition-colors text-amber-600 font-bold">Invite Member</button>
            <button @click="openEdit" class="w-full text-left px-2 py-1.5 hover:bg-slate-100 rounded-md transition-colors">Edit profile</button>
            <button @click="logout" class="w-full text-left px-2 py-1.5 hover:bg-slate-100 rounded-md transition-colors text-red-600">Logout</button>
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
        <h2 class="text-xl font-bold mb-4 text-[#1A3C3B]">Login</h2>
        <input
          v-model="email"
          type="email"
          placeholder="Email"
          class="w-full mb-3 px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#A08050]"
        />

        <div class="relative mb-3">
          <input
            v-model="password"
            :type="showPassword ? 'text' : 'password'"
            placeholder="Password"
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#A08050] pr-10"
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
          class="w-full bg-linear-to-b from-[#A08050] to-[#6d5030] py-2 rounded-lg text-white font-bold
                 transition hover:brightness-110 active:scale-95"
        >
          Continue
        </button>

        <div class="mt-4 text-center text-sm">
          <button @click="registering = true" class="text-lime-800 font-medium">Create an account</button>
        </div>
      </template>

      <template v-else>
        <h2 class="text-xl font-bold mb-4 text-lime-800">Create Account</h2>

        <div class="mb-4 text-xs text-gray-500">
           Enter your Sponsor's Member ID to join.
        </div>

        <input v-model="sponsorId" placeholder="Sponsor Member ID" class="w-full mb-3 px-3 py-2 border rounded-lg border-amber-500 bg-amber-50" />
        <input v-model="regName" placeholder="Full name" class="w-full mb-3 px-3 py-2 border rounded-lg" />
        <input v-model="regEmail" placeholder="Email" class="w-full mb-3 px-3 py-2 border rounded-lg" />
        <input v-model="regEmail" placeholder="Email" class="w-full mb-3 px-3 py-2 border rounded-lg" />
        
        <div class="mb-3">
            <label class="block text-xs text-gray-500 mb-1">Profile Photo (Optional)</label>
            <input 
                type="file" 
                @change="(e: any) => regAvatar = e.target.files[0]"
                accept="image/*"
                class="w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-lime-50 file:text-lime-700 hover:file:bg-lime-100"
            />
        </div>
        
        <div class="relative mb-1">
          <input
            v-model="regPassword"
            :type="showRegPassword ? 'text' : 'password'"
            placeholder="Password"
            class="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-[#A08050] pr-10"
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
            <span :class="passwordStrength >= 3 ? 'text-lime-600 font-bold' : 'text-gray-500'">{{ passwordStrengthLabel }}</span>
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
          <button @click.prevent="register" class="flex-1 bg-lime-700 text-white py-2 rounded">Create</button>
          <button @click.prevent="registering = false" class="flex-1 bg-slate-100 py-2 rounded">Cancel</button>
        </div>
      </template>
    </div>
    </Transition>
  </teleport>
</template>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.25s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.scale-fade-enter-active,
.scale-fade-leave-active {
  transition: all 0.3s ease;
}
.scale-fade-enter-from,
.scale-fade-leave-to {
  opacity: 0;
  transform: translate(-50%, -50%) scale(0.95);
}
</style>
