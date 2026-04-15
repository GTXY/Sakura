<script setup lang="ts">
import { useRouter } from 'vue-router'
import type { Shop } from '../types/shop'

const props = defineProps<{ shop: Shop }>()
const router = useRouter()

function onImgError(e: Event) {
  const img = e.target as HTMLImageElement
  img.src = `https://picsum.photos/seed/${props.shop.id}/600/800`
}

function goType(e: Event) {
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
  <article class="group">
    <router-link :to="`/shops/${shop.id}`" class="block relative overflow-hidden rounded-2xl bg-stone-100 aspect-[3/4]">
      <!-- Image -->
      <img
        :src="shop.coverImage"
        :alt="shop.name"
        loading="lazy"
        class="w-full h-full object-cover transition-transform duration-700 ease-out group-hover:scale-105"
        @error="onImgError"
      />

      <!-- Gradient overlay -->
      <div class="absolute inset-0 bg-gradient-to-t from-black/75 via-black/10 to-transparent" />

      <!-- Type badge top-left -->
      <div class="absolute top-2.5 left-2.5">
        <span
          class="text-[10px] px-2 py-0.5 rounded-full
                 bg-white/20 backdrop-blur-sm text-white font-medium tracking-wide
                 cursor-pointer hover:bg-sakura-400/80 transition-colors"
          @click="goType"
        >{{ shop.tag || shop.category }}</span>
      </div>

      <!-- Rating top-right -->
      <div
        class="absolute top-2.5 right-2.5 flex items-center gap-0.5
               bg-white/90 backdrop-blur-sm rounded-full px-2 py-0.5
               text-[11px] font-medium text-sumi shadow-sm"
      >
        <svg width="9" height="9" viewBox="0 0 24 24" fill="#E57696">
          <path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z" />
        </svg>
        {{ shop.rating.toFixed(1) }}
      </div>

      <!-- Bottom info -->
      <div class="absolute bottom-0 left-0 right-0 p-3">
        <p class="text-white font-semibold text-sm leading-tight line-clamp-1 drop-shadow-sm">
          {{ shop.name }}
        </p>
        <div class="mt-1.5 flex items-center justify-between">
          <span
            class="text-[10px] text-white/65 cursor-pointer hover:text-sakura-300 transition-colors"
            @click="goPref"
          >{{ shop.prefecture }} · {{ shop.city }}</span>
        </div>
      </div>
    </router-link>
  </article>
</template>
