import { defineStore } from 'pinia'
import { api } from '../api'

export const useAuth = defineStore('auth', {
  state: () => ({ user: null, ready: false }),
  getters: { loggedIn: (s) => !!s.user },
  actions: {
    async init() {
      if (localStorage.getItem('token')) {
        try {
          this.user = await api('/auth/me/')
        } catch {
          localStorage.removeItem('token')
        }
      }
      this.ready = true
    },
    async _auth(path, body) {
      const { token, user } = await api(path, { method: 'POST', body })
      localStorage.setItem('token', token)
      this.user = user
    },
    login(email, password) {
      return this._auth('/auth/login/', { email, password })
    },
    register(payload) {
      return this._auth('/auth/register/', payload)
    },
    async logout() {
      try {
        await api('/auth/me/', { method: 'DELETE' })
      } catch {}
      localStorage.removeItem('token')
      this.user = null
    },
  },
})
