import { useRuntimeConfig } from '#imports'
import { defineStore } from 'pinia'
import { users } from '~/data/users'

const apiBase = () => (useRuntimeConfig().public.apiBase as string) || 'http://localhost:8000'
const useLocalAuth = () => {
  const flag = (useRuntimeConfig().public as any).localAuth
  return flag === true || flag === 'true'
}

function getCookie(name: string) {
  if (typeof document === 'undefined') return null
  const matches = document.cookie.match(new RegExp('(^|; )' + name + '=([^;]+)'))
  return matches ? matches[2] : null
}

export interface User {
  id: number
  email: string
  first_name?: string
  last_name?: string
  name?: string
  profile_pic?: string | null
  username?: string
  is_superuser?: boolean
  is_staff?: boolean
  managed_members?: Array<{
    id: number
    name: string
    profile_pic: string | null
    relation: string
    is_independent: boolean
    has_account: boolean
  }>
}

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null as null | User,
    token: null as string | null,
    isAuthenticated: false,
  }),

  actions: {
    // Login: uses frontend local users when localAuth enabled; otherwise hits backend
    async login(email: string, password: string) {
      if (useLocalAuth()) {
        const u = users.find((x) => x.email.toLowerCase() === email.toLowerCase() && x.password === password)
        if (!u) return false
        this.setAuth({ id: u.id, email: u.email, name: u.name }, 'local')
        return { ok: true, data: { id: u.id, email: u.email, name: u.name } }
      }

      const base = apiBase()
      try {
        const csrfRes = await fetch(base + '/api/csrf/', { credentials: 'include' })
        const csrfData = await csrfRes.json().catch(() => ({}))
        const csrftoken = getCookie('csrftoken') || csrfData.csrfToken

        const res = await fetch(base + '/api/auth/login/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
          },
          credentials: 'include',
          body: JSON.stringify({ identifier: email, password }),
        })

        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          return { ok: false, error: err.error || err.detail || 'Login failed' }
        }

        const data = await res.json()
        this.setAuth(data, null)
        return { ok: true, data }
      } catch (e) {
        return { ok: false, error: String(e) }
      }
    },

    async signup(payload: any) {
      if (useLocalAuth()) {
        const exists = users.find((u) => u.email.toLowerCase() === payload.email?.toLowerCase())
        if (exists) return { ok: false, error: { error: 'User already exists' } }
        const nextId = users.reduce((m, x) => Math.max(m, x.id), 0) + 1
        users.push({ id: nextId, email: payload.email, password: payload.password, name: payload.username })
        this.setAuth({ id: nextId, email: payload.email, name: payload.username }, 'local')
        return { ok: true, data: { id: nextId, email: payload.email, name: payload.username } }
      }

      const base = apiBase()
      try {
        const csrfRes = await fetch(base + '/api/csrf/', { credentials: 'include' })
        const csrfData = await csrfRes.json().catch(() => ({}))
        const csrftoken = getCookie('csrftoken') || csrfData.csrfToken
        
        const headers: Record<string, string> = {
            ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
        }

        let body
        if (payload instanceof FormData) {
            body = payload
            // browser sets content-type with boundary automatically for FormData
        } else {
            headers['Content-Type'] = 'application/json'
            body = JSON.stringify(payload)
        }

        const res = await fetch(base + '/api/auth/signup/', {
          method: 'POST',
          headers,
          credentials: 'include',
          body,
        })
        if (!res.ok) {
          const err = await res.json().catch(() => ({}))
          return { ok: false, error: err }
        }
        const data = await res.json()
        this.setAuth(data, null)
        return { ok: true, data }
      } catch (e) {
        return { ok: false, error: e }
      }
    },

    setAuth(user: any, token?: string | null) {
      this.user = user
      this.token = token ?? null
      this.isAuthenticated = true
    },

    async fetchProfile() {
      if (useLocalAuth()) {
        return this.user
      }
      const base = apiBase()
      try {
        const res = await fetch(base + '/api/auth/me/', { credentials: 'include' })
        if (!res.ok) return null
        const data = await res.json()
        this.setAuth(data, null)
        return data
      } catch (e) {
        return null
      }
    },

    async logout() {
      if (useLocalAuth()) {
        this.clearAuth()
        return
      }
      const base = apiBase()
      try {
        const csrfRes = await fetch(base + '/api/csrf/', { credentials: 'include' })
        const csrfData = await csrfRes.json().catch(() => ({}))
        const csrftoken = getCookie('csrftoken') || csrfData.csrfToken

        await fetch(base + '/api/auth/logout/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
          },
          credentials: 'include',
        })
      } catch (e) {
        // ignore
      }
      this.clearAuth()
    },

    clearAuth() {
      this.user = null
      this.token = null
      this.isAuthenticated = false
    },

    // Update profile fields locally (e.g., name)
    updateProfile(partial: Partial<User>) {
      if (!this.user) return
      this.user = { ...this.user, ...partial }
    },

    // Guardian: give access to a managed member
    async giveAccess(profileId: number, username: string, password: string) {
      const base = apiBase()
      try {
        const csrfRes = await fetch(base + '/api/csrf/', { credentials: 'include' })
        const csrfData = await csrfRes.json().catch(() => ({}))
        const csrftoken = getCookie('csrftoken') || csrfData.csrfToken

        const res = await fetch(base + '/api/auth/give-access/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
          },
          credentials: 'include',
          body: JSON.stringify({ profile_id: profileId, username, password }),
        })
        const data = await res.json()
        if (!res.ok) return { ok: false, error: data.error || 'Failed' }
        await this.fetchProfile() // Refresh managed_members
        return { ok: true, data }
      } catch (e) {
        return { ok: false, error: String(e) }
      }
    },

    // Claim account with a claim token
    async claimAccount(token: string, newPassword?: string) {
      const base = apiBase()
      try {
        const csrfRes = await fetch(base + '/api/csrf/', { credentials: 'include' })
        const csrfData = await csrfRes.json().catch(() => ({}))
        const csrftoken = getCookie('csrftoken') || csrfData.csrfToken

        const res = await fetch(base + '/api/auth/claim/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
          },
          credentials: 'include',
          body: JSON.stringify({ token, new_password: newPassword }),
        })
        const data = await res.json()
        if (!res.ok) return { ok: false, error: data.error || 'Claim failed' }
        this.setAuth(data, null)
        return { ok: true, data }
      } catch (e) {
        return { ok: false, error: String(e) }
      }
    },

    // Go independent — revoke guardian access
    async goIndependent() {
      const base = apiBase()
      try {
        const csrfRes = await fetch(base + '/api/csrf/', { credentials: 'include' })
        const csrfData = await csrfRes.json().catch(() => ({}))
        const csrftoken = getCookie('csrftoken') || csrfData.csrfToken

        const res = await fetch(base + '/api/auth/go-independent/', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            ...(csrftoken ? { 'X-CSRFToken': csrftoken } : {}),
          },
          credentials: 'include',
        })
        const data = await res.json()
        if (!res.ok) return { ok: false, error: data.error || 'Failed' }
        await this.fetchProfile()
        return { ok: true, data }
      } catch (e) {
        return { ok: false, error: String(e) }
      }
    },
  },

  persist: true, // 🔑 persistence
})
