<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import Login from '~/components/Login.vue'
import { useAuthStore } from '~/stores/auth'
// import { useFamilyStore } from '~/stores/family' (removed, no longer used)
import { useLanguage } from '~/composables/useLanguage'

const mobileOpen = ref(false)
const router = useRouter()
const auth = useAuthStore()
const { currentLanguage, setLanguage } = useLanguage()
const loginRef = ref<InstanceType<typeof Login> | null>(null)

const onLanguageChange = (event: Event) => {
  const value = (event.target as HTMLSelectElement).value
  setLanguage(value === 'ml' ? 'ml' : 'en')
}

const displayName = computed(() => auth.user?.name ?? auth.user?.email ?? '')
const initials = computed(() => {
  const n = (displayName.value ?? '').trim()
  if (!n) return ''
  const parts = n.split(/\s+/).filter(Boolean)
  if (parts.length === 0) return ''
  if (parts.length === 1) return (parts[0] ?? '').slice(0, 2).toUpperCase()
  const a = parts[0]?.charAt(0) ?? ''
  const b = parts[parts.length - 1]?.charAt(0) ?? ''
  return (a + b).toUpperCase()
})

const userPhoto = computed(() => {
  const u = auth.user
  if (!u) return ''
  const photo = (u as any).profile_pic || (u as any).photo || (u as any).image || ''
  if (!photo) return ''
  if (photo.startsWith('http') || photo.startsWith('data:') || photo.startsWith('blob:')) return photo
  const config = useRuntimeConfig()
  const apiBase = (config.public.apiBase as string) || 'http://localhost:8000'
  return `${apiBase}/${photo.replace(/^\/+/, '')}`
})

const resolvePhoto = (path: string) => {
  if (!path) return ''
  if (path.startsWith('http') || path.startsWith('data:') || path.startsWith('blob:')) return path
  const config = useRuntimeConfig()
  const apiBase = (config.public.apiBase as string) || 'http://localhost:8000'
  return `${apiBase}/${path.replace(/^\/+/, '')}`
}

interface NavLink {
  name: string
  to: string
  primary?: boolean
}

const links: NavLink[] = [
  { name: 'Family Tree', to: '/familytree', primary: true },
  { name: 'Gallery', to: '/gallery', primary: true },
  { name: 'Family History', to: '/history', primary: true },
  { name: 'Committee Members', to: '/committee', primary: true },
  { name: 'Donate', to: '/donate', primary: false },
  { name: 'Contact', to: '/contact', primary: false },
]

const restrictedPaths = new Set(['/gallery', '/familytree'])
const visibleLinks = computed(() => links.filter((l) => !restrictedPaths.has(l.to) || auth.isAuthenticated))

// Desktop navigation: primary links are always displayed when permitted
const desktopPrimaryLinks = computed(() => {
  return links.filter((l) => l.primary && (!restrictedPaths.has(l.to) || auth.isAuthenticated))
})

// Desktop navigation: secondary links (Donate, Contact)
const desktopSecondaryLinks = computed(() => {
  return links.filter((l) => !l.primary && (!restrictedPaths.has(l.to) || auth.isAuthenticated))
})

// Hover state to reveal secondary links when logged in
const isNavbarHovered = ref(false)
let hoverTimeout: ReturnType<typeof setTimeout> | null = null

const onNavMouseEnter = () => {
  if (hoverTimeout) {
    clearTimeout(hoverTimeout)
    hoverTimeout = null
  }
  isNavbarHovered.value = true
}

const onNavMouseLeave = () => {
  if (hoverTimeout) clearTimeout(hoverTimeout)
  hoverTimeout = setTimeout(() => {
    isNavbarHovered.value = false
  }, 250)
}

// Mobile menu actions
const mobileLogin = () => {
  mobileOpen.value = false
  loginRef.value?.toggle()
}
const mobileLogout = async () => {
  mobileOpen.value = false
  await (auth as any).logout()
  router.push('/')
}
const mobileNav = (path: string) => {
  mobileOpen.value = false
  router.push(path)
}

function getCookie(name: string) {
  if (typeof document === 'undefined') return null
  const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
  return matches ? matches[2] : null
}

