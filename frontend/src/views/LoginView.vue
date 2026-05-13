<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useAuthStore } from '../stores/auth'

const router = useRouter()
const route = useRoute()
const authStore = useAuthStore()

const username = ref('')
const password = ref('')
const error = ref('')
const loading = ref(false)

async function handleLogin() {
  if (!username.value.trim() || !password.value) return
  error.value = ''
  loading.value = true
  try {
    await authStore.login(username.value.trim(), password.value)
    const redirect = (route.query.redirect as string) || '/'
    router.push(redirect)
  } catch (e: unknown) {
    error.value = e instanceof Error ? e.message : '登入失敗，請再試一次'
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="h-dvh overflow-hidden bg-washi flex flex-col items-center justify-center px-5">
    <!-- Decorative sakura petals -->
    <div aria-hidden="true" class="pointer-events-none fixed inset-0 overflow-hidden">
      <svg class="absolute top-32 left-6 text-sakura-200 opacity-30" width="140" height="140" viewBox="0 0 24 24" fill="currentColor">
        <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
        <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
        <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
        <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
        <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
      </svg>
      <svg class="absolute bottom-16 right-8 text-sakura-300 opacity-20" width="90" height="90" viewBox="0 0 24 24" fill="currentColor" style="transform: rotate(25deg)">
        <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
        <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
        <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
        <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
        <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
      </svg>
    </div>

    <!-- Card -->
    <div class="relative w-full max-w-sm">
      <!-- Logo -->
      <div class="text-center mb-8">
        <router-link to="/" class="inline-flex flex-col items-center gap-2 group">
          <svg class="text-sakura-400 transition-transform duration-500 group-hover:rotate-45" width="36" height="36" viewBox="0 0 24 24" fill="currentColor">
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
            <circle cx="12" cy="12" r="2.5" fill="#FAF7F2" />
            <circle cx="12" cy="12" r="1.2" fill="currentColor" opacity="0.6" />
          </svg>
          <span class="font-mincho text-2xl text-sumi tracking-wide">桜探記</span>
        </router-link>
        <p class="mt-2 text-xs tracking-widest text-sakura-400 uppercase">Japan Journey Journal</p>
      </div>

      <!-- Form -->
      <div class="bg-white rounded-2xl shadow-sm border border-sakura-100 px-6 py-7">
        <h1 class="text-base font-medium text-sumi mb-5 text-center">登入帳號</h1>

        <form @submit.prevent="handleLogin" class="space-y-4">
          <!-- Username -->
          <div>
            <label class="block text-xs text-stone-500 mb-1.5">用戶名</label>
            <input
              v-model="username"
              type="text"
              autocomplete="username"
              placeholder="請輸入用戶名"
              class="w-full bg-washi border border-sakura-100 rounded-xl px-4 py-2.5
                     text-sm text-sumi placeholder-stone-400
                     focus:outline-none focus:border-sakura-300 focus:ring-2 focus:ring-sakura-100
                     transition-all"
            />
          </div>

          <!-- Password -->
          <div>
            <label class="block text-xs text-stone-500 mb-1.5">密碼</label>
            <input
              v-model="password"
              type="password"
              autocomplete="current-password"
              placeholder="請輸入密碼"
              class="w-full bg-washi border border-sakura-100 rounded-xl px-4 py-2.5
                     text-sm text-sumi placeholder-stone-400
                     focus:outline-none focus:border-sakura-300 focus:ring-2 focus:ring-sakura-100
                     transition-all"
            />
          </div>

          <!-- Error message -->
          <p v-if="error" class="text-xs text-red-500 text-center">{{ error }}</p>

          <!-- Submit -->
          <button
            type="submit"
            :disabled="loading || !username.trim() || !password"
            class="w-full py-2.5 rounded-xl text-sm font-medium text-white transition-all duration-200
                   disabled:opacity-50 disabled:cursor-not-allowed"
            :style="{ background: 'linear-gradient(135deg, #EEA0B8 0%, #D9506F 100%)' }"
          >
            <span v-if="loading" class="inline-flex items-center gap-2">
              <svg class="animate-spin" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
              </svg>
              登入中…
            </span>
            <span v-else>登入</span>
          </button>
        </form>
      </div>

      <!-- Back link -->
      <p class="text-center mt-5 text-xs text-stone-400">
        <router-link to="/" class="hover:text-sakura-500 transition-colors">← 返回首頁</router-link>
      </p>
    </div>
  </div>
</template>
