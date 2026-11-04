<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from '#imports'
import Footer from '~/components/Footer.vue'
import Navbar from '~/components/Navbar.vue'
import CelebrationNotifications from '~/components/CelebrationNotifications.vue'

const route = useRoute()
const hideFooter = computed(() => ['/familytree', '/history'].includes(route.path))
</script>

<template>
  <div>
    <Navbar />
    <slot />
    <CelebrationNotifications />
    <Footer v-if="!hideFooter" />
  </div>
</template>
