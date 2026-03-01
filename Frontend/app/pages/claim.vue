<template>
  <div class="min-h-screen bg-[#F5F5F7] text-slate-900 pt-32 pb-16 px-4 flex flex-col items-center font-sans">
    <div class="max-w-md w-full">
      <div class="bg-white/70 backdrop-blur-2xl p-8 md:p-12 rounded-[40px] shadow-[0_20px_40px_rgba(0,0,0,0.05)] border border-white/60">
        
        <div class="text-center mb-8">
          <div class="w-20 h-20 bg-brand-gold/10 rounded-3xl flex items-center justify-center mx-auto mb-4">
            <svg class="w-10 h-10 text-brand-gold" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H4a1 1 0 01-1-1v-2.586a1 1 0 01.293-.707l5.964-5.964A6 6 0 1121 9z"></path></svg>
          </div>
          <h1 class="text-3xl font-black text-slate-900 mb-2">Claim Your Account</h1>
          <p class="text-slate-500 text-sm font-medium">A family member has created a profile for you. Set your new password to take control.</p>
        </div>

        <div v-if="!claimed" class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">New Password</label>
            <input v-model="newPassword" type="password" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-brand-gold focus:ring-4 focus:ring-brand-gold/10 outline-none transition-all" placeholder="Choose a strong password">
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-500 uppercase tracking-wider mb-2 ml-1">Confirm Password</label>
            <input v-model="confirmPassword" type="password" class="w-full bg-slate-50 border border-slate-200 rounded-2xl px-4 py-3.5 text-slate-900 font-medium focus:bg-white focus:border-brand-gold focus:ring-4 focus:ring-brand-gold/10 outline-none transition-all" placeholder="Confirm password">
          </div>

          <div v-if="error" class="text-sm text-red-600 font-medium">{{ error }}</div>

          <button @click="claim" :disabled="loading" class="w-full py-4 bg-brand-gold text-white font-bold rounded-2xl hover:brightness-110 active:scale-95 transition-all disabled:opacity-50 text-lg">
            {{ loading ? 'Claiming...' : 'Claim Account' }}
          </button>
        </div>

        <div v-else class="text-center py-8">
          <div class="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg class="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>
          </div>
          <h2 class="text-2xl font-black text-slate-900 mb-2">Account Claimed!</h2>
          <p class="text-slate-500 mb-6">Welcome! You are now logged in.</p>
          <button @click="$router.push('/onboarding')" class="px-8 py-3 bg-brand-gold text-white font-bold rounded-2xl hover:brightness-110 active:scale-95 transition-all">
            Edit My Profile
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useAuthStore } from '~/stores/auth'

const route = useRoute()
const router = useRouter()
const auth = useAuthStore()

const newPassword = ref('')
const confirmPassword = ref('')
const error = ref('')
const loading = ref(false)
const claimed = ref(false)

const tokenFromUrl = ref('')

onMounted(() => {
    tokenFromUrl.value = route.query.token || ''
    if (!tokenFromUrl.value) {
        error.value = 'No claim token provided. Please use the link shared by your family member.'
    }
})

async function claim() {
    error.value = ''
    if (!newPassword.value) {
        error.value = 'Please enter a new password.'
        return
    }
    if (newPassword.value !== confirmPassword.value) {
        error.value = 'Passwords do not match.'
        return
    }
    if (newPassword.value.length < 6) {
        error.value = 'Password must be at least 6 characters.'
        return
    }

    loading.value = true
    const result = await auth.claimAccount(tokenFromUrl.value, newPassword.value)
    loading.value = false

    if (result.ok) {
        claimed.value = true
    } else {
        error.value = result.error || 'Failed to claim account.'
    }
}
</script>
