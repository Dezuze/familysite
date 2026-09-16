<script setup lang="ts">
import { ref, computed } from 'vue'
import QrcodeVue from 'qrcode.vue'
import { useI18n } from 'vue-i18n'
import { useAuthStore } from '~/stores/auth'
import { useRuntimeConfig, useFetch, useHead } from '#imports'

const { t } = useI18n()
const authStore = useAuthStore()
const config = useRuntimeConfig()
const apiBase = (config.public.apiBase as string) || 'http://localhost:8000'

useHead(() => ({
  title: 'Donate | Kollamparampil Family'
}))

// The single unified options managed in Django admin
const { data: donationOptions, pending: optionsLoading } = useFetch<any[]>(`${apiBase}/api/payments/options/`)

const showQrModal = ref(false)
const selectedOption = ref<any>(null)
const loading = ref(false)

const userName = computed(() => {
    if (authStore.user) {
        return authStore.user.name || (authStore.user.first_name ? `${authStore.user.first_name} ${authStore.user.last_name || ''}`.trim() : 'Donor')
    }
    return 'Donor'
})

const upiUrl = computed(() => {
    if (!selectedOption.value) return ''
    const opt = selectedOption.value
    const userId = authStore.user ? authStore.user.id : 'Guest'
    const note = `${userId}`
    return `upi://pay?pa=${opt.upi_id}&pn=${encodeURIComponent(opt.payee_name)}&am=${parseFloat(opt.amount).toFixed(2)}&cu=INR&tn=${encodeURIComponent(note)}`
})

const handleCardClick = async (option: any) => {
    selectedOption.value = option
    loading.value = true
    await new Promise(r => setTimeout(r, 600)) // smooth UI effect
    loading.value = false
    showQrModal.value = true
}

const closeQrModal = () => {
    showQrModal.value = false
    selectedOption.value = null
}
</script>

<template>
    <div class="min-h-screen bg-slate-50 px-2 sm:px-4 pt-32 pb-10 text-slate-800 font-sans overflow-x-hidden relative flex flex-col">
        <!-- Background Pattern -->
        <div class="absolute inset-0 pointer-events-none opacity-40">
            <div class="absolute inset-0" style="background-image: radial-gradient(circle at 2px 2px, rgba(148, 163, 184, 0.15) 1px, transparent 0); background-size: 32px 32px;"></div>
            <div class="absolute inset-0 bg-gradient-to-b from-transparent via-slate-50/50 to-slate-50"></div>
        </div>

        <main class="mx-auto flex min-h-[calc(100vh-10rem)] w-full max-w-full flex-col md:max-w-7xl relative z-10">
            <div class="max-w-3xl mx-auto w-full">
                <!-- Header -->
                <div class="text-center mb-12 space-y-4">
                    <div class="inline-flex items-center justify-center px-4 py-1.5 rounded-full bg-brand-gold/10 text-brand-gold text-sm font-bold tracking-widest uppercase mb-2">
                        Support Our Legacy
                    </div>
                    <h1 class="text-4xl md:text-5xl font-serif font-bold text-slate-900 leading-tight">
                        Help Us Preserve <br /> Our Family History
                    </h1>
                    <div class="h-1.5 w-32 bg-brand-gold mx-auto rounded-full mb-6"></div>
                    <p class="text-lg text-slate-600 font-medium max-w-2xl mx-auto leading-relaxed mt-6">
                        Maintaining the servers, databases, and expanding this platform requires resources. Your contribution ensures that future generations can continue to explore our shared heritage.
                    </p>
                </div>

                <!-- Donation Options -->
                <div class="bg-white/80 backdrop-blur-xl rounded-[2rem] p-8 md:p-12 shadow-2xl border border-slate-100 mb-8">
                    
                    <h3 class="text-xl font-bold text-slate-800 mb-6">Select an amount</h3>
                    
                    <div v-if="optionsLoading" class="flex justify-center py-12">
                        <svg class="animate-spin h-8 w-8 text-brand-gold" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                        </svg>
                    </div>

                    <!-- Grid of options matching the image -->
                    <div v-else-if="donationOptions?.length" class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                        <div 
                            v-for="option in donationOptions" 
                            :key="option.id"
                            @click="handleCardClick(option)"
                            class="relative p-8 rounded-2xl border-2 cursor-pointer transition-all duration-300 group overflow-hidden flex flex-col items-center text-center"
                            :class="selectedOption?.id === option.id ? 'border-brand-gold bg-brand-gold/5 shadow-md shadow-brand-gold/10 scale-105' : 'border-slate-100 bg-white hover:border-brand-gold/40 hover:bg-slate-50'"
                        >
                            <div class="text-4xl font-black mb-3 transition-colors duration-300" :class="selectedOption?.id === option.id ? 'text-brand-gold' : 'text-slate-800'">
                                ₹{{ parseFloat(option.amount) }}
                            </div>
                            <div class="text-sm font-bold uppercase tracking-widest mb-3 transition-colors duration-300" :class="selectedOption?.id === option.id ? 'text-brand-gold-dark' : 'text-slate-500'">
                                {{ option.title }}
                            </div>
                            <div class="text-sm font-medium text-slate-500 leading-relaxed max-w-[200px]">
                                {{ option.purpose }}
                            </div>

                            <!-- Loading overlay for individual card -->
                            <div v-if="loading && selectedOption?.id === option.id" class="absolute inset-0 bg-white/80 backdrop-blur-sm flex items-center justify-center">
                                <svg class="animate-spin h-8 w-8 text-brand-gold" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                                    <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
                                    <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                                </svg>
                            </div>
                        </div>
                    </div>
                    
                    <div class="text-center mt-6 flex items-center justify-center gap-2 text-xs font-semibold text-slate-400 uppercase tracking-widest">
                        <svg class="w-4 h-4 text-slate-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"></path></svg>
                        Secure Encrypted Transaction
                    </div>

                </div>
            </div>
        </main>

        <!-- QR Code Modal -->
        <Transition name="fade">
            <div v-if="showQrModal && selectedOption" class="fixed inset-0 z-50 flex items-center justify-center p-4">
                <!-- Backdrop -->
                <div class="absolute inset-0 bg-slate-900/60 backdrop-blur-sm" @click="closeQrModal"></div>
                
                <!-- Modal Content -->
                <div class="relative bg-white rounded-3xl shadow-2xl w-full max-w-sm overflow-hidden scale-fade-enter-active">
                    <div class="p-6 md:p-8 text-center flex flex-col items-center">
                        <h2 class="text-2xl font-bold text-slate-800 mb-2">Scan to Donate</h2>
                        <p class="text-slate-500 text-sm mb-6">Open your preferred UPI app and scan the QR code below.</p>
                        
                        <div class="bg-slate-50 p-6 rounded-2xl border border-slate-100 shadow-inner mb-6 inline-block">
                            <qrcode-vue :value="upiUrl" :size="200" level="H" foreground="#1e293b" />
                        </div>
                        
                        <div class="text-3xl font-black text-brand-gold mb-1">
                            ₹{{ parseFloat(selectedOption.amount) }}
                        </div>
                        <div class="text-sm font-semibold text-slate-600 mb-6 uppercase tracking-widest">
                            {{ selectedOption.title }}
                        </div>

                        <button @click="closeQrModal" class="w-full py-3.5 rounded-xl bg-slate-100 hover:bg-slate-200 text-slate-700 font-bold transition-colors">
                            Done
                        </button>
                    </div>
                </div>
            </div>
        </Transition>
    </div>
</template>