const mobileCopyInvite = async () => {
  mobileOpen.value = false
  try {
    const config = useRuntimeConfig()
    const apiBase = (config.public.apiBase as string) || 'http://localhost:8000'
    await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
    const csrftoken = getCookie('csrftoken')
    const res = await fetch(`${apiBase}/api/auth/generate-invite-token/`, {
      method: 'POST',
      headers: { ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}) },
      credentials: 'include'
    })
    if (res.ok) {
      const data = await res.json()
      const link = `${window.location.origin}/?token=${data.token}`
      await navigator.clipboard.writeText(`Hey! Join our family directory here: ${link}`)
      alert('Invite link copied to clipboard!')
    } else {
      const err = await res.json().catch(() => ({}))
      alert(err.error || 'Failed to generate invite token.')
    }
  } catch (e) {
    alert('Error generating invite.')
  }
}

// --- Auto-hide Navbar Logic ---
const showNavbar = ref(true)
const lastScrollY = ref(0)
const handleScroll = () => {
    const currentScrollY = window.scrollY
    if (currentScrollY < lastScrollY.value || currentScrollY < 50) {
        showNavbar.value = true
    } else {
        showNavbar.value = false
    }
    lastScrollY.value = currentScrollY
}

onMounted(() => {
  window.addEventListener('scroll', handleScroll)
  lastScrollY.value = window.scrollY
})

onUnmounted(() => {
    window.removeEventListener('scroll', handleScroll)
    if (hoverTimeout) clearTimeout(hoverTimeout)
})
</script>

