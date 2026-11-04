<script setup lang="ts">
import { useHead, useRoute, useRuntimeConfig } from '#imports'
import { onMounted } from 'vue'
import { useLanguage } from '~/composables/useLanguage'
import { useI18n } from 'vue-i18n'

const route = useRoute()
const config = useRuntimeConfig()
const siteUrl = config.public.siteUrl || 'http://localhost:3000'
const { initLanguage } = useLanguage()
const { t } = useI18n()

onMounted(() => {
  initLanguage()
})

useHead(() => ({
  titleTemplate: (title: string | undefined) => {
    return (title && title !== t('app.siteName')) ? `${title} | ${t('app.siteName')}` : t('app.siteName')
  },
  title: t('app.siteName'),
  link: [
    { rel: 'manifest', href: '/manifest.webmanifest' },
    { rel: 'apple-touch-icon', href: '/favicon.png?v=4' },
    { rel: 'icon', type: 'image/png', href: '/favicon.png?v=4' },
    { rel: 'icon', type: 'image/x-icon', href: '/favicon.ico?v=4' },
    { rel: 'shortcut icon', href: '/favicon.ico?v=4' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Cinzel:wght@400;700&display=swap' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Fleur+De+Leah&display=swap' },
    { rel: 'stylesheet', href: 'https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap' },
    { rel: 'canonical', href: `${siteUrl}${route.path}` }
  ],
  meta: [
    // Primary Meta Tags
    { name: 'title', content: t('app.siteName') },
    { name: 'description', content: t('app.metaDescription') },
    { name: 'keywords', content: 'Kollamparampil, Family, Heritage, Association, Kerala, India' },
    { name: 'author', content: t('app.siteName') },
    { name: 'viewport', content: 'width=device-width, initial-scale=1.0' },
    { name: 'mobile-web-app-capable', content: 'yes' },
    { name: 'apple-mobile-web-app-capable', content: 'yes' },
    { name: 'apple-mobile-web-app-status-bar-style', content: 'default' },
    { name: 'apple-mobile-web-app-title', content: t('app.siteName') },
    
    // Open Graph / Facebook
    { property: 'og:type', content: 'website' },
    { property: 'og:title', content: t('app.siteName') },
    { property: 'og:description', content: t('app.metaDescription') },
    { property: 'og:site_name', content: t('app.siteName') },
    { property: 'og:locale', content: 'en_US' },
    { property: 'og:image', content: '/images/logo.png' },
    { property: 'og:image:width', content: '1200' },
    { property: 'og:image:height', content: '630' },
    { property: 'og:image:alt', content: 'Kollamparampil Family Logo' },
    
    // Twitter
    { name: 'twitter:card', content: 'summary_large_image' },
    { name: 'twitter:title', content: t('app.siteName') },
    { name: 'twitter:description', content: t('app.metaDescription') },
    { name: 'twitter:image', content: '/images/logo.png' },
    
    // WhatsApp / Mobile
    { property: 'og:image:type', content: 'image/png' },
    { name: 'theme-color', content: t('app.themeColor') },
    
    // Additional Meta
    { name: 'robots', content: 'index, follow' }
  ],
  script: [
    {
      type: 'application/ld+json',
      children: JSON.stringify({
        "@context": "https://schema.org",
        "@type": "Organization",
        "name": t('app.siteName'),
        "url": siteUrl,
        "logo": `${siteUrl}/images/logo.png`
      })
    }
  ]
}))
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
