<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import ShopMap from '../components/ShopMap.vue'
import { CATEGORIES, CATEGORY_ICON, CATEGORY_TAGS } from '../types/shop'
import type { ShopCategory } from '../types/shop'
import { createShop, uploadCover, uploadPhotos } from '../api/shops'

const router = useRouter()

const form = ref({
  name: '',
  prefecture: '',
  city: '',
  address: '',
  category: '' as ShopCategory | '',
  tag: '',
  featured: false,
  visitDate: '',
  rating: 0,
  phone: '',
  hours: '',
  oneLiner: '',
  description: '',
  lat: 35.6762,
  lng: 139.6503,
})

const hoverRating = ref(0)
const lastClickedStar = ref(0)
const coverFile = ref<File | null>(null)
const coverPreview = ref<string>('')
const photoFiles = ref<File[]>([])
const photoPreviews = ref<string[]>([])
const submitting = ref(false)
const errorMsg = ref('')

// ── Location states ───────────────────────────────────────────────
const locating = ref(false)      // GPS / IP detection in progress
const geocoding = ref(false)     // address → coordinates in progress
const locateMsg = ref('')        // feedback message for the user

const NOM_HEADERS = {
  'User-Agent': '桜探記/1.0 (personal travel journal)',
  'Accept-Language': 'ja,zh-TW;q=0.8',
}

/** Reverse-geocode lat/lng → fill prefecture & city */
async function reverseGeocode(lat: number, lng: number) {
  const res = await fetch(
    `https://nominatim.openstreetmap.org/reverse?format=json&lat=${lat}&lon=${lng}`,
    { headers: NOM_HEADERS },
  )
  if (!res.ok) return
  const data = await res.json()
  const addr = data.address ?? {}
  const pref = addr.state ?? addr.province ?? ''
  const city = addr.city_district ?? addr.suburb ?? addr.city ?? addr.town ?? addr.county ?? ''
  if (pref && prefectures.includes(pref)) form.value.prefecture = pref
  if (city) form.value.city = city
}

/** GPS → reverse geocode → fill fields */
async function detectByGPS(): Promise<void> {
  return new Promise((resolve, reject) => {
    if (!navigator.geolocation) { reject(new Error('not supported')); return }
    navigator.geolocation.getCurrentPosition(
      async (pos) => {
        form.value.lat = pos.coords.latitude
        form.value.lng = pos.coords.longitude
        await reverseGeocode(pos.coords.latitude, pos.coords.longitude)
        resolve()
      },
      reject,
      { timeout: 8000, maximumAge: 60000 },
    )
  })
}

/** IP geolocation fallback → fill lat/lng + reverse geocode */
async function detectByIP() {
  const res = await fetch('https://ipapi.co/json/')
  if (!res.ok) throw new Error('IP geo failed')
  const data = await res.json()
  form.value.lat = data.latitude
  form.value.lng = data.longitude
  await reverseGeocode(data.latitude, data.longitude)
}

/** Main detect entry: GPS first, fall back to IP */
async function detectLocation() {
  locating.value = true
  locateMsg.value = '定位中…'
  try {
    await detectByGPS()
    locateMsg.value = 'GPS 定位成功'
  } catch {
    try {
      locateMsg.value = 'GPS 不可用，嘗試 IP 定位…'
      await detectByIP()
      locateMsg.value = 'IP 定位成功（精度：城市級）'
    } catch {
      locateMsg.value = '自動定位失敗，請手動填寫'
    }
  } finally {
    locating.value = false
  }
}

/** Forward geocode: prefecture + city + address → lat/lng */
async function geocodeAddress() {
  const q = [form.value.prefecture, form.value.city, form.value.address].filter(Boolean).join(' ')
  if (!q) return
  geocoding.value = true
  locateMsg.value = '搜尋地址中…'
  try {
    const res = await fetch(
      `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&countrycodes=jp&limit=1`,
      { headers: NOM_HEADERS },
    )
    const data = await res.json()
    if (data.length > 0) {
      form.value.lat = parseFloat(data[0].lat)
      form.value.lng = parseFloat(data[0].lon)
      locateMsg.value = '地址定位成功'
    } else {
      locateMsg.value = '找不到該地址，請確認後重試'
    }
  } catch {
    locateMsg.value = '搜尋失敗，請稍後再試'
  } finally {
    geocoding.value = false
  }
}

/** Called when user clicks the map to pick a position */
function onMapPick(lat: number, lng: number) {
  form.value.lat = lat
  form.value.lng = lng
  locateMsg.value = `已選定位置 (${lat.toFixed(5)}, ${lng.toFixed(5)})`
}

