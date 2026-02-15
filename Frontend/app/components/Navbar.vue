<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import Login from '~/components/Login.vue'
import { useAuthStore } from '~/stores/auth'

const mobileOpen = ref(false)

const auth = useAuthStore()

const displayName = computed(() => auth.user?.name ?? auth.user?.email ?? '')
const initials = computed(() => {
  const n = displayName.value.trim()
  if (!n) return ''
  const parts = n.split(/\s+/).filter(Boolean)
  if (parts.length === 0) return ''
  if (parts.length === 1) return parts[0].slice(0, 2).toUpperCase()
  const a = parts[0]?.charAt(0) ?? ''
  const b = parts[parts.length - 1]?.charAt(0) ?? ''
  return (a + b).toUpperCase()
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
    class="fixed top-0 left-0 right-0 w-full lg:w-190 z-50 bg-transparent transition-transform duration-300 ease-in-out"
    :class="[ showNavbar ? 'translate-y-0' : '-translate-y-full' ]"
  >
      <div class="hidden bg-white lg:flex lg:rounded-br-[80px] lg:rounded-tr-[10px] lg:hover:rounded-br-[100px] lg:hover:rounded-tr-[10px] px-4 items-center relative h-15">
        <div class="flex items-center gap-4">
          <NuxtLink to="/" class="flex fixed items-center gap-3">
             <div class="flex flex-col leading-tight">
                <span class="font-fleur text-2xl text-slate-800 hover:text-brand-gold transition-colors">Kollamparambil</span>
                <span class="font-fleur text-xl text-slate-600 hover:text-brand-gold transition-colors -mt-1 ml-4">Family</span>
             </div>
          </NuxtLink>
          <div class="flex absolute items-center gap-4 right-6">
            <NuxtLink
              v-for="link in visibleLinks"
              :key="link.to"
              :to="link.to"
              class="py-2 rounded-md text-sm font-bold text-slate-800 hover:bg-slate-50 hover:text-brand-olive hover:shadow-sm transition"
            >
              {{ link.name }}
            </NuxtLink>
          </div>
        </div>
        <div class="flex -z-20 ml-170 items-center gap-3">
          <Login />
        </div>
      </div>



      <!-- Mobile -->
      <div class="flex bg-white lg:hidden items-center z-30 justify-between h-15">
        <NuxtLink to="/" class="flex px-3 items-center gap-3">
           <div class="flex flex-col leading-tight">
              <span class="font-fleur text-xl text-slate-800">Kollamparambil</span>
              <span class="font-fleur text-lg text-slate-600 -mt-1 ml-4">Family</span>
           </div>
        </NuxtLink>

        <div class="flex items-center gap-2">
          <button
            @click="mobileOpen = !mobileOpen"
            class="flex items-center gap-3 text-base font-semibold text-slate-800 pr-6 py-1 rounded transition"
          >
            <template v-if="auth.isAuthenticated">
              <div v-if="auth.user?.profile_pic" class="h-8 w-8 rounded-full border border-slate-200 overflow-hidden">
                <img :src="auth.user.profile_pic.startsWith('http') ? auth.user.profile_pic : `${useRuntimeConfig().public.apiBase || 'http://localhost:8000'}${auth.user.profile_pic}`" class="w-full h-full object-cover" />
              </div>
              <span v-else class="h-8 w-8 rounded-full bg-brand-gold text-white flex items-center justify-center font-bold">{{ initials }}</span>
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
        class="lg:hidden fixed inset-x-0 top-15 -z-10 bg-white shadow-lg flex flex-col gap-3 px-6 pb-6 rounded-b-4xl"
      >
        <div class="flex items-center justify-between pt-3">
          <button @click="mobileOpen = false" class="text-xl"></button>
        </div>

        <div class="flex flex-col gap-2 mt-2">
          <NuxtLink
            v-for="link in visibleLinks"
            :key="link.to"
            :to="link.to"
            @click="mobileOpen = false"
            class="w-full text-center py-3 rounded-md font-semibold text-slate-800 hover:bg-slate-50 transition"
          >
            {{ link.name }}
          </NuxtLink>
        </div>

        <div class="mt-3">
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
