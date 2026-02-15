<script setup lang="ts">
import { useHead } from '#imports'

useHead({
  titleTemplate: () => 'Kollamparambil Family',
  title: 'Kollamparambil Family',
  link: [
    { rel: 'icon', type: 'image/png', href: '/favicon.png?v=3' },
    { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico?v=3' },
    { rel: 'shortcut icon', href: '/favicon.ico?v=3' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Fleur+De+Leah&display=swap' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap' }
  ],
  meta: [
    // Primary Meta Tags
    { name: 'title', content: 'Kollamparambil Family' },
    { name: 'description', content: 'Kollamparambil Family Association - Connecting our heritage and future.' },
    { name: 'keywords', content: 'Kollamparambil, Family, Heritage, Association, Kerala, India' },
    { name: 'author', content: 'Kollamparambil Family' },
    { name: 'viewport', content: 'width=device-width, initial-scale=1.0' },
    
    // Open Graph / Facebook
    { property: 'og:type', content: 'website' },
    { property: 'og:title', content: 'Kollamparambil Family' },
    { property: 'og:description', content: 'Kollamparambil Family Association - Connecting our heritage and future.' },
    { property: 'og:site_name', content: 'Kollamparambil Family' },
    { property: 'og:locale', content: 'en_US' },
    { property: 'og:image', content: '/images/logo.png' },
    { property: 'og:image:width', content: '1200' },
    { property: 'og:image:height', content: '630' },
    { property: 'og:image:alt', content: 'Kollamparambil Family Logo' },
    
    // Twitter
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: 'Kollamparambil Family' },
    { name: 'twitter:description', content: 'Kollamparambil Family Association - Connecting our heritage and future.' },
    { name: 'twitter:image', content: '/images/logo.png' },
    
    // WhatsApp / Mobile
    { property: 'og:image:type', content: 'image/png' },
    { name: 'theme-color', content: '#A08050' },
    
    // Additional Meta
    { name: 'robots', content: 'index, follow' }
  ]
})
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
