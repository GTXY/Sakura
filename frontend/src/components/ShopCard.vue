<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Shop } from '../types/shop'

const props = defineProps<{ shop: Shop }>()
const router = useRouter()

function onImgError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = `https://picsum.photos/seed/${props.shop.id}/800/600`
}

function formatDate(dateStr: string) {
  const d = new Date(dateStr)
  return `${d.getFullYear()} · ${String(d.getMonth() + 1).padStart(2, '0')} · ${String(d.getDate()).padStart(2, '0')}`
}

function goTag(e: Event) {
  e.preventDefault()
  e.stopPropagation()
  router.push({ path: '/shops', query: { type: props.shop.category } })
}

function goPref(e: Event) {
  e.preventDefault()
  e.stopPropagation()
  router.push({ path: '/shops', query: { pref: props.shop.prefecture } })
}
</script>

<template>
  <article class="group cursor-pointer">
    <router-link :to="`/shops/${shop.id}`" class="block">
      <!-- Image -->
      <div class="relative overflow-hidden rounded-2xl bg-stone-100 aspect-[3/2]">
        <img
          :src="shop.coverImage"
          :alt="shop.name"
          loading="lazy"
          class="w-full h-full object-cover transition-transform duration-700 ease-out
                 group-hover:scale-105"
          @error="onImgError"
        />

        <!-- Rating badge -->
        <div
          class="absolute top-3 right-3 flex items-center gap-1
                 bg-white/90 backdrop-blur-sm rounded-full
                 px-2.5 py-1 text-xs font-medium text-sumi shadow-sm"
        >
          <svg width="11" height="11" viewBox="0 0 24 24" fill="#E57696">
            <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
          </svg>
          <span>{{ shop.rating.toFixed(1) }}</span>
        </div>

        <!-- Featured ribbon -->
        <div v-if="shop.featured" class="absolute top-3 left-3">
          <span class="badge bg-sakura-400/90 text-white backdrop-blur-sm text-[10px] tracking-widest">
            精選
          </span>
        </div>
      </div>

      <!-- Info -->
      <div class="mt-3.5 px-1">
        <!-- Tags (no category on homepage) -->
        <div class="flex items-center flex-wrap gap-1.5 mb-2">
          <span
            v-if="shop.tag"
            class="badge bg-stone-100 text-stone-500 cursor-pointer
                   hover:bg-stone-200 hover:text-stone-700 transition-colors"
            @click="goTag"
          >{{ shop.tag }}</span>
          <span
            class="badge-pref cursor-pointer hover:bg-stone-200 hover:text-stone-700 transition-colors"
            @click="goPref"
          >{{ shop.prefecture }}</span>
        </div>

        <!-- Shop name -->
        <h2 class="font-mincho text-[1.15rem] font-semibold text-sumi leading-snug
                   group-hover:text-sakura-600 transition-colors duration-200">
          {{ shop.name }}
        </h2>
        <!-- One-liner -->
        <p class="mt-2.5 text-sm text-stone-600 leading-relaxed line-clamp-2 text-balance">
          {{ shop.oneLiner }}
        </p>

        <!-- Footer row -->
        <div class="flex items-center justify-between mt-3 text-xs text-stone-400">
          <span>{{ formatDate(shop.visitDate) }}</span>
          <span class="flex items-center gap-1 text-sakura-400">
            <svg width="10" height="10" viewBox="0 0 24 24" fill="currentColor">
              <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" />
              <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(72 12 12)" />
              <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(144 12 12)" />
              <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(216 12 12)" />
              <ellipse cx="12" cy="5.5" rx="2.6" ry="4.5" transform="rotate(288 12 12)" />
            </svg>
            探訪記錄
          </span>
        </div>
      </div>
    </router-link>

    <!-- Divider -->
    <div class="mt-6 h-px bg-gradient-to-r from-transparent via-sakura-100 to-transparent" />
  </article>
</template>
