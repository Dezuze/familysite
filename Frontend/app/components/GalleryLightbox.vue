<template>
  <div class="gl-overlay" @click.self="close">
    <div class="gl-inner">
        <!-- Close button -->
        <button class="gl-close" @click.stop="close" aria-label="Close">
          <svg class="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>
        </button>

        <!-- Prev button -->
        <button class="gl-prev" @click.stop="prev" aria-label="Previous">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path></svg>
        </button>

        <div class="gl-content-wrapper">
          <!-- Loading Spinner -->
          <div v-if="loading" class="gl-loading">
            <div class="gl-spinner"></div>
          </div>

          <div 
            class="gl-img" 
            :class="{ 'opacity-0': loading }"
            :style="{ backgroundImage: `url(${image.photo})` }" 
            role="img" 
            :aria-label="image.title || 'Image'"
          ></div>
          
          <!-- Hidden image to track loading -->
          <img :src="image.photo" @load="handleLoad" class="hidden" />

          <!-- blocker captures contextmenu/long-press to make downloading harder -->
          <div class="gl-img-blocker" @contextmenu.prevent @touchstart.prevent @mousedown.prevent></div>
        </div>

        <!-- Next button -->
        <button class="gl-next" @click.stop="next" aria-label="Next">
          <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5l7 7-7 7"></path></svg>
        </button>

        <div class="gl-caption" v-if="image.title || image.created_at">
          <div class="title" v-if="image.title">{{ image.title }}</div>
          <div class="date" v-if="image.created_at">{{ formattedDate }}</div>
        </div>
      </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed, watch } from 'vue'

interface GalleryItem {
  id: number
  photo: string
  title?: string
  created_at?: string | null
}

const props = defineProps<{ image: GalleryItem }>()
const emit = defineEmits(['close', 'next', 'prev'])

const loading = ref(true)

const handleLoad = () => {
  loading.value = false
}

// Reset loading state when image changes (next/prev)
watch(() => props.image.id, () => {
  loading.value = true
})

const close = () => emit('close')
const next = () => emit('next')
const prev = () => emit('prev')

// Touch/swipe support for mobile
let touchStartX = 0
let touchStartY = 0
const SWIPE_THRESHOLD = 50

const onTouchStart = (e: TouchEvent) => {
  const t = e.touches?.[0]
  if (!t) return
  touchStartX = t.clientX
  touchStartY = t.clientY
}

const onTouchEnd = (e: TouchEvent) => {
  const t = e.changedTouches?.[0]
  if (!t) return
  const dx = t.clientX - touchStartX
  const dy = t.clientY - touchStartY
  if (Math.abs(dx) > Math.abs(dy) && Math.abs(dx) > SWIPE_THRESHOLD) {
    if (dx < 0) next()
    else prev()
  }
}

const formattedDate = computed(() => {
  if (!props.image?.created_at) return ''
  try { return new Date(props.image.created_at).toLocaleString() } catch { return props.image.created_at as any }
})

const onKey = (e: KeyboardEvent) => {
  if (e.key === 'Escape') close()
  if (e.key === 'ArrowRight') next()
  if (e.key === 'ArrowLeft') prev()
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
  window.addEventListener('touchstart', onTouchStart, { passive: true })
  window.addEventListener('touchend', onTouchEnd)
  // Prevent background scroll while lightbox open
  document.body.style.overflow = 'hidden'
})

onBeforeUnmount(() => {
  window.removeEventListener('keydown', onKey)
  window.removeEventListener('touchstart', onTouchStart)
  window.removeEventListener('touchend', onTouchEnd)
  document.body.style.overflow = ''
})
</script>

<style scoped>
.gl-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0,0,0,0.92);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  backdrop-filter: blur(4px);
}
.gl-inner { position: relative; width: 100%; max-width: 1200px; height: 90vh; display:flex; align-items:center; justify-content:center; touch-action: none; padding: 0 80px; }
.gl-content-wrapper { position: relative; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center; }
.gl-img { width: 100%; height: 100%; border-radius: 4px; display:block; background-size: contain; background-position: center; background-repeat: no-repeat; -webkit-user-drag: none; user-select: none; transition: opacity 0.3s ease; }
.gl-img.opacity-0 { opacity: 0; }
.gl-img-blocker { position: absolute; left: 0; right: 0; top: 0; bottom: 0; z-index: 2; cursor: default; }

.gl-loading { position: absolute; inset: 0; display: flex; align-items: center; justify-content: center; z-index: 5; }
.gl-spinner { 
  width: 40px; height: 40px; border: 3px solid rgba(255,255,255,0.1); border-top-color: #A08050; border-radius: 50%;
  animation: gl-spin 0.8s linear infinite;
}
@keyframes gl-spin { to { transform: rotate(360deg); } }

.gl-close { 
  position: absolute; right: 20px; top: 20px; background: rgba(0,0,0,0.3); color: white; border: none; 
  padding: 8px; border-radius: 50%; z-index: 1001; cursor: pointer; transition: background 0.2s;
}
.gl-close:hover { background: rgba(255,255,255,0.1); }

.gl-prev, .gl-next { 
  position: absolute; background: rgba(255,255,255,0.05); color: white; border: none; 
  width: 48px; height: 48px; display: flex; align-items: center; justify-content: center;
  border-radius: 50%; z-index: 1001; cursor: pointer; transition: all 0.2s;
}
.gl-prev:hover, .gl-next:hover { background: rgba(255,255,255,0.15); scale: 1.1; }
.gl-prev { left: 16px }
.gl-next { right: 16px }

.gl-caption { position: absolute; left: 0; bottom: 20px; color: white; width: 100%; text-align: center; z-index: 1001; text-shadow: 0 2px 4px rgba(0,0,0,0.8); }
.gl-caption .title { font-weight: 600; font-size: 1.1rem; margin-bottom: 4px; }
.gl-caption .date { font-size: 13px; color: #a1a1aa }

.hidden { display: none; }

@media (max-width: 768px) {
  .gl-inner { padding: 0; }
  .gl-prev, .gl-next { width: 40px; height: 40px; background: rgba(0,0,0,0.2); }
  .gl-prev { left: 8px }
  .gl-next { right: 8px }
  .gl-close { right: 10px; top: 10px; background: rgba(0,0,0,0.5); }
}
</style>
