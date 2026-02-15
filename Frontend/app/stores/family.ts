import { defineStore } from 'pinia'
import type { FamilyMember } from '~/types/family'
import { useRuntimeConfig } from '#imports'

export const useFamilyStore = defineStore('family', {
  state: () => ({
    members: [] as FamilyMember[],
    links: [] as any[], // Add links state
    loading: false,
    error: null as string | null
  }),

  actions: {
    async fetchFamily() {
      // Prevent multiple fetches if already loaded
      if (this.members.length > 0 && this.links.length > 0) return

      this.loading = true
      this.error = null
      
      const config = useRuntimeConfig()
      const apiBase = config.public.apiBase || 'http://localhost:8000'

      try {
        const response = await fetch(`${apiBase}/api/families/tree/`, {
             // Add Auth header if needed, but tree might be public or read-only
             // credentials: 'include' 
        })
        if (response.ok) {
            const data = await response.json()
            // Data is { nodes: [], links: [] }
            this.members = data.nodes || []
            this.links = data.links || [] // Store links
        } else {
            this.error = 'Failed to load family data'
        }
      } catch (err) {
        this.error = 'Error loading family data'
        console.error(err)
      } finally {
        this.loading = false
      }
    },

    // find member by id
    findById(id: number): FamilyMember | undefined {
      return this.members.find(m => m.id === id)
    },

    // flat list accessor
    flatList(): FamilyMember[] {
      return this.members
    },
    
    // Legacy support or helper
    // addMember logic moved to backend/onboarding
  },

  persist: true,
})
