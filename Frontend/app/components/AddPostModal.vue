<template>
  <teleport to="body">
    <div v-if="isOpen" class="fixed inset-0 z-50 flex items-center justify-center p-4">
      <!-- Backdrop -->
      <Transition name="fade" appear>
        <div class="absolute inset-0 bg-black/60 backdrop-blur-sm" @click="close"></div>
      </Transition>

      <!-- Modal Content -->
      <Transition name="scale-fade" appear>
        <div class="relative bg-white rounded-2xl p-8 w-full max-w-lg shadow-2xl border border-slate-100 flex flex-col">
          <h2 class="text-2xl font-serif font-bold text-slate-800 mb-6 flex items-center gap-2">
            <span v-if="initialData">✏️ Edit {{ type === 'news' ? 'News' : 'Event' }}</span>
            <span v-else-if="type === 'news'">📰 Add News</span>
            <span v-else>📅 Add Event</span>
          </h2>

          <form @submit.prevent="submit" class="space-y-5">
            <!-- Title -->
            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5 uppercase tracking-wider">Title</label>
              <input 
                v-model="form.title" 
                type="text" 
                required
                class="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-brand-gold/40 transition-shadow"
                placeholder="Enter a descriptive title..."
              />
            </div>

            <!-- Description -->
            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5 uppercase tracking-wider">Description</label>
              <textarea 
                v-model="form.description" 
                required
                rows="4"
                class="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-brand-gold/40 transition-shadow resize-none"
                placeholder="Share the details..."
              ></textarea>
            </div>

            <!-- Event Specific Fields -->
            <div v-if="type === 'event'" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label class="block text-sm font-bold text-slate-700 mb-1.5 uppercase tracking-wider">Date & Time</label>
                <input 
                  v-model="form.event_date" 
                  type="datetime-local" 
                  required
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-brand-gold/40 transition-shadow"
                />
              </div>
              <div>
                <label class="block text-sm font-bold text-slate-700 mb-1.5 uppercase tracking-wider">Location</label>
                <input 
                  v-model="form.location" 
                  type="text" 
                  class="w-full px-4 py-3 rounded-xl border border-slate-200 bg-white focus:outline-none focus:ring-2 focus:ring-brand-gold/40 transition-shadow"
                  placeholder="e.g. Community Hall"
                />
              </div>
            </div>

            <!-- Image Upload (Optional) -->
            <div>
              <label class="block text-sm font-bold text-slate-700 mb-1.5 uppercase tracking-wider">Cover Image (Optional)</label>
              <div class="relative group">
                <input 
                  type="file" 
                  accept="image/*"
                  @change="handleFileChange"
                  class="block w-full text-sm text-slate-500 file:mr-4 file:py-2.5 file:px-4 file:rounded-xl file:border-0 file:text-sm file:font-bold file:bg-brand-gold/10 file:text-brand-gold hover:file:bg-brand-gold/20 transition-all cursor-pointer"
                />
              </div>
            </div>

            <!-- Actions -->
            <div class="flex flex-col sm:flex-row justify-end gap-3 pt-6 border-t border-slate-100">
              <button 
                type="button" 
                @click="close"
                class="px-6 py-3 rounded-xl text-slate-500 font-bold hover:bg-slate-50 transition-colors order-2 sm:order-1"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                :disabled="loading"
                class="px-8 py-3 rounded-xl bg-linear-to-b from-brand-gold to-brand-gold-dark text-white font-bold shadow-lg shadow-brand-gold/20 hover:brightness-110 active:scale-95 transition-all disabled:opacity-50 order-1 sm:order-2"
              >
                {{ loading ? 'Saving...' : (initialData ? 'Save Changes' : 'Post Now') }}
              </button>
            </div>
          </form>
        </div>
      </Transition>
    </div>
  </teleport>
</template>

<script setup lang="ts">
import { ref, reactive, watch } from 'vue'
import { useRuntimeConfig } from '#imports'

const props = defineProps<{
  isOpen: boolean
  type: 'news' | 'event'
  isKudumbayogam?: boolean
  initialData?: any
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

watch(() => props.isOpen, (newVal) => {
  if (newVal && props.initialData) {
    form.title = props.initialData.title || ''
    form.description = props.initialData.description || ''
    form.event_date = props.initialData.event_date ? new Date(props.initialData.event_date).toISOString().slice(0, 16) : ''
    form.location = props.initialData.location || ''
    form.image = null
  } else if (newVal) {
    close() // Reset if opening fresh
  }
})

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

    if (props.isKudumbayogam) {
      formData.append('is_kudumbayogam', 'true')
    }

    // Get CSRF Token
    await fetch(`${apiBase}/api/csrf/`, { credentials: 'include' })
    const csrftoken = getCookie('csrftoken')

    const url = props.initialData 
      ? `${apiBase}/api/news/${props.initialData.id}/`
      : `${apiBase}/api/news/create/`
    
    const method = props.initialData ? 'PUT' : 'POST'

    const res = await fetch(url, {
      method: method,
      headers: {
        ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {})
      },
      body: formData,
      credentials: 'include'
    })

    if (!res.ok) {
      throw new Error(`Failed to ${props.initialData ? 'update' : 'create'} post`)
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

<style scoped>
/* Scoped transitions if needed, but using global ones from tailwind.css */
</style>
