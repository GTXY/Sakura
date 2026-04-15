<script setup lang="ts">
import { ref } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import AppNav from './components/AppNav.vue'

const router = useRouter()
const route = useRoute()

const fabHovered = ref(false)
</script>

<template>
  <AppNav />
  <router-view />

  <!-- Floating action button: 只在首頁顯示 -->
  <div v-if="route.name === 'home'" class="fixed bottom-5 right-5 z-50 flex flex-col items-end gap-2">
    <!-- FAB button -->
    <button
      class="relative w-10 h-10 rounded-full shadow-md
             flex items-center justify-center
             transition-transform duration-200 active:scale-90
             focus:outline-none focus-visible:ring-2 focus-visible:ring-sakura-300"
      :class="fabHovered ? 'scale-110' : 'scale-100'"
      aria-label="新增店舖"
      @mouseenter="fabHovered = true"
      @mouseleave="fabHovered = false"
      @focus="fabHovered = true"
      @blur="fabHovered = false"
      @click="router.push('/shops/new')"
    >
      <!-- Gradient background -->
      <span
        class="absolute inset-0 rounded-full"
        :style="{
          background: 'linear-gradient(135deg, #EEA0B8 0%, #D9506F 100%)',
          boxShadow: fabHovered
            ? '0 6px 18px rgba(217,80,111,0.45)'
            : '0 3px 10px rgba(217,80,111,0.30)',
          transition: 'box-shadow 0.2s ease',
        }"
      />

      <!-- Icon: pen nib -->
      <svg
        class="relative z-10 text-white transition-transform duration-300"
        :style="{ transform: fabHovered ? 'rotate(-15deg)' : 'rotate(0deg)' }"
        width="15"
        height="15"
        viewBox="0 0 24 24"
        fill="none"
        stroke="currentColor"
        stroke-width="2.2"
        stroke-linecap="round"
        stroke-linejoin="round"
      >
        <path d="M12 20h9" />
        <path d="M16.5 3.5a2.121 2.121 0 013 3L7 19l-4 1 1-4L16.5 3.5z" />
      </svg>

      <!-- Sakura petal badge -->
      <span
        class="absolute -bottom-0.5 -right-0.5 w-3 h-3 rounded-full
               bg-washi flex items-center justify-center"
      >
        <svg class="text-sakura-300" width="7" height="7" viewBox="0 0 24 24" fill="currentColor">
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
        </svg>
      </span>
    </button>
  </div>
</template>
