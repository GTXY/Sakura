<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { CATEGORY_ICON } from '../types/shop'
import type { Shop } from '../types/shop'
import { fetchShop } from '../api/shops'
import ShopMap from '../components/ShopMap.vue'

const route = useRoute()
const router = useRouter()

const shop = ref<Shop | null>(null)
const loading = ref(true)
const notFound = ref(false)

onMounted(async () => {
  try {
    shop.value = await fetchShop(route.params.id as string)
  } catch {
    notFound.value = true
  } finally {
    loading.value = false
  }
})

const lightboxIndex = ref<number | null>(null)

function openLightbox(i: number) { lightboxIndex.value = i }
function closeLightbox() { lightboxIndex.value = null }
function prevPhoto() {
  if (lightboxIndex.value === null || !shop.value) return
  lightboxIndex.value = (lightboxIndex.value - 1 + shop.value.photos.length) % shop.value.photos.length
}
function nextPhoto() {
  if (lightboxIndex.value === null || !shop.value) return
  lightboxIndex.value = (lightboxIndex.value + 1) % shop.value.photos.length
}

function onImgError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = `https://picsum.photos/seed/${shop.value?.id}/800/600`
}

const ratingFull = computed(() => Math.floor(shop.value?.rating ?? 0))
const ratingHalf = computed(() => ((shop.value?.rating ?? 0) % 1) >= 0.5)
</script>

