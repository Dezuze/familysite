<template>
  <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
    <!-- Backdrop -->
    <div class="absolute inset-0 bg-black/50 backdrop-blur-sm" @click="close"></div>

    <!-- Modal Content -->
    <div class="relative bg-white/90 dark:bg-zinc-900/90 backdrop-blur-xl rounded-2xl p-6 w-full max-w-lg shadow-2xl border border-white/20 dark:border-white/10">
      <h2 class="text-2xl font-serif text-slate-800 dark:text-slate-100 mb-4 flex items-center gap-2">
        <span v-if="type === 'news'">📰 Add News</span>
        <span v-else>📅 Add Event</span>
      </h2>

      <form @submit.prevent="submit" class="space-y-4">
        <!-- Title -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Title</label>
          <input 
            v-model="form.title" 
            type="text" 
            required
            class="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-black/20 focus:outline-none focus:ring-2 focus:ring-amber-500/50"
            placeholder="Enter title..."
          />
        </div>

        <!-- Description -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Description</label>
          <textarea 
            v-model="form.description" 
            required
            rows="4"
            class="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-black/20 focus:outline-none focus:ring-2 focus:ring-amber-500/50"
            placeholder="Enter details..."
          ></textarea>
        </div>

        <!-- Event Specific Fields -->
        <div v-if="type === 'event'" class="grid grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Date & Time</label>
            <input 
              v-model="form.event_date" 
              type="datetime-local" 
              required
              class="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-black/20 focus:outline-none focus:ring-2 focus:ring-amber-500/50"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Location</label>
            <input 
              v-model="form.location" 
              type="text" 
              class="w-full px-4 py-2 rounded-xl border border-slate-200 dark:border-slate-700 bg-white dark:bg-black/20 focus:outline-none focus:ring-2 focus:ring-amber-500/50"
              placeholder="e.g. Community Hall"
            />
          </div>
        </div>

        <!-- Image Upload (Optional) -->
        <div>
          <label class="block text-sm font-medium text-slate-700 dark:text-slate-300 mb-1">Image (Optional)</label>
          <input 
            type="file" 
            accept="image/*"
            @change="handleFileChange"
            class="block w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-semibold file:bg-amber-50 file:text-amber-700 hover:file:bg-amber-100 dark:file:bg-amber-900/30 dark:file:text-amber-400"
          />
        </div>

        <!-- Actions -->
        <div class="flex justify-end gap-3 pt-4">
          <button 
            type="button" 
            @click="close"
            class="px-4 py-2 rounded-xl text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-white/5 transition-colors"
          >
            Cancel
          </button>
          <button 
            type="submit" 
            :disabled="loading"
            class="px-6 py-2 rounded-xl bg-linear-to-r from-amber-500 to-orange-600 text-white font-medium shadow-lg shadow-amber-500/20 hover:shadow-amber-500/30 active:scale-95 transition-all disabled:opacity-50"
          >
            {{ loading ? 'Posting...' : 'Post' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'


const props = defineProps<{
  isOpen: boolean
  type: 'news' | 'event'
}>()

const emit = defineEmits(['close', 'refresh'])

const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'

const loading = ref(false)
const form = reactive({
  title: '',
  description: '',
  event_date: '',
  location: '',
  image: null as File | null
})

function close() {
  emit('close')
  // Reset form
  form.title = ''
  form.description = ''
  form.event_date = ''
  form.location = ''
  form.image = null
}

function handleFileChange(event: Event) {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    form.image = target.files[0]
  }
}

function getCookie(name: string) {
  if (typeof document === 'undefined') return null
  const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
  return matches ? matches[2] : null
}

async function submit() {
  loading.value = true
  try {
    const formData = new FormData()
    formData.append('title', form.title)
    formData.append('description', form.description)
    formData.append('post_type', props.type)
    
    if (props.type === 'event') {
      formData.append('event_date', form.event_date)
      formData.append('location', form.location)
    }
    
    if (form.image) {
      formData.append('image', form.image)
    }

    // Get CSRF Token
    await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
    const csrftoken = getCookie('csrftoken')

    const res = await fetch(`${apiBase}/api/news/create/`, {
      method: 'POST',
      headers: {
        ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {})
      },
      body: formData,
      credentials: 'include'
    })

    if (!res.ok) {
      throw new Error('Failed to create post')
    }

    emit('refresh')
    close()
  } catch (e) {
    console.error(e)
    alert('Error creating post')
  } finally {
    loading.value = false
  }
}
</script>