// Auto-detect on mount
onMounted(() => { detectLocation() })

const prefectures = [
  '東京都', '大阪府', '京都府', '神奈川県', '福岡県',
  '北海道', '愛知県', '兵庫県', '奈良県', '沖縄県',
  '埼玉県', '千葉県', '茨城県', '栃木県', '群馬県',
  '新潟県', '長野県', '静岡県', '広島県', '宮城県',
]

const suggestedTags = computed(() =>
  form.value.category ? CATEGORY_TAGS[form.value.category] : [],
)

function selectCategory(cat: ShopCategory) {
  if (form.value.category === cat) return
  form.value.category = cat
  form.value.tag = ''
}

function selectTag(tag: string) {
  form.value.tag = form.value.tag === tag ? '' : tag
}

function onStarClick(i: number) {
  if (lastClickedStar.value === i) {
    const next = Math.round((form.value.rating + 0.1) * 10) / 10
    form.value.rating = next >= i + 1 ? i : Math.min(next, 5.0)
  } else {
    form.value.rating = i
    lastClickedStar.value = i
  }
}

function displayRating(): number {
  if (hoverRating.value > 0 && hoverRating.value !== lastClickedStar.value) {
    return hoverRating.value
  }
  return form.value.rating
}

function starClipWidth(i: number, rating: number): number {
  if (i <= Math.floor(rating)) return 24
  if (i === Math.ceil(rating) && rating % 1 >= 0.5) return 12
  return 0
}

function handleCoverChange(e: Event) {
  const input = e.target as HTMLInputElement
  const file = input.files?.[0]
  if (!file) return
  coverFile.value = file
  const reader = new FileReader()
  reader.onload = (ev) => (coverPreview.value = ev.target?.result as string)
  reader.readAsDataURL(file)
}

function handlePhotoChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files) return
  Array.from(input.files).forEach((file) => {
    photoFiles.value.push(file)
    const reader = new FileReader()
    reader.onload = (ev) => photoPreviews.value.push(ev.target?.result as string)
    reader.readAsDataURL(file)
  })
}

function removePhoto(i: number) {
  photoFiles.value.splice(i, 1)
  photoPreviews.value.splice(i, 1)
}

async function handleSubmit() {
  errorMsg.value = ''
  if (!form.value.name || !form.value.prefecture || !form.value.category || !form.value.visitDate) {
    errorMsg.value = '請填寫店名、都道府縣、類別及探訪日期'
    return
  }
  submitting.value = true
  try {
    let coverImageUrl = ''
    if (coverFile.value) {
      coverImageUrl = await uploadCover(coverFile.value)
    } else if (photoFiles.value.length) {
      coverImageUrl = await uploadCover(photoFiles.value[0])
    } else {
      coverImageUrl = `https://picsum.photos/seed/${Date.now()}/800/600`
    }

    const shop = await createShop({
      name: form.value.name,
      prefecture: form.value.prefecture,
      city: form.value.city,
      address: form.value.address || undefined,
      category: form.value.category,
      tag: form.value.tag,
      phone: form.value.phone || undefined,
      hours: form.value.hours || undefined,
      lat: form.value.lat,
      lng: form.value.lng,
      coverImage: coverImageUrl,
      oneLiner: form.value.oneLiner,
      description: form.value.description,
      rating: form.value.rating,
      visitDate: form.value.visitDate,
      featured: form.value.featured,
    })

    if (photoFiles.value.length) {
      await uploadPhotos(shop.id, photoFiles.value)
    }

    router.replace(`/shops/${shop.id}`)
  } catch (err) {
    errorMsg.value = err instanceof Error ? err.message : '儲存失敗，請稍後再試'
  } finally {
    submitting.value = false
  }
}
</script>

<template>
  <div class="min-h-dvh bg-washi pb-20">

    <!-- Header -->
    <div class="sticky top-0 z-10 bg-washi/95 backdrop-blur-md border-b border-sakura-100">
      <div class="max-w-lg mx-auto px-5 h-14 flex items-center justify-between">
        <div class="flex items-center gap-3">
          <button
            class="w-6 h-6 rounded-full bg-white border border-stone-200 shadow-sm
                   flex items-center justify-center text-stone-400
                   hover:text-sakura-500 hover:border-sakura-200 transition-colors"
            @click="router.back()"
          >
            <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round">
              <polyline points="15 18 9 12 15 6"/>
            </svg>
          </button>
          <span class="font-mincho text-base font-semibold text-sumi">新增店舖</span>
        </div>
        <button
          class="px-4 py-1.5 rounded-full text-xs font-medium text-white
                 transition-all duration-200 active:scale-95 disabled:opacity-50"
          style="background: linear-gradient(135deg, #EEA0B8, #D9506F)"
          :disabled="submitting"
          @click="handleSubmit"
        >
          {{ submitting ? '儲存中…' : '儲存' }}
        </button>
      </div>
    </div>

    <!-- Error message -->
    <div v-if="errorMsg" class="max-w-lg mx-auto px-5 pt-3">
      <p class="text-xs text-red-500 bg-red-50 rounded-xl px-4 py-2">{{ errorMsg }}</p>
    </div>

    <div class="max-w-lg mx-auto px-5 pt-6 space-y-6">

      <!-- 封面相片 -->
      <section>
        <p class="text-[11px] text-stone-400 uppercase tracking-widest mb-3">封面相片</p>
        <label class="block relative">
          <div
            class="aspect-[3/2] rounded-2xl overflow-hidden border-2 border-dashed border-sakura-200
                   flex items-center justify-center bg-stone-50 cursor-pointer
                   hover:border-sakura-400 hover:bg-sakura-50 transition-all"
            :class="coverPreview ? 'border-transparent' : ''"
          >
            <img v-if="coverPreview" :src="coverPreview" class="w-full h-full object-cover" />
            <div v-else class="flex flex-col items-center gap-2 text-stone-400">
              <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#E57696" stroke-width="1.5" stroke-linecap="round">
                <rect x="3" y="3" width="18" height="18" rx="3"/>
                <circle cx="8.5" cy="8.5" r="1.5"/><polyline points="21 15 16 10 5 21"/>
              </svg>
              <span class="text-xs text-sakura-400">點擊上傳封面相片</span>
            </div>
          </div>
          <input type="file" accept="image/*" class="hidden" @change="handleCoverChange" />
        </label>
      </section>

      <!-- 基本資訊 -->
      <section>
        <p class="text-[11px] text-stone-400 uppercase tracking-widest mb-3">基本資訊</p>
        <div class="bg-white rounded-2xl border border-sakura-50 shadow-sm overflow-hidden divide-y divide-stone-50">
          <div class="px-4 py-3">
            <label class="text-[10px] text-stone-400 tracking-wide block mb-1">店名</label>
            <input
              v-model="form.name"
              type="text"
              placeholder="如：一蘭拉麵"
              class="w-full text-sm text-sumi bg-transparent outline-none placeholder-stone-300"
            />
          </div>
          <div class="px-4 py-3">
            <label class="text-[10px] text-stone-400 tracking-wide block mb-1">一句話簡介</label>
            <input
              v-model="form.oneLiner"
              type="text"
              placeholder="如：凌晨一點的拉麵，治癒了所有疲憊"
              class="w-full text-sm text-sumi bg-transparent outline-none placeholder-stone-300"
            />
          </div>
          <div class="px-4 py-3">
            <label class="text-[10px] text-stone-400 tracking-wide block mb-1">電話</label>
            <input
              v-model="form.phone"
              type="tel"
              placeholder="如：03-1234-5678"
              class="w-full text-sm text-sumi bg-transparent outline-none placeholder-stone-300"
            />
          </div>
          <div class="px-4 py-3">
            <label class="text-[10px] text-stone-400 tracking-wide block mb-1">營業時間</label>
            <input
              v-model="form.hours"
              type="text"
              placeholder="如：11:00–22:00（週二休）"
              class="w-full text-sm text-sumi bg-transparent outline-none placeholder-stone-300"
            />
          </div>
        </div>
      </section>

      <!-- 地點 & 分類 -->
      <section>
        <p class="text-[11px] text-stone-400 uppercase tracking-widest mb-3">地點 & 分類</p>

        <!-- Location card (顺丰 style) -->
        <div class="bg-white rounded-2xl border border-sakura-50 shadow-sm overflow-hidden divide-y divide-stone-50 mb-4">

          <!-- Auto-locate row -->
          <div class="flex items-center justify-between px-4 py-3">
            <div class="flex items-center gap-2">
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="#E57696" stroke-width="2" stroke-linecap="round">
                <circle cx="12" cy="10" r="3"/><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z"/>
              </svg>
              <span class="text-xs text-stone-500 leading-snug">
                <template v-if="locating">
                  <span class="text-sakura-400">定位中…</span>
                </template>
                <template v-else-if="locateMsg">{{ locateMsg }}</template>
                <template v-else>點擊右側自動定位</template>
              </span>
            </div>
            <button
              type="button"
              class="text-xs px-3 py-1 rounded-full border border-sakura-200 text-sakura-500
                     hover:bg-sakura-50 transition-colors disabled:opacity-40 shrink-0"
              :disabled="locating"
              @click="detectLocation"
            >
              <span v-if="locating" class="flex items-center gap-1">
                <svg class="animate-spin" width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4"/>
                </svg>
                定位中
              </span>
              <span v-else>📍 重新定位</span>
            </button>
          </div>

          <!-- Prefecture + city -->
          <div class="flex divide-x divide-stone-50">
            <div class="flex-1 px-4 py-3">
              <label class="text-[10px] text-stone-400 tracking-wide block mb-1">都道府縣</label>
              <select
                v-model="form.prefecture"
                class="w-full text-sm text-sumi bg-transparent outline-none"
              >
                <option value="" disabled>請選擇</option>
                <option v-for="p in prefectures" :key="p" :value="p">{{ p }}</option>
              </select>
            </div>
            <div class="flex-1 px-4 py-3">
              <label class="text-[10px] text-stone-400 tracking-wide block mb-1">城市 / 區</label>
              <input
                v-model="form.city"
                type="text"
                placeholder="如：渋谷区"
                class="w-full text-sm text-sumi bg-transparent outline-none placeholder-stone-300"
              />
            </div>
          </div>

          <!-- Detailed address + geocode button -->
          <div class="px-4 py-3 flex items-center gap-2">
            <div class="flex-1">
              <label class="text-[10px] text-stone-400 tracking-wide block mb-1">詳細地址</label>
              <input
                v-model="form.address"
                type="text"
                placeholder="如：道玄坂1-2-3 渋谷ヒカリエ10F（選填）"
                class="w-full text-sm text-sumi bg-transparent outline-none placeholder-stone-300"
                @keydown.enter.prevent="geocodeAddress"
              />
            </div>
            <button
              type="button"
              class="shrink-0 mt-4 w-8 h-8 rounded-full bg-sakura-50 border border-sakura-200
                     flex items-center justify-center text-sakura-400
                     hover:bg-sakura-100 transition-colors disabled:opacity-40"
              :disabled="geocoding"
              aria-label="搜尋地址"
              @click="geocodeAddress"
            >
              <svg v-if="geocoding" class="animate-spin" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4"/>
              </svg>
              <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                <circle cx="11" cy="11" r="7"/><line x1="16.5" y1="16.5" x2="22" y2="22"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Map: pickable pin -->
        <ShopMap
          :lat="form.lat"
          :lng="form.lng"
          name="新店舖位置"
          :pickable="true"
          @pick="onMapPick"
        />
        <p class="text-[10px] text-stone-400 mt-1.5 text-center">可點擊地圖精確調整位置</p>

        <!-- Category grid -->
        <p class="text-xs text-stone-400 mb-2 mt-5">店舖類別</p>
        <div class="grid grid-cols-4 gap-2 mb-4">
          <button
            v-for="cat in CATEGORIES"
            :key="cat"
            class="flex flex-col items-center justify-center gap-1 py-2.5 rounded-xl border text-center transition-all duration-150"
            :class="form.category === cat
              ? 'bg-sakura-400 border-sakura-400 text-white shadow-sm'
              : 'bg-white border-stone-100 text-stone-500 hover:border-sakura-200'"
            @click="selectCategory(cat)"
          >
            <span class="text-xl leading-none">{{ CATEGORY_ICON[cat] }}</span>
            <span class="text-[10px] font-medium leading-tight">{{ cat }}</span>
          </button>
        </div>

        <!-- Tag chips -->
        <Transition name="fade-slide">
          <div v-if="form.category">
            <p class="text-xs text-stone-400 mb-2">細分標籤<span class="text-stone-300 ml-1">（單選）</span></p>
            <div class="flex flex-wrap gap-2">
              <button
                v-for="tag in suggestedTags"
                :key="tag"
                class="text-xs px-3 py-1.5 rounded-full border transition-all duration-150"
                :class="form.tag === tag
                  ? 'bg-sumi text-white border-sumi font-medium'
                  : 'bg-white border-stone-200 text-stone-500 hover:border-stone-400'"
                @click="selectTag(tag)"
              >{{ tag }}</button>
            </div>
          </div>
        </Transition>
      </section>

      <!-- 精選 -->
      <section>
        <div class="flex items-center justify-between bg-white rounded-2xl border border-sakura-50 shadow-sm px-4 py-3">
          <div>
            <p class="text-sm text-sumi font-medium">列為精選</p>
            <p class="text-[10px] text-stone-400 mt-0.5">精選店舖會在首頁優先展示</p>
          </div>
          <button
            class="relative w-11 h-6 rounded-full transition-colors duration-200 focus:outline-none"
            :class="form.featured ? 'bg-sakura-400' : 'bg-stone-200'"
            @click="form.featured = !form.featured"
          >
            <span
              class="absolute top-0.5 left-0.5 w-5 h-5 bg-white rounded-full shadow-sm
                     transition-transform duration-200"
              :class="form.featured ? 'translate-x-5' : 'translate-x-0'"
            />
          </button>
        </div>
      </section>

      <!-- 探訪日期 -->
      <section>
        <p class="text-[11px] text-stone-400 uppercase tracking-widest mb-3">探訪日期</p>
        <div class="bg-white rounded-2xl border border-sakura-50 shadow-sm px-4 py-3">
          <input
            v-model="form.visitDate"
            type="date"
            class="w-full text-sm text-sumi bg-transparent outline-none"
          />
        </div>
      </section>

      <!-- 評分 -->
      <section>
        <p class="text-[11px] text-stone-400 uppercase tracking-widest mb-3">我的評分</p>
        <div class="flex items-center gap-3" @mouseleave="hoverRating = 0">

          <!-- Stars: clipPath for reliable half-star rendering -->
          <div class="flex items-center gap-0.5">
            <div
              v-for="i in 5"
              :key="i"
              class="w-9 h-9 cursor-pointer select-none"
              @mouseenter="hoverRating = i"
              @click="onStarClick(i)"
            >
              <svg width="36" height="36" viewBox="0 0 24 24">
                <defs>
                  <clipPath :id="`clip-s${i}`">
                    <rect x="0" y="0" :width="starClipWidth(i, displayRating())" height="24"/>
                  </clipPath>
                </defs>
                <!-- Base: empty star -->
                <path fill="#E5E7EB" d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/>
                <!-- Overlay: filled star, clipped to fill width -->
                <path
                  fill="#E57696"
                  :clip-path="`url(#clip-s${i})`"
                  d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"
                />
              </svg>
            </div>
          </div>

          <!-- Score: follows right after stars, soft colour -->
          <span class="font-mincho text-3xl font-semibold tabular-nums leading-none" style="color:#E57696">
            {{ form.rating.toFixed(1) }}
          </span>
        </div>
      </section>

      <!-- 評價 -->
      <section>
        <p class="text-[11px] text-stone-400 uppercase tracking-widest mb-3">我的評價</p>
        <textarea
          v-model="form.description"
          rows="5"
          placeholder="寫下這次探訪的感受、推薦的單品、特別的記憶……"
          class="w-full bg-white border border-sakura-50 rounded-2xl px-4 py-3
                 text-sm text-sumi placeholder-stone-300 outline-none
                 focus:border-sakura-200 focus:ring-2 focus:ring-sakura-50
                 resize-none transition-all shadow-sm"
        />
      </section>

      <!-- 相片上傳 -->
      <section>
        <p class="text-[11px] text-stone-400 uppercase tracking-widest mb-3">上傳相片</p>
        <div class="grid grid-cols-3 gap-2">
          <div
            v-for="(preview, i) in photoPreviews"
            :key="i"
            class="relative aspect-square overflow-hidden rounded-xl bg-stone-100"
          >
            <img :src="preview" class="w-full h-full object-cover" />
            <button
              class="absolute top-1 right-1 w-5 h-5 rounded-full bg-black/50
                     flex items-center justify-center text-white hover:bg-black/70 transition-colors"
              @click="removePhoto(i)"
            >
              <svg width="8" height="8" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round">
                <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
              </svg>
            </button>
          </div>
          <label
            class="aspect-square rounded-xl border-2 border-dashed border-sakura-200
                   flex flex-col items-center justify-center gap-1
                   cursor-pointer hover:border-sakura-400 hover:bg-sakura-50 transition-all"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#E57696" stroke-width="1.8" stroke-linecap="round">
              <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
            </svg>
            <span class="text-[10px] text-sakura-400">新增相片</span>
            <input type="file" accept="image/*" multiple class="hidden" @change="handlePhotoChange" />
          </label>
        </div>
      </section>

    </div>
  </div>
</template>

<style scoped>
.fade-slide-enter-active {
  transition: all 0.25s ease;
}
.fade-slide-leave-active {
  transition: all 0.15s ease;
}
.fade-slide-enter-from,
.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}
</style>
