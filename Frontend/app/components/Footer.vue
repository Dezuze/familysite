<template>
  <footer class="bg-slate-200 text-slate-600 py-8 md:py-16 px-6 border-t border-slate-300 w-full overflow-hidden">
    <div class="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center md:items-start gap-6 md:gap-10 text-center md:text-left">
      <!-- Logo Section -->
      <div class="flex flex-col items-center md:items-start w-full md:w-auto">
        <span class="font-fleur text-4xl text-slate-800 mb-6 drop-shadow-sm leading-normal py-2 block">
          Kollamparambil Family
        </span>
      </div>

      <!-- Links -->
      <div class="grid grid-cols-2 gap-x-8 sm:gap-x-12 gap-y-4 font-semibold text-base sm:text-lg w-full md:w-auto px-4 md:px-0">
        <NuxtLink v-if="auth.isAuthenticated" to="/familytree" class="hover:text-brand-gold hover:underline transition-colors leading-tight">Family Tree</NuxtLink>
        <NuxtLink to="/history" class="hover:text-brand-gold hover:underline transition-colors leading-tight">Family History</NuxtLink>
        <NuxtLink to="/events" class="hover:text-brand-gold hover:underline transition-colors leading-tight">Events</NuxtLink>
        <NuxtLink v-if="auth.isAuthenticated" to="/committee" class="hover:text-brand-gold hover:underline transition-colors leading-tight">Committee</NuxtLink>
        <NuxtLink v-if="auth.isAuthenticated" to="/directory" class="hover:text-brand-gold hover:underline transition-colors leading-tight">Directory</NuxtLink>
        <NuxtLink v-if="auth.isAuthenticated" to="/gallery" class="hover:text-brand-gold hover:underline transition-colors leading-tight">Gallery</NuxtLink>
        <NuxtLink to="/donate" class="hover:text-brand-gold hover:underline transition-colors leading-tight">Donations</NuxtLink>
        <NuxtLink to="/contact" class="hover:text-brand-gold hover:underline transition-colors leading-tight">Contact</NuxtLink>
      </div>
    </div>
    
    <div class="max-w-6xl mx-auto mt-8 md:mt-12 pt-6 md:pt-8 border-t border-slate-300 flex flex-col items-center gap-4">
      <p class="text-xs md:text-sm font-medium opacity-60 text-center">© {{ new Date().getFullYear() }} Kollamparambil Family. All rights reserved.</p>
    </div>
  </footer>
</template>

<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'
const auth = useAuthStore()
</script>