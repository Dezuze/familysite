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
const visibleCount = ref(999)
const perPage = 999
const isLoading = ref(false)
const error = ref<string | null>(null)

const sentinel = ref<HTMLElement | null>(null)

const sortedImages = computed(() =>
  [...images.value].sort((a, b) => {
    const da = a.created_at ? Date.parse(a.created_at) : 0
    const db = b.created_at ? Date.parse(b.created_at) : 0
    return db - da
  })
)

const visibleImages = computed(() => sortedImages.value)
const hasMore = computed(() => false)

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
      photo: i.image ? (i.image.startsWith('http') ? i.image : apiBase + i.image) : '',
      title: i.description || i.title || i.name || '',
      created_at: i.created_at || i.date || i.uploaded_at || null,
    }))
  } catch (e: any) {
    error.value = e?.message ?? 'Failed to load gallery'
  } finally {
    isLoading.value = false
  }
}

const loadMore = () => {}

const selectedImage = ref<GalleryItem | null>(null)

const openImage = (img: GalleryItem) => {
  console.log("Opening image:", img)
  selectedImage.value = img
}

const closeLightbox = () => { selectedImage.value = null }

const currentIndex = () => sortedImages.value.findIndex(i => i.id === selectedImage.value?.id)

const nextImage = () => {
  const idx = currentIndex()
  if (idx >= 0 && idx < sortedImages.value.length - 1) {
    selectedImage.value = sortedImages.value[idx + 1] || null
  }
}

const prevImage = () => {
  const idx = currentIndex()
  if (idx > 0) selectedImage.value = sortedImages.value[idx - 1] || null
}

onMounted(async () => {
  await loadGallery()
})

onBeforeUnmount(() => {
})
</script>

<template>
  <div class="min-h-screen bg-slate-100 font-sans pt-32">
    <div class="page-container">
      <header class="gallery-header text-center py-8">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 mb-2">Gallery</h1>
        <div class="h-1 w-16 bg-brand-gold mx-auto rounded-full mb-4"></div>
        <p class="muted text-slate-500 font-medium">Latest images from our family gatherings and events.</p>
      </header>

      <main>
      <div class="columns-2 sm:columns-3 lg:columns-4 xl:columns-5 gap-0 p-0">
        <!-- Skeleton Loaders -->
        <template v-if="isLoading && images.length === 0">
          <div v-for="n in 10" :key="n" class="aspect-square bg-slate-200 animate-pulse border border-slate-100"></div>
        </template>
        
        <GalleryImage
          v-else
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
