<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CATEGORIES, CATEGORY_ICON } from '../types/shop'
import { fetchShops } from '../api/shops'
import { useInfiniteShops } from '../composables/useInfiniteShops'
import MasonryCard from '../components/MasonryCard.vue'

const route = useRoute()
const router = useRouter()

const activeSearch = ref<string>((route.query.q as string) || '')
const filterMode = ref<'search' | 'type' | 'pref'>(
  route.query.q ? 'search' : route.query.pref ? 'pref' : 'type',
)
const activeType = ref<string>((route.query.type as string) || '')
const activePref = ref<string>((route.query.pref as string) || '')

// Prefecture list for filter chips — loaded once from full dataset
const allPrefs = ref<string[]>([])

const { shops, loading, loadingMore, hasMore, reset, sentinelRef } = useInfiniteShops(() => ({
  search: activeSearch.value || undefined,
  category: activeType.value || undefined,
  pref: activePref.value || undefined,
}))

onMounted(async () => {
  if (allPrefs.value.length === 0) {
    try {
      const all = await fetchShops({ limit: 200, offset: 0 })
      allPrefs.value = [...new Set(all.map((s) => s.prefecture))]
    } catch { /* ignore */ }
  }
})

watch(
  () => route.query,
  (q) => {
    if (q.q) {
      filterMode.value = 'search'
      activeSearch.value = (q.q as string) || ''
      activeType.value = ''
      activePref.value = ''
    } else if (q.pref) {
      filterMode.value = 'pref'
      activePref.value = (q.pref as string) || ''
      activeSearch.value = ''
      activeType.value = ''
    } else {
      filterMode.value = 'type'
      activeType.value = (q.type as string) || ''
      activePref.value = ''
      activeSearch.value = ''
    }
    reset()
  },
)

const filterLabel = () =>
  activeSearch.value ? `"${activeSearch.value}"` : activeType.value || activePref.value || '全部'

function setType(t: string) {
  const next = t === activeType.value ? '' : t
  activeType.value = next
  router.replace({ path: '/shops', query: next ? { type: next } : {} })
}

function setPref(p: string) {
  const next = p === activePref.value ? '' : p
  activePref.value = next
  router.replace({ path: '/shops', query: next ? { pref: next } : {} })
}
</script>

<template>
  <div class="min-h-dvh bg-washi">

    <!-- Header -->
    <div class="px-5 pt-4 pb-3 max-w-lg mx-auto">
      <div class="flex items-center gap-3">
        <button
          class="flex items-center justify-center w-6 h-6 rounded-full shrink-0
                 bg-white border border-stone-200 shadow-sm
                 text-stone-400 hover:text-sakura-500 hover:border-sakura-200 transition-colors"
          aria-label="返回"
          @click="router.back()"
        >
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor"
               stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="15 18 9 12 15 6" />
          </svg>
        </button>

        <div class="flex items-baseline gap-2 min-w-0">
          <h1 class="font-mincho text-xl font-semibold text-sumi truncate">{{ filterLabel() }}</h1>
          <span class="text-xs text-stone-400 shrink-0">{{ shops.length }} 間</span>
        </div>
      </div>
    </div>

    <!-- Filter chips — type mode (all categories) -->
    <div v-if="filterMode === 'type'" class="max-w-lg mx-auto px-5 mb-4">
      <div class="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
        <button
          v-for="cat in CATEGORIES"
          :key="cat"
          class="shrink-0 flex items-center gap-1.5 text-xs px-3.5 py-1.5 rounded-full border transition-all duration-150"
          :class="activeType === cat
            ? 'bg-sakura-400 border-sakura-400 text-white font-medium shadow-sm'
            : 'bg-white border-stone-200 text-stone-500 hover:border-sakura-300 hover:text-sakura-500'"
          @click="setType(cat)"
        >
          <span>{{ CATEGORY_ICON[cat] }}</span>
          <span>{{ cat }}</span>
        </button>
      </div>
    </div>

    <!-- Filter chips — pref mode -->
    <div v-else-if="filterMode === 'pref'" class="max-w-lg mx-auto px-5 mb-4">
      <div class="flex gap-2 overflow-x-auto pb-1 scrollbar-none">
        <button
          v-for="p in allPrefs"
          :key="p"
          class="shrink-0 text-xs px-3.5 py-1.5 rounded-full border transition-all duration-150"
          :class="activePref === p
            ? 'bg-sumi border-sumi text-white font-medium shadow-sm'
            : 'bg-white border-stone-200 text-stone-500 hover:border-stone-400 hover:text-stone-700'"
          @click="setPref(p)"
        >{{ p }}</button>
      </div>
    </div>

    <!-- Divider -->
    <div class="max-w-lg mx-auto mx-5 h-px bg-gradient-to-r from-transparent via-sakura-100 to-transparent mb-4" />

    <!-- Grid -->
    <main class="max-w-lg mx-auto px-3 pb-8">
      <!-- First-page loading skeleton -->
      <div v-if="loading" class="grid grid-cols-2 gap-3">
        <div v-for="i in 6" :key="i" class="animate-pulse aspect-[3/4] rounded-2xl bg-stone-200" />
      </div>

      <template v-else>
        <!-- Empty state -->
        <div v-if="!shops.length" class="flex flex-col items-center justify-center py-24 gap-3 text-stone-400">
          <svg class="text-sakura-200" width="44" height="44" viewBox="0 0 24 24" fill="currentColor">
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
            <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
          </svg>
          <p class="text-sm">暫無符合條件的店舖</p>
        </div>

        <TransitionGroup
          v-else
          name="fade"
          tag="div"
          class="grid grid-cols-2 gap-3"
        >
          <MasonryCard
            v-for="shop in shops"
            :key="shop.id"
            :shop="shop"
          />
        </TransitionGroup>

        <!-- Sentinel -->
        <div ref="sentinelRef" class="h-px mt-3" />

        <!-- Loading more -->
        <div v-if="loadingMore" class="grid grid-cols-2 gap-3 mt-3">
          <div v-for="i in 2" :key="i" class="animate-pulse aspect-[3/4] rounded-2xl bg-stone-200" />
        </div>

        <!-- End of list -->
        <div v-if="!hasMore && shops.length" class="flex flex-col items-center gap-1.5 py-6 text-stone-400">
          <svg class="text-sakura-200" width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
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

  </div>
</template>

<style scoped>
.scrollbar-none {
  scrollbar-width: none;
}
.scrollbar-none::-webkit-scrollbar {
  display: none;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(6px);
}
</style>
