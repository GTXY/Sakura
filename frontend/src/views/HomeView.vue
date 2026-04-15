<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import ShopCard from '../components/ShopCard.vue'
import { fetchStats } from '../api/shops'
import type { Stats } from '../api/shops'
import { useInfiniteShops } from '../composables/useInfiniteShops'

type SortKey = 'recent' | 'rating' | 'featured'

const sortKey = ref<SortKey>('recent')
const stats = ref<Stats>({ total: 0, prefectures: 0 })

const sortOptions: { key: SortKey; label: string }[] = [
  { key: 'recent', label: '最新探訪' },
  { key: 'rating', label: '評分最高' },
  { key: 'featured', label: '精選推薦' },
]

const { shops, loading, loadingMore, hasMore, reset, sentinelRef } = useInfiniteShops(
  () => ({ sort: sortKey.value }),
)

// When sort changes, reset to first page
watch(sortKey, reset)

onMounted(() => {
  fetchStats().then((v) => (stats.value = v)).catch(() => {})
})
</script>

<template>
  <div class="min-h-dvh bg-washi">
    <!-- Hero section -->
    <section class="relative overflow-hidden">
      <!-- Decorative sakura petals — fully inside section, no overflow clipping -->
      <div aria-hidden="true" class="pointer-events-none absolute inset-0">
        <!-- Large petal top-left: inset so the full 180px flower is visible -->
        <svg
          class="absolute top-5 left-5 text-sakura-200 opacity-35"
          width="180" height="180" viewBox="0 0 24 24" fill="currentColor"
        >
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
        </svg>
        <!-- Small petal top-right: right-8 keeps 60px flower fully inside -->
        <svg
          class="absolute top-6 right-8 text-sakura-300 opacity-25"
          width="60" height="60" viewBox="0 0 24 24" fill="currentColor"
          style="transform: rotate(30deg)"
        >
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
        </svg>
        <!-- Medium petal right: right-2 keeps 90px flower fully inside -->
        <svg
          class="absolute top-20 right-2 text-sakura-200 opacity-20"
          width="90" height="90" viewBox="0 0 24 24" fill="currentColor"
          style="transform: rotate(-20deg)"
        >
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
        </svg>
      </div>

      <div class="max-w-lg mx-auto px-5 pt-8 pb-6 relative">
        <!-- Subtitle / tagline -->
        <p class="text-xs tracking-widest2 text-sakura-400 uppercase font-medium mb-3 select-none">
          Japan Journey Journal
        </p>

        <h1 class="font-mincho text-3xl text-sumi leading-snug text-balance">
          記錄每一次<br />
          <span class="text-sakura-500">在日本</span>的探訪時光
        </h1>

        <p class="mt-3 text-sm text-stone-500 leading-relaxed">
          去過的神社、泡過的溫泉、吃過的拉麵……<br />
          都在這裡留下印記。
        </p>

        <!-- Stats chips -->
        <div class="flex items-center gap-3 mt-5">
          <div class="flex items-center gap-1.5 bg-white rounded-full px-3.5 py-1.5 shadow-sm border border-sakura-100">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#E57696" stroke-width="2" stroke-linecap="round">
              <path d="M3 9l9-7 9 7v11a2 2 0 01-2 2H5a2 2 0 01-2-2z" />
              <polyline points="9 22 9 12 15 12 15 22" />
            </svg>
            <span class="text-xs text-stone-600 font-medium">{{ stats.total }} 店</span>
          </div>
          <div class="flex items-center gap-1.5 bg-white rounded-full px-3.5 py-1.5 shadow-sm border border-sakura-100">
            <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="#E57696" stroke-width="2" stroke-linecap="round">
              <circle cx="12" cy="10" r="3" />
              <path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" />
            </svg>
            <span class="text-xs text-stone-600 font-medium">{{ stats.prefectures }} 都道府県</span>
          </div>
        </div>
      </div>

      <!-- Bottom fade -->
      <div class="h-px bg-gradient-to-r from-transparent via-sakura-100 to-transparent" />
    </section>

    <!-- Sort tabs -->
    <div class="max-w-lg mx-auto px-5 pt-5 pb-2">
      <div class="flex items-center gap-2">
        <button
          v-for="opt in sortOptions"
          :key="opt.key"
          class="text-xs px-3.5 py-1.5 rounded-full border transition-all duration-200"
          :class="
            sortKey === opt.key
              ? 'bg-sakura-400 border-sakura-400 text-white font-medium shadow-sm'
              : 'border-stone-200 text-stone-500 hover:border-sakura-300 hover:text-sakura-500 bg-white'
          "
          @click="sortKey = opt.key"
        >
          {{ opt.label }}
        </button>
      </div>
    </div>

    <!-- Shop card list -->
    <main class="max-w-lg mx-auto px-5 pt-4 pb-8 space-y-8">
      <!-- First-page loading skeleton -->
      <div v-if="loading" class="space-y-8">
        <div v-for="i in 3" :key="i" class="animate-pulse">
          <div class="aspect-[3/2] rounded-2xl bg-stone-200" />
          <div class="mt-3.5 px-1 space-y-2">
            <div class="h-3 w-24 rounded bg-stone-200" />
            <div class="h-5 w-40 rounded bg-stone-200" />
            <div class="h-3 w-full rounded bg-stone-100" />
          </div>
        </div>
      </div>

      <template v-else>
        <TransitionGroup name="list" tag="div" class="space-y-8">
          <ShopCard
            v-for="shop in shops"
            :key="shop.id"
            :shop="shop"
          />
        </TransitionGroup>

        <!-- Sentinel: intersection triggers next page -->
        <div ref="sentinelRef" class="h-px" />

        <!-- Loading more indicator -->
        <div v-if="loadingMore" class="flex justify-center py-4">
          <svg class="animate-spin text-sakura-300" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
          </svg>
        </div>

        <!-- End of list -->
        <div v-if="!hasMore && shops.length" class="flex flex-col items-center gap-1.5 py-4 text-stone-400">
          <svg class="text-sakura-200" width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
          </svg>
          <p class="text-xs">已顯示全部 {{ shops.length }} 間店舖</p>
        </div>
      </template>
    </main>

    <!-- Footer -->
    <footer class="text-center py-8 text-xs text-stone-400 space-y-1 border-t border-sakura-100">
      <div class="flex justify-center">
        <svg class="text-sakura-300" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
          <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
        </svg>
      </div>
      <p>桜探記 · 個人探店檔案</p>
    </footer>
  </div>
</template>

<style scoped>
.list-move,
.list-enter-active,
.list-leave-active {
  transition: all 0.35s ease;
}
.list-enter-from,
.list-leave-to {
  opacity: 0;
  transform: translateY(12px);
}
</style>
