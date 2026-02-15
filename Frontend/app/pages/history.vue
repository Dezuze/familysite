<template>
  <div class="min-h-screen bg-slate-50 flex flex-col items-center px-4 pt-32 pb-16 text-slate-800 font-sans">
    <div class="w-full">
    <div class="max-w-7xl mx-auto mb-16 text-center space-y-4">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
            Family History
        </h1>
        <div class="h-1.5 w-32 bg-brand-gold mx-auto rounded-full"></div>
    </div>
        
        <div class="bg-white rounded-xl p-4 md:p-8 backdrop-blur-sm border border-slate-200 shadow-xl w-full">
            <client-only>
            <div class="w-full h-[70vh]">
                <PdfViewer :src="pdfUrl" />
            </div>
            </client-only>
        </div>

        <p class="text-sm text-slate-500 mt-6 text-center">Use swipe or arrow keys to navigate pages.</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import PdfViewer from '~/components/PdfViewer.vue'

const pdfUrl = '/Document/history.pdf'
</script>

<style scoped>
/* center page content */
</style>
