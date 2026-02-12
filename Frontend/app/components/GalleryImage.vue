<template>
  <div
    class="gallery-item"
    :title="image.title || ''"
    role="button"
    tabindex="0"
    @click.stop="$emit('open', image)"
    @keydown.enter.stop="$emit('open', image)"
    @contextmenu.prevent
  >
    <img
      :data-src="image.photo"
      :alt="image.title || 'Gallery image'"
      loading="lazy"
      class="gallery-img"
      @load="loaded = true"
      ref="imgEl"
      draggable="false"
    />

    <div class="meta">
      <span class="date">{{ formattedDate }}</span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onBeforeUnmount, computed } from 'vue'

interface GalleryItem {
  id: number
  photo: string
  title?: string
  created_at?: string
}

const props = defineProps<{ image: GalleryItem }>()
const emit = defineEmits(['open'])
const imgEl = ref<HTMLImageElement | null>(null)
const loaded = ref(false)

const formattedDate = computed(() => {
  if (!props.image?.created_at) return ''
  try {
    return new Date(props.image.created_at).toLocaleDateString()
  } catch {
    return props.image.created_at
  }
})

let io: IntersectionObserver | null = null

onMounted(() => {
  // Ensure src set when element becomes visible
  if (imgEl.value) {
    io = new IntersectionObserver(entries => {
      entries.forEach(en => {
        if (en.isIntersecting) {
          if (imgEl.value && imgEl.value.dataset.src) {
            imgEl.value.src = imgEl.value.dataset.src
          }
          io?.disconnect()
        }
      })
    })
    io.observe(imgEl.value)
  }
})

onBeforeUnmount(() => {
  io?.disconnect()
})
</script>

<style scoped>
.gallery-item {
  display: block;
  width: 100%;
  margin: 0;
  padding: 0;
  position: relative;
  break-inside: avoid;
  cursor: pointer;
  overflow: hidden;
}

.gallery-img {
  width: 100%;
  height: auto;
  display: block;
  border-radius: 0;
  background: #f3f4f6;
  transition: opacity 180ms ease-in-out, transform 160ms ease;
  will-change: opacity, transform;
  -webkit-user-drag: none;
  user-select: none;
}

.gallery-item:active .gallery-img { transform: scale(0.995) }

.meta {
  position: absolute;
  left: 8px;
  bottom: 8px;
  background: rgba(0,0,0,0.5);
  color: white;
  padding: 4px 8px;
  border-radius: 6px;
  font-size: 12px;
}

.date { font-weight: 500 }
</style>
