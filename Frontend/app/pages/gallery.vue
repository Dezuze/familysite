<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'
import { useRuntimeConfig } from '#imports'
import GalleryImage from '~/components/GalleryImage.vue'
import GalleryLightbox from '~/components/GalleryLightbox.vue'

interface GalleryItem {
  id: number
  photo: string
  title?: string
  created_at?: string
}

const config = useRuntimeConfig()
const apiBase = config.public.apiBase as string

const images = ref<GalleryItem[]>([])
const visibleCount = ref(30)
const perPage = 30
const isLoading = ref(false)
const error = ref<string | null>(null)

const sentinel = ref<HTMLElement | null>(null)
let io: IntersectionObserver | null = null

const sortedImages = computed(() =>
  [...images.value].sort((a, b) => {
    const da = a.created_at ? Date.parse(a.created_at) : 0
    const db = b.created_at ? Date.parse(b.created_at) : 0
    return db - da
  })
)

const visibleImages = computed(() => sortedImages.value.slice(0, visibleCount.value))
const hasMore = computed(() => visibleCount.value < sortedImages.value.length)

const loadGallery = async () => {
  isLoading.value = true
  error.value = null
  try {
    const res = await fetch(apiBase + '/api/profiles/gallery/', { credentials: 'include' })
    if (!res.ok) throw new Error(`${res.status}`)
    const payload = await res.json()
    const list = Array.isArray(payload) ? payload : (payload?.items ?? [])

    images.value = (list || []).map((i: any) => ({
      id: i.id,
      photo: i.photo ? (i.photo.startsWith('http') ? i.photo : apiBase + i.photo) : '',
      title: i.title ?? i.name ?? '',
      created_at: i.created_at ?? i.date ?? i.uploaded_at ?? null,
    }))
  } catch (e: any) {
    error.value = e?.message ?? 'Failed to load gallery'
  } finally {
    isLoading.value = false
  }
}

const loadMore = () => {
  if (!hasMore.value) return
  visibleCount.value = Math.min(images.value.length, visibleCount.value + perPage)
}

const selectedImage = ref<GalleryItem | null>(null)

const openImage = (img: GalleryItem) => {
  selectedImage.value = img
}

const closeLightbox = () => { selectedImage.value = null }

const currentIndex = () => sortedImages.value.findIndex(i => i.id === selectedImage.value?.id)

const nextImage = () => {
  const idx = currentIndex()
  if (idx >= 0 && idx < sortedImages.value.length - 1) {
    selectedImage.value = sortedImages.value[idx + 1]
  }
}

const prevImage = () => {
  const idx = currentIndex()
  if (idx > 0) selectedImage.value = sortedImages.value[idx - 1]
}

onMounted(async () => {
  await loadGallery()

  io = new IntersectionObserver(entries => {
    entries.forEach(en => {
      if (en.isIntersecting && hasMore.value && !isLoading.value) {
        loadMore()
      }
    })
  }, { root: null, rootMargin: '400px', threshold: 0 })

  if (sentinel.value) io.observe(sentinel.value)
})

onBeforeUnmount(() => {
  io?.disconnect()
})
</script>

<template>
  <div class="min-h-screen bg-slate-100 font-sans pt-32">
    <div class="page-container">
      <header class="gallery-header text-center py-8">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 mb-2">Gallery</h1>
        <div class="h-1 w-16 bg-amber-500 mx-auto rounded-full mb-4"></div>
        <p class="muted text-slate-500 font-medium">Latest images from our family gatherings and events.</p>
      </header>

      <main>
      <div class="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4 p-4">
        <GalleryImage
          v-for="img in visibleImages"
          :key="img.id"
          :image="img"
          @open="openImage"
        />
      </div>

      <GalleryLightbox
        v-if="selectedImage"
        :image="selectedImage"
        @close="closeLightbox"
        @next="nextImage"
        @prev="prevImage"
      />

      <div ref="sentinel" class="h-1 w-full" />

      <div class="text-center py-8 text-slate-500">
        <div v-if="isLoading">Loading...</div>
        <div v-if="error" class="text-red-500">Error: {{ error }}</div>
        <div v-if="!hasMore && !isLoading" class="text-gray-600">No more images</div>
      </div>
    </main>
    </div>
  </div>
</template>

<style scoped>
.page-container { margin: 0 auto; width: 100%; }
.gallery-header { margin-bottom: 24px }
/* Grid handled by Tailwind classes */
</style>
