<template>
  <div class="min-h-screen bg-slate-100 text-slate-800 font-sans pt-32 pb-16 px-4 md:px-12 flex flex-col items-center justify-center">
    <div class="max-w-2xl w-full text-center bg-white p-12 rounded-3xl border border-slate-200 shadow-2xl backdrop-blur-sm">
      
      <!-- Icon -->
      <div class="mb-8 relative inline-block">
        <div class="absolute inset-0 bg-brand-gold/20 blur-xl rounded-full"></div>
        <svg class="w-20 h-20 text-brand-gold relative" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.384-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
      </div>

      <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 mb-4">Under Development</h1>
      <div class="h-1 w-24 bg-brand-gold mx-auto rounded-full mb-6"></div>
      
      <p class="text-lg text-slate-600 leading-relaxed mb-8 font-medium">
        We are currently setting up our secure donation system. <br>
        Please check back soon to support the Kollamparambil Family Association.
      </p>

      <NuxtLink to="/" class="inline-flex items-center gap-2 px-8 py-3 bg-brand-gold hover:bg-brand-gold/90 text-white font-bold rounded-lg shadow-lg hover:brightness-110 transition-all active:scale-95">
        <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"></path></svg>
        Return Home
      </NuxtLink>

    </div>
  </div>
</template>

<script setup lang="ts">
import { useHead } from '#imports'

useHead({
  title: 'Donation - Coming Soon'
})
</script>
