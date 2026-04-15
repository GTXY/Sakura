<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const searchOpen = ref(false)
const searchQuery = ref('')

function submitSearch() {
  if (!searchQuery.value.trim()) return
  router.push({ path: '/shops', query: { q: searchQuery.value.trim() } })
  searchOpen.value = false
  searchQuery.value = ''
}
</script>

<template>
  <header class="sticky top-0 z-50 bg-washi/95 backdrop-blur-md">
    <!-- thin sakura top border -->
    <div class="h-px bg-gradient-to-r from-transparent via-sakura-300 to-transparent" />

    <div class="max-w-lg mx-auto px-5">
      <!-- Main nav row -->
      <div class="flex items-center justify-between h-14">
        <!-- Logo -->
        <router-link
          to="/"
          class="flex items-center gap-2.5 group"
          aria-label="桜探記 首頁"
        >
          <!-- Sakura SVG icon -->
          <svg
            width="22"
            height="22"
            viewBox="0 0 24 24"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
            class="text-sakura-400 transition-transform duration-500 group-hover:rotate-45"
          >
            <!-- Cherry blossom: 5 petals -->
            <g fill="currentColor">
              <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
              <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
              <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
              <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
              <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
              <circle cx="12" cy="12" r="2.5" fill="#FAF7F2" />
              <circle cx="12" cy="12" r="1.2" fill="currentColor" opacity="0.6" />
            </g>
          </svg>

          <span class="font-mincho text-xl text-sumi tracking-wide leading-none select-none">
            桜探記
          </span>
        </router-link>

        <!-- Right actions -->
        <div class="flex items-center gap-1">
          <button
            class="btn-icon"
            aria-label="搜尋"
            @click="searchOpen = !searchOpen"
          >
            <svg
              v-if="!searchOpen"
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
              stroke-linejoin="round"
            >
              <circle cx="11" cy="11" r="7" />
              <line x1="16.5" y1="16.5" x2="22" y2="22" />
            </svg>
            <svg
              v-else
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              stroke-width="1.8"
              stroke-linecap="round"
            >
              <line x1="18" y1="6" x2="6" y2="18" />
              <line x1="6" y1="6" x2="18" y2="18" />
            </svg>
          </button>
        </div>
      </div>

      <!-- Expandable search bar -->
      <Transition
        enter-active-class="transition-all duration-200 ease-out"
        enter-from-class="opacity-0 -translate-y-1"
        enter-to-class="opacity-100 translate-y-0"
        leave-active-class="transition-all duration-150 ease-in"
        leave-from-class="opacity-100 translate-y-0"
        leave-to-class="opacity-0 -translate-y-1"
      >
        <div v-if="searchOpen" class="pb-4">
          <form @submit.prevent="submitSearch" class="relative">
            <input
              v-model="searchQuery"
              type="text"
              placeholder="搜尋店舖、城市、類型…"
              autofocus
              class="w-full bg-white border border-sakura-100 rounded-xl
                     px-4 py-2.5 pr-20 text-sm text-sumi placeholder-stone-400
                     focus:outline-none focus:border-sakura-300 focus:ring-2
                     focus:ring-sakura-100 transition-all"
            />
            <!-- Clear button -->
            <button
              v-if="searchQuery"
              type="button"
              class="absolute right-9 top-1/2 -translate-y-1/2 text-stone-300 hover:text-sakura-400 transition-colors"
              aria-label="清除"
              @click="searchQuery = ''"
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
            <!-- Submit button -->
            <button
              type="submit"
              class="absolute right-3 top-1/2 -translate-y-1/2 text-stone-400 hover:text-sakura-500 transition-colors"
              aria-label="搜尋"
            >
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <circle cx="11" cy="11" r="7" /><line x1="16.5" y1="16.5" x2="22" y2="22" />
              </svg>
            </button>
          </form>
        </div>
      </Transition>
    </div>

    <!-- Bottom border -->
    <div class="h-px bg-sakura-100" />
  </header>
</template>
