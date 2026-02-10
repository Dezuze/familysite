<script setup lang="ts">
import { useHead } from '#imports'

useHead({
  titleTemplate: (titleChunk) => {
    return titleChunk ? `${titleChunk} - Kollamparambil Family` : 'Kollamparambil Family'
  },
  link: [
    { rel: 'icon', type: 'image/png', href: '/favicon.png?v=3' },
    { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico?v=3' },
    { rel: 'shortcut icon', href: '/favicon.ico?v=3' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap' }
  ],
  meta: [
    { name: 'description', content: 'Kollamparambil Family Association - Connecting our heritage and future.' }
  ]
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
