<template>
  <footer class="bg-slate-200 text-slate-600 py-16 px-6 border-t border-slate-300 w-full overflow-hidden">
    <div class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center md:items-start gap-10 text-center md:text-left">
      <!-- Logo Section -->
      <div class="flex flex-col items-center md:items-start w-full md:w-auto">
        <img src="/images/logo.png" alt="Family Logo" class="w-48 mb-6 opacity-80 mix-blend-multiply hover:opacity-100 transition-all" />
      </div>

      <!-- Links -->
      <div class="grid grid-cols-2 gap-x-8 sm:gap-x-12 gap-y-4 font-semibold text-base sm:text-lg w-full md:w-auto px-4 md:px-0">
        <NuxtLink v-if="auth.isAuthenticated" to="/familytree" class="hover:text-[#A08050] hover:underline transition-colors leading-tight">Family Tree</NuxtLink>
        <NuxtLink to="/history" class="hover:text-[#A08050] hover:underline transition-colors leading-tight">Family History</NuxtLink>
        <NuxtLink to="/events" class="hover:text-[#A08050] hover:underline transition-colors leading-tight">Events</NuxtLink>
        <NuxtLink v-if="auth.isAuthenticated" to="/committee" class="hover:text-[#A08050] hover:underline transition-colors leading-tight">Committee</NuxtLink>
        <NuxtLink v-if="auth.isAuthenticated" to="/directory" class="hover:text-[#A08050] hover:underline transition-colors leading-tight">Directory</NuxtLink>
        <NuxtLink v-if="auth.isAuthenticated" to="/gallery" class="hover:text-[#A08050] hover:underline transition-colors leading-tight">Gallery</NuxtLink>
        <NuxtLink to="/donate" class="hover:text-[#A08050] hover:underline transition-colors leading-tight">Donations</NuxtLink>
        <NuxtLink to="/contact" class="hover:text-[#A08050] hover:underline transition-colors leading-tight">Contact</NuxtLink>
      </div>
    </div>
    
    <div class="max-w-6xl mx-auto mt-12 pt-8 border-t border-slate-300 flex flex-col items-center gap-4">
      <p class="text-sm font-medium opacity-60 text-center">© {{ new Date().getFullYear() }} Kollamparambil Family. All rights reserved.</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
const auth = useAuthStore()
</script>