<template>
  <div :class="cardClass" class="bg-white rounded-lg shadow-sm p-4 flex items-center gap-4 border border-slate-200 hover:shadow-md transition">
    <div class="shrink-0">
      <img v-if="member.photo" :src="member.photo" alt="photo" class="w-16 h-16 rounded-full object-cover ring-1 ring-slate-100" />
      <div v-else class="w-16 h-16 rounded-full bg-slate-100 flex items-center justify-center text-lg font-semibold text-slate-500">
        {{ initials }}
      </div>
    </div>

    <div class="flex-1 min-w-0">
      <div class="flex items-center justify-between">
        <h3 class="text-sm font-semibold truncate text-slate-800">{{ member.name }}</h3>
        <span class="text-xs text-slate-400">#{{ member.id }}</span>
      </div>
      <p class="text-xs text-slate-500 truncate">
        <span v-if="member.role" class="text-amber-600 font-bold mr-1">{{ member.role }}</span>
        <span v-else-if="member.relation">{{ member.relation }}</span>
        <span v-if="member.age" class="ml-1">• {{ member.age }}y</span>
      </p>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { FamilyMember } from '~/types/family'
import { computed } from 'vue'

const props = defineProps<{ member: FamilyMember; variant?: 'default' | 'compact' | 'list' }>()

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
