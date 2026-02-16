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
const isUploading = ref(false)
const error = ref<string | null>(null)
const showUploadModal = ref(false)

const uploadForm = ref({
  image: null as File | null,
  description: '',
  date: new Date().toISOString().split('T')[0]
})

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

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    uploadForm.value.image = target.files[0] || null
  }
}

const handleUpload = async () => {
  if (!uploadForm.value.image) {
    alert("Please select an image first.")
    return
  }

  isUploading.value = true
  try {
    const formData = new FormData()
    formData.append('image', uploadForm.value.image)
    formData.append('description', uploadForm.value.description)
    if (uploadForm.value.date) {
      formData.append('date', uploadForm.value.date)
    }

    const res = await fetch(apiBase + '/api/profiles/gallery/', {
      method: 'POST',
      credentials: 'include',
      body: formData
    })

    if (!res.ok) {
      const errData = await res.json().catch(() => ({}))
      throw new Error(errData.detail || 'Upload failed')
    }

    // Reset and close
    showUploadModal.value = false
    uploadForm.value = { image: null, description: '', date: new Date().toISOString().split('T')[0] }
    await loadGallery()
  } catch (e: any) {
    alert(e.message || 'Upload failed')
  } finally {
    isUploading.value = false
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
  <div class="min-h-screen bg-slate-50 font-sans pt-32 pb-16 px-4">
    <div class="page-container">
      <div class="max-w-7xl mx-auto mb-16 text-center space-y-4">
        <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
            Family Gallery
        </h1>
        <div class="h-1.5 w-32 bg-brand-gold mx-auto rounded-full"></div>
        <p class="text-lg text-slate-500 max-w-xl mx-auto font-medium">
            Capturing moments of our shared heritage and celebrations.
        </p>

        <div class="pt-4">
            <button 
                @click="showUploadModal = true"
                class="bg-brand-gold text-white px-6 py-2.5 rounded-full font-bold hover:bg-opacity-90 transition shadow-lg"
            >
                Upload Photo
            </button>
        </div>
      </div>

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

      <!-- Upload Modal -->
      <div v-if="showUploadModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
        <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="showUploadModal = false"></div>
        <div class="relative bg-white rounded-2xl shadow-2xl max-w-md w-full p-8 overflow-hidden">
          <h3 class="text-2xl font-serif font-bold text-slate-900 mb-6">Upload Gallery Photo</h3>
          
          <div class="space-y-4">
            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Photo</label>
              <input 
                type="file" 
                accept="image/*" 
                @change="handleFileChange"
                class="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-brand-gold file:text-white hover:file:bg-opacity-90"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-slate-700 mb-1.5">Description (Optional)</label>
              <textarea 
                v-model="uploadForm.description"
                placeholder="Share a short memory or detail..."
                class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-gold focus:border-brand-gold outline-none h-24 resize-none transition-all"
              ></textarea>
            </div>

            <div>
                <label class="block text-sm font-semibold text-slate-700 mb-1.5">Event Date (Optional)</label>
                <input 
                  type="date"
                  v-model="uploadForm.date"
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 focus:ring-2 focus:ring-brand-gold focus:border-brand-gold outline-none transition-all"
                />
              </div>

            <div class="flex gap-3 pt-4 font-bold">
              <button 
                @click="showUploadModal = false"
                class="flex-1 px-6 py-3 rounded-xl border-2 border-slate-100 text-slate-600 hover:bg-slate-50 transition-all active:scale-95"
              >
                Cancel
              </button>
              <button 
                @click="handleUpload"
                :disabled="isUploading || !uploadForm.image"
                class="flex-[2] px-6 py-3 rounded-xl bg-brand-gold text-white hover:shadow-lg hover:shadow-brand-gold/20 disabled:opacity-50 transition-all active:scale-95"
              >
                <span v-if="isUploading">Uploading...</span>
                <span v-else>Share Moment</span>
              </button>
            </div>
          </div>
        </div>
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
