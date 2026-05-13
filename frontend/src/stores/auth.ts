import { defineStore } from 'pinia'
import { computed, ref } from 'vue'

const API_BASE = `${import.meta.env.BASE_URL}api`

export interface AuthUser {
  id: string
  username: string
}

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('sakura_token'))
  const user = ref<AuthUser | null>(null)

  const isLoggedIn = computed(() => !!token.value)

  async function login(username: string, password: string): Promise<void> {
    const res = await fetch(`${API_BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username, password }),
    })
    if (!res.ok) {
      const data = await res.json().catch(() => ({}))
      throw new Error(data.detail || '登入失敗')
    }
    const data = await res.json()
    token.value = data.access_token
    localStorage.setItem('sakura_token', data.access_token)
    await fetchMe()
  }

  async function fetchMe(): Promise<void> {
    if (!token.value) return
    const res = await fetch(`${API_BASE}/auth/me`, {
      headers: { Authorization: `Bearer ${token.value}` },
    })
    if (res.ok) {
      user.value = await res.json()
    } else {
      logout()
    }
  }

  function logout(): void {
    token.value = null
    user.value = null
    localStorage.removeItem('sakura_token')
  }

  // Restore user info on app startup
  if (token.value) {
    fetchMe()
  }

  return { token, user, isLoggedIn, login, logout, fetchMe }
})
