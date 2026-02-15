<template>
  <div :class="cardClass" class="bg-white rounded-lg shadow-sm p-4 flex items-center gap-4 border border-slate-200 hover:shadow-md transition">
    <div class="shrink-0">
      <img v-if="member.photo" :src="resolveImage(member.photo)" alt="photo" class="w-16 h-16 rounded-full object-cover ring-1 ring-slate-100 shadow-sm" />
      <div v-else class="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center text-lg font-semibold text-slate-500">
        {{ initials }}
      </div>
    </div>

    <div class="flex-1 min-w-0">
      <div class="flex items-center justify-between gap-2">
        <h3 class="text-sm font-semibold truncate text-slate-800">{{ member.name }}</h3>
        <span v-if="member.is_committee" class="shrink-0 bg-brand-olive/10 text-brand-olive text-[10px] px-1.5 py-0.5 rounded font-bold uppercase tracking-tight">Comm</span>
        <span class="shrink-0 text-[10px] text-slate-400">#{{ member.id }}</span>
      </div>
      <p class="text-xs text-slate-500 truncate mt-0.5">
        <span v-if="member.role" class="text-brand-gold font-bold mr-1">{{ member.role }}</span>
        <span v-else-if="member.relation">{{ member.relation }}</span>
        <span v-if="member.age" class="ml-1 opacity-70">• {{ member.age }}y</span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FamilyMember } from '~/types/family'
import { computed } from 'vue'
import { useRuntimeConfig } from '#imports'

const props = defineProps<{ member: FamilyMember; variant?: 'default' | 'compact' | 'list' }>()
const config = useRuntimeConfig()
const apiBase = config.public.apiBase || 'http://localhost:8000'

const resolveImage = (path: string | undefined | null) => {
    if (!path) return undefined
    if (path.startsWith('http')) return path
    return `${apiBase}${path}`
}

const initials = computed(() => {
  const n = props.member?.name ?? ''
  return n.split(' ').map((s) => s.charAt(0).toUpperCase()).slice(0,2).join('')
})

const cardClass = computed(() => {
  if (props.variant === 'compact') return 'py-2 px-3'
  if (props.variant === 'list') return 'w-full'
  return 'py-3 px-4'
})
</script>

<style scoped>
/* minimal scoped styling; layout handled via Tailwind */
</style>