<template>
  <!-- Loading -->
  <div v-if="loading" class="min-h-dvh bg-washi flex items-center justify-center">
    <div class="flex flex-col items-center gap-3 text-stone-400">
      <svg class="animate-spin text-sakura-300" width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4M4.93 19.07l2.83-2.83M16.24 7.76l2.83-2.83"/>
      </svg>
      <span class="text-sm">載入中…</span>
    </div>
  </div>

  <div v-else-if="shop" class="min-h-dvh bg-washi pb-16">

    <!-- Hero image -->
    <div class="relative h-72 overflow-hidden">
      <img
        :src="shop.coverImage"
        :alt="shop.name"
        class="w-full h-full object-cover"
        @error="onImgError"
      />
      <!-- gradient overlay -->
      <div class="absolute inset-0 bg-gradient-to-b from-black/30 via-transparent to-transparent" />

      <!-- Back button -->
      <button
        class="absolute top-4 left-4 w-8 h-8 rounded-full
               bg-white/80 backdrop-blur-sm shadow-sm
               flex items-center justify-center
               text-stone-600 hover:text-sakura-500 transition-colors"
        @click="router.back()"
      >
        <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor"
             stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
          <polyline points="15 18 9 12 15 6" />
        </svg>
      </button>

      <!-- Featured badge -->
      <div v-if="shop.featured" class="absolute top-4 right-4">
        <span class="badge bg-sakura-400/90 text-white backdrop-blur-sm text-[10px] tracking-widest">精選</span>
      </div>
    </div>

    <!-- Content -->
    <div class="max-w-lg mx-auto px-5">

      <!-- Name, badges & rating -->
      <div class="pt-5 pb-4">

        <!-- Category + address row: left plain text, right address -->
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center gap-1.5">
            <span class="text-base leading-none">{{ CATEGORY_ICON[shop.category] }}</span>
            <span class="text-xs font-medium text-sakura-600">{{ shop.category }}</span>
            <span v-if="shop.tag" class="text-stone-300 text-[10px]">·</span>
            <span v-if="shop.tag" class="text-xs text-stone-500">{{ shop.tag }}</span>
          </div>
          <span class="text-xs text-stone-400">{{ shop.prefecture }} · {{ shop.city }}</span>
        </div>

        <!-- Title row: name + rating number side by side -->
        <div class="flex items-start justify-between gap-3">
          <h1 class="font-mincho text-2xl font-semibold text-sumi leading-tight min-w-0">{{ shop.name }}</h1>
          <!-- Rating block -->
          <div class="shrink-0 flex flex-col items-center gap-0.5 pt-0.5">
            <span class="font-mincho text-2xl font-semibold text-sumi leading-none">{{ shop.rating.toFixed(1) }}</span>
            <div class="flex items-center gap-px">
              <svg
                v-for="i in 5" :key="i"
                width="12" height="12" viewBox="0 0 24 24"
                :fill="i <= ratingFull ? '#E57696' : (i === ratingFull + 1 && ratingHalf ? 'url(#half)' : '#E5E7EB')"
              >
                <defs>
                  <linearGradient id="half">
                    <stop offset="50%" stop-color="#E57696"/>
                    <stop offset="50%" stop-color="#E5E7EB"/>
                  </linearGradient>
                </defs>
                <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
              </svg>
            </div>
          </div>
        </div>
      </div>

      <div class="h-px bg-gradient-to-r from-transparent via-sakura-100 to-transparent mb-5" />

      <!-- My review -->
      <div class="mb-5">
        <p class="text-[11px] text-stone-400 uppercase tracking-widest mb-3">我的評價</p>
        <p class="text-sm text-stone-700 leading-loose">{{ shop.description }}</p>
        <p class="text-xs text-stone-400 mt-3">探訪日期：{{ shop.visitDate.replace(/-/g, ' · ') }}</p>
      </div>

      <div class="h-px bg-sakura-50 mb-5" />

      <!-- Photo gallery -->
      <div class="mb-5">
        <p class="text-[11px] text-stone-400 uppercase tracking-widest mb-3">探訪相片</p>
        <div class="grid grid-cols-3 gap-2">
          <button
            v-for="(photo, i) in shop.photos"
            :key="i"
            class="relative aspect-square overflow-hidden rounded-xl bg-stone-100 group"
            @click="openLightbox(i)"
          >
            <img
              :src="photo"
              :alt="`${shop.name} 相片 ${i + 1}`"
              loading="lazy"
              class="w-full h-full object-cover transition-transform duration-500 group-hover:scale-110"
              @error="onImgError"
            />
          </button>
        </div>
      </div>

      <div class="h-px bg-sakura-50 mb-5" />

      <!-- Info card -->
      <div class="mb-5 bg-white rounded-2xl border border-sakura-50 shadow-sm overflow-hidden">
        <!-- Address -->
        <div v-if="shop.address" class="flex items-center gap-3 px-4 py-3.5 border-b border-stone-50">
          <div class="w-8 h-8 rounded-full bg-sakura-50 flex items-center justify-center shrink-0">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#E57696" stroke-width="2" stroke-linecap="round">
              <circle cx="12" cy="10" r="3"/><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
            </svg>
          </div>
          <div>
            <p class="text-[10px] text-stone-400 tracking-wide mb-0.5">地址</p>
            <p class="text-sm text-sumi font-medium leading-snug">
              {{ shop.prefecture }}{{ shop.city }}{{ shop.address }}
            </p>
          </div>
        </div>
        <div v-else class="flex items-center gap-3 px-4 py-3.5 border-b border-stone-50">
          <div class="w-8 h-8 rounded-full bg-sakura-50 flex items-center justify-center shrink-0">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#E57696" stroke-width="2" stroke-linecap="round">
              <circle cx="12" cy="10" r="3"/><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
            </svg>
          </div>
          <div>
            <p class="text-[10px] text-stone-400 tracking-wide mb-0.5">地址</p>
            <p class="text-sm text-sumi font-medium">{{ shop.prefecture }} {{ shop.city }}</p>
          </div>
        </div>
        <div v-if="shop.phone" class="flex items-center gap-3 px-4 py-3.5 border-b border-stone-50">
          <div class="w-8 h-8 rounded-full bg-sakura-50 flex items-center justify-center shrink-0">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#E57696" stroke-width="2" stroke-linecap="round">
              <path d="M22 16.92v3a2 2 0 01-2.18 2 19.79 19.79 0 01-8.63-3.07A19.5 19.5 0 013.07 9.8 19.79 19.79 0 0117.45 2a2 2 0 012 1.72 12.84 12.84 0 00.7 2.81 2 2 0 01-.45 2.11L18.09 9.91a16 16 0 006.29 6.29l1.27-1.27a2 2 0 012.11-.45 12.84 12.84 0 002.81.7A2 2 0 0122 16.92z"/>
            </svg>
          </div>
          <div>
            <p class="text-[10px] text-stone-400 tracking-wide mb-0.5">電話</p>
            <a :href="`tel:${shop.phone}`" class="text-sm text-sumi font-medium hover:text-sakura-500 transition-colors">
              {{ shop.phone }}
            </a>
          </div>
        </div>
        <div v-if="shop.hours" class="flex items-center gap-3 px-4 py-3.5">
          <div class="w-8 h-8 rounded-full bg-sakura-50 flex items-center justify-center shrink-0">
            <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="#E57696" stroke-width="2" stroke-linecap="round">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
          </div>
          <div>
            <p class="text-[10px] text-stone-400 tracking-wide mb-0.5">營業時間</p>
            <p class="text-sm text-sumi font-medium">{{ shop.hours }}</p>
          </div>
        </div>
      </div>

      <!-- Map -->
      <div class="mb-5">
        <p class="text-[11px] text-stone-400 uppercase tracking-widest mb-3">位置</p>
        <ShopMap :lat="shop.lat" :lng="shop.lng" :name="shop.name" />
      </div>

    </div>

    <!-- Lightbox -->
    <Teleport to="body">
      <Transition
        enter-active-class="transition-opacity duration-200"
        enter-from-class="opacity-0"
        leave-active-class="transition-opacity duration-200"
        leave-to-class="opacity-0"
      >
        <div
          v-if="lightboxIndex !== null"
          class="fixed inset-0 z-[100] bg-black/75 flex items-center justify-center"
          @click.self="closeLightbox"
        >
          <!-- Close -->
          <button
            class="absolute top-5 right-5 w-9 h-9 rounded-full bg-white/10
                   flex items-center justify-center text-white hover:bg-white/20 transition-colors"
            @click="closeLightbox"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>

          <!-- Prev -->
          <button
            v-if="shop.photos.length > 1"
            class="absolute left-4 w-9 h-9 rounded-full bg-white/10
                   flex items-center justify-center text-white hover:bg-white/20 transition-colors"
            @click="prevPhoto"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>

          <!-- Image -->
          <img
            :src="shop.photos[lightboxIndex]"
            :alt="shop.name"
            class="max-w-[calc(100vw-5rem)] max-h-[85dvh] object-contain rounded-lg select-none"
          />

          <!-- Next -->
          <button
            v-if="shop.photos.length > 1"
            class="absolute right-4 w-9 h-9 rounded-full bg-white/10
                   flex items-center justify-center text-white hover:bg-white/20 transition-colors"
            @click="nextPhoto"
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
              <polyline points="9 18 15 12 9 6"/>
            </svg>
          </button>

          <!-- Counter -->
          <p class="absolute bottom-6 left-1/2 -translate-x-1/2 text-xs text-white/60">
            {{ lightboxIndex + 1 }} / {{ shop.photos.length }}
          </p>
        </div>
      </Transition>
    </Teleport>
  </div>

  <!-- 404 -->
  <div v-else-if="notFound" class="min-h-dvh bg-washi flex flex-col items-center justify-center gap-4 text-stone-400">
    <svg class="text-sakura-200" width="48" height="48" viewBox="0 0 24 24" fill="currentColor">
      <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
      <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
      <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
      <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
      <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
    </svg>
    <p class="text-sm">找不到該店舖</p>
    <button class="text-xs text-sakura-500 underline underline-offset-2" @click="router.push('/')">返回首頁</button>
  </div>
</template>
