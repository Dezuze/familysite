<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Login from '~/components/Login.vue'
import { useAuthStore } from '~/stores/auth'

const mobileOpen = ref(false)

const auth = useAuthStore()

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
  
  if (photo.startsWith('http') || photo.startsWith('data:') || photo.startsWith('blob:')) {
      return photo
  }
  
  const config = useRuntimeConfig()
  const apiBase = (config.public.apiBase as string) || 'http://localhost:8000'
  const cleanPath = photo.replace(/^\/+/, '')
  return `${apiBase}/${cleanPath}`
})

const links = [
  { name: 'Family Tree', to: '/familytree' },
  { name: 'Gallery', to: '/gallery' },
  { name: 'Family History', to: '/history' },
  { name: 'Committee Members', to: '/committee' },
  { name: 'Contact', to: '/contact' },
]

const restricted = ['Gallery', 'Family Tree', 'Donation']
const visibleLinks = computed(() => links.filter((l) => !restricted.includes(l.name) || auth.isAuthenticated))

// --- Auto-hide Navbar Logic ---
const showNavbar = ref(true)
const lastScrollY = ref(0)
const handleScroll = () => {
    const currentScrollY = window.scrollY
    
    // Show if scrolling up OR at the very top
    if (currentScrollY < lastScrollY.value || currentScrollY < 50) {
        showNavbar.value = true
    } else {
        // Hide if scrolling down AND not at top
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
})
</script>

<template>
  <!-- NAVBAR -->
  <nav 
    class="fixed top-0 left-0 right-0 w-full lg:w-170 z-50 bg-transparent transition-transform duration-300 ease-in-out"
    :class="[ showNavbar ? 'translate-y-0' : '-translate-y-full' ]"
  >
      <div class="hidden bg-white lg:flex lg:rounded-br-[80px] lg:rounded-tr-[10px] lg:hover:rounded-br-[100px] lg:hover:rounded-tr-[10px] px-4 items-center relative h-15 shadow-sm">
        <div class="flex items-center gap-4 h-full">
          <NuxtLink to="/" class="flex font-fleur text-2xl items-center text-right h-full">
           Kollamparambil<br>Family
        </NuxtLink>
          <div class="flex absolute items-center right-5">
            <NuxtLink
              v-for="link in visibleLinks"
              :key="link.to"
              :to="link.to"
              class="py-2 px-2 rounded-md text-sm font-bold text-slate-800 hover:bg-slate-50 hover:text-brand-gold hover:shadow-sm transition"
            >
              {{ link.name }}
            </NuxtLink>
          </div>
        </div>
        <div class="flex -z-20 ml-120 items-center gap-3">
          <Login />
        </div>
      </div>



      <!-- Mobile -->
      <div class="flex bg-white lg:hidden items-center z-30 justify-between h-15 px-4 shadow-sm border-b border-slate-100">
        <NuxtLink to="/" class="flex font-fleur text-2xl items-center ml-4 text-right h-full">
           Kollamparambil<br>Family
        </NuxtLink>

        <div class="flex items-center gap-2">
          <button
            @click="mobileOpen = !mobileOpen"
            class="flex items-center gap-3 text-base font-semibold text-slate-800 pr-2 py-1 rounded transition h-10 w-10 justify-center"
          >
            <template v-if="auth.isAuthenticated">
              <div v-if="userPhoto" class="h-10 w-10 rounded-full border-2 border-brand-gold overflow-hidden shrink-0 shadow-sm">
                <img :src="userPhoto" class="w-full h-full object-cover" @error="(e) => (e.target as any).style.display='none'" />
              </div>
              <span v-else class="h-10 w-10 rounded-full bg-brand-gold text-white flex items-center justify-center font-bold shrink-0 shadow-sm">{{ initials }}</span>
            </template>
            <template v-else>
               <svg class="w-8 h-8 text-slate-800" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16"></path></svg>
            </template>
          </button>
        </div>
      </div>

    <!-- MOBILE MENU -->
    <Transition name="slide">
      <div
        v-if="mobileOpen"
        class="lg:hidden fixed inset-x-0 top-15 z-40 bg-white shadow-2xl flex flex-col items-center gap-6 px-8 py-10 rounded-b-[40px] border-t border-slate-50"
      >
        <div class="flex flex-col items-center gap-2 w-full">
          <NuxtLink
            v-for="link in visibleLinks"
            :key="link.to"
            :to="link.to"
            @click="mobileOpen = false"
            class="w-full text-center py-4 rounded-2xl font-bold text-lg text-slate-800 hover:bg-slate-50 hover:text-brand-gold transition-all active:scale-95"
          >
            {{ link.name }}
          </NuxtLink>
        </div>

        <div class="w-full pt-4 border-t border-slate-100 flex flex-col items-center">
          <Login />
        </div>
      </div>
    </Transition>
  </nav>
</template>

<style scoped>
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.55s ease-in-out;
}
.slide-enter-from,
.slide-leave-to {
  transform: translateY(-100%);
}
</style>