<template>
  <!-- NAVBAR -->
  <nav 
    class="fixed top-0 left-0 w-full lg:w-200 z-50 bg-transparent transition-transform duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]"
    :class="[ showNavbar ? 'translate-y-0' : '-translate-y-full' ]"
    @mouseenter="onNavMouseEnter"
    @mouseleave="onNavMouseLeave"
  >
      <!-- Desktop Navbar -->
      <div class="hidden bg-white lg:flex lg:rounded-br-[80px] lg:rounded-tr-[10px] lg:hover:rounded-br-[100px] lg:hover:rounded-tr-[10px] px-4 items-center relative h-15 shadow-sm transition-all duration-500 ease-[cubic-bezier(0.16,1,0.3,1)]">
        <div class="flex items-center gap-4 h-full">
          <NuxtLink to="/" class="flex font-fleur text-2xl items-center text-right h-full shrink-0">
           Kollamparampil<br>Family
         </NuxtLink>
          <div class="flex absolute items-center right-5 gap-1">
            <!-- Primary Links (Always visible on desktop) -->
            <NuxtLink
              v-for="link in desktopPrimaryLinks"
              :key="link.to"
              :to="link.to"
              class="py-2 px-2 rounded-md text-sm font-bold text-slate-800 hover:bg-slate-50 hover:text-brand-gold hover:shadow-sm transition-all duration-300 active:scale-95 whitespace-nowrap"
            >
              {{ link.name }}
            </NuxtLink>

            <!-- For Guests (Logged Out): Donate and Contact are visible in the top row -->
            <template v-if="!auth.isAuthenticated">
              <NuxtLink
                v-for="link in desktopSecondaryLinks"
                :key="link.to"
                :to="link.to"
                class="py-2 px-2 rounded-md text-sm font-bold text-slate-800 hover:bg-slate-50 hover:text-brand-gold hover:shadow-sm transition-all duration-300 active:scale-95 whitespace-nowrap"
              >
                {{ link.name }}
              </NuxtLink>
            </template>

            <!-- Downward indicator chevron & seamless dropdown when logged in -->
            <div v-if="auth.isAuthenticated" class="relative flex items-center">
              <div 
                class="px-1 py-2 text-slate-400 hover:text-brand-gold transition-colors flex items-center cursor-pointer"
                title="More options"
              >
                <svg 
                  class="w-3.5 h-3.5 transition-transform duration-300 ease-out"
                  :class="isNavbarHovered ? 'rotate-180 text-brand-gold' : ''"
                  fill="none" 
                  stroke="currentColor" 
                  viewBox="0 0 24 24"
                >
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M19 9l-7 7-7-7" />
                </svg>
              </div>

              <!-- Seamless Dropdown Menu for secondary options (Donate, Contact) -->
              <div
                class="absolute top-full right-0 min-w-36 bg-white rounded-b-2xl rounded-t-none shadow-2xl border-x border-b border-slate-100/90 p-1.5 flex flex-col gap-0.5 z-50 transition-all duration-300 ease-[cubic-bezier(0.16,1,0.3,1)] origin-top-right overflow-hidden"
                :class="[
                  isNavbarHovered 
                    ? 'opacity-100 translate-y-0 max-h-40 pointer-events-auto scale-100' 
                    : 'opacity-0 -translate-y-2 max-h-0 pointer-events-none scale-95'
                ]"
              >
                <NuxtLink
                  v-for="link in desktopSecondaryLinks"
                  :key="link.to"
                  :to="link.to"
                  class="py-2.5 px-4 rounded-xl text-sm font-bold text-slate-700 hover:bg-slate-50 hover:text-brand-gold transition-all duration-200 active:scale-95 whitespace-nowrap"
                >
                  {{ link.name }}
                </NuxtLink>
              </div>
            </div>

            <label class="inline-flex items-center gap-1 rounded-full border border-slate-200 bg-white pl-2 pr-1 py-1 text-slate-600 shadow-sm ml-1 shrink-0">
              <svg class="w-3.5 h-3.5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.8" d="M3 12h18M12 3a15.3 15.3 0 014 9 15.3 15.3 0 01-4 9 15.3 15.3 0 01-4-9 15.3 15.3 0 014-9z" />
              </svg>
              <div class="relative">
                <select
                  :value="currentLanguage"
                  aria-label="Language"
                  class="appearance-none rounded-full border border-slate-200 bg-white pl-2.5 pr-5 py-0.5 font-semibold text-xs w-13 text-slate-700 outline-hidden transition-all duration-300 focus:border-brand-gold focus:ring-2 focus:ring-brand-gold/25"
                  @change="onLanguageChange"
                >
                  <option value="en">EN</option>
                  <option value="ml">മല</option>
                </select>
                <svg class="pointer-events-none absolute right-1.5 top-1/2 -translate-y-1/2 w-2.5 h-2.5 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                </svg>
              </div>
            </label>
          </div>
        </div>
        <div class="flex -z-20 ml-150 items-center gap-3">
          <Login ref="loginRef" />
        </div>

        <!-- Remove Managed Members section from desktop dropdown -->
      </div>

      <!-- Mobile Top Bar -->
      <div 
        class="flex lg:hidden items-center z-30 justify-between h-16 px-4 transition-all duration-300"
        :class="mobileOpen ? 'bg-white shadow-none' : 'bg-white shadow-md'"
      >
        <NuxtLink to="/" class="font-fleur text-[1.7rem] text-slate-800 leading-[0.82]" @click="mobileOpen = false">
          <span class="block">Kollamparampil</span>
          <span class="block -mt-1">Family</span>
        </NuxtLink>

        <button
          @click="mobileOpen = !mobileOpen"
          class="relative flex items-center justify-center h-10 w-10 rounded-full transition-all duration-300"
          :class="mobileOpen ? 'bg-slate-100' : ''"
        >
          <template v-if="auth.isAuthenticated">
              <div 
              class="h-9 w-9 rounded-full overflow-hidden shrink-0 transition-all duration-300"
              :class="mobileOpen ? 'ring-2 ring-brand-gold ring-offset-1' : 'border-2 border-brand-gold/50 shadow-sm'"
            >
              <img v-if="userPhoto" :src="userPhoto" :alt="displayName || 'User photo'" class="w-full h-full object-cover" @error="(e) => (e.target as any).style.display='none'" />
              <div v-else class="w-full h-full bg-brand-gold text-white flex items-center justify-center font-bold text-sm">{{ initials }}</div>
            </div>
          </template>
          <template v-else>
            <!-- Animated hamburger / close icon -->
            <div class="flex flex-col justify-center items-center w-6 h-6 gap-1.5">
              <span class="block h-0.5 w-5 bg-slate-700 rounded-full transition-all duration-300 ease-out" :class="mobileOpen ? 'rotate-45 translate-y-2' : ''"></span>
              <span class="block h-0.5 w-5 bg-slate-700 rounded-full transition-all duration-300 ease-out" :class="mobileOpen ? 'opacity-0' : ''"></span>
              <span class="block h-0.5 w-5 bg-slate-700 rounded-full transition-all duration-300 ease-out" :class="mobileOpen ? '-rotate-45 -translate-y-2' : ''"></span>
            </div>
          </template>
        </button>
      </div>

    <!-- MOBILE MENU BACKDROP -->
    <Transition name="fade-backdrop">
      <div
        v-if="mobileOpen"
        class="lg:hidden fixed top-0 left-0 w-screen h-[100dvh] z-30"
        @click="mobileOpen = false"
      />
    </Transition>

    <!-- MOBILE MENU — fully inlined, no nested dropdowns -->
    <Transition name="slide">
      <div
        v-if="mobileOpen"
        class="lg:hidden fixed inset-x-0 top-15 z-40 bg-white/95 shadow-2xl flex flex-col rounded-b-3xl border-b border-slate-100 max-h-[calc(100vh-80px)] overflow-y-auto"
      >
        <!-- Nav Links -->
        <div class="flex flex-col px-4 pt-3 pb-1">
          <NuxtLink
            v-for="link in visibleLinks"
            :key="link.to"
            :to="link.to"
            @click="mobileOpen = false"
            class="flex items-center gap-3 px-3 py-2.5 rounded-xl font-semibold text-sm md:text-base text-slate-700 hover:bg-slate-50 hover:text-brand-gold active:bg-slate-100 transition-all duration-300"
          >
            <span class="w-1.5 h-1.5 rounded-full bg-brand-gold/40 shrink-0"></span>
            {{ link.name }}
          </NuxtLink>
        </div>

        <div class="px-4 pb-3">
          <label class="flex items-center justify-between rounded-xl border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-700">
              <span class="uppercase tracking-wide text-slate-500">Language</span>
            <div class="relative">
              <select
                :value="currentLanguage"
                aria-label="Language"
                class="appearance-none rounded-full border border-slate-200 bg-white pl-2.5 pr-6 py-1 text-xs font-semibold text-slate-700 outline-hidden transition-all duration-300 focus:border-brand-gold focus:ring-2 focus:ring-brand-gold/25"
                @change="onLanguageChange"
              >
                <option value="en">EN</option>
                <option value="ml">മല</option>
              </select>
              <svg class="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 w-3 h-3 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </div>
          </label>
        </div>

        <div class="mx-5 border-t border-slate-100"></div>

        <!-- LOGGED IN: Inline profile section -->
        <div v-if="auth.isAuthenticated" class="px-4 py-3 flex flex-col gap-0.5">
          <!-- User Info -->
          <div class="flex items-center gap-3 px-3 py-2 mb-1">
              <div class="w-9 h-9 rounded-full bg-brand-gold text-white flex items-center justify-center text-sm font-bold overflow-hidden shrink-0 border-2 border-brand-gold/30">
              <img v-if="userPhoto" :src="userPhoto" :alt="displayName || 'User photo'" class="w-full h-full object-cover" @error="(e: any) => e.target.style.display='none'" />
              <span v-else>{{ initials }}</span>
            </div>
            <div class="flex flex-col flex-1 min-w-0">
              <span class="font-bold text-slate-800 text-sm truncate">{{ displayName }}</span>
              <span class="text-xs text-slate-400">Logged in</span>
            </div>
          </div>

          <!-- Quick Actions -->
          <button @click="mobileCopyInvite" class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-brand-gold hover:bg-brand-gold/5 active:bg-brand-gold/10 transition-all duration-300">
            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"></path></svg>
            Invite Member
          </button>
          <button @click="mobileNav('/familytree?view=visual&edit=1')" class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 active:bg-slate-100 transition-all duration-300">
            <svg class="w-4 h-4 text-brand-gold shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"></path></svg>
            Add Family Member
          </button>
          <button @click="mobileNav('/onboarding')" class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-slate-700 hover:bg-slate-50 active:bg-slate-100 transition-all duration-300">
            <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"></path></svg>
            Edit Profile
          </button>


          <!-- Logout -->
          <div class="mt-1 pt-2 border-t border-slate-100">
            <button @click="mobileLogout" class="flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-semibold text-red-500 hover:bg-red-50 active:bg-red-100 transition-all duration-300 w-full">
              <svg class="w-4 h-4 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1"></path></svg>
              Logout
            </button>
          </div>
        </div>

        <!-- NOT LOGGED IN: Simple login button -->
        <div v-else class="px-5 py-4">
          <button 
            @click="mobileLogin"
            class="w-full py-3 rounded-2xl font-bold text-white text-sm bg-linear-to-b from-brand-gold to-brand-gold-dark shadow-lg hover:brightness-110 active:scale-95 transition-all duration-300"
          >
            Login
          </button>
        </div>
      </div>
    </Transition>
  </nav>
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.4s cubic-bezier(0.16, 1, 0.3, 1), opacity 0.28s ease;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateY(-20px);
  opacity: 0;
}
.fade-backdrop-enter-active,
.fade-backdrop-leave-active {
  transition: opacity 0.32s ease;
}
.fade-backdrop-enter-from,
.fade-backdrop-leave-to {
  opacity: 0;
}
</style>
