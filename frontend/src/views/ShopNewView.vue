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
  postalCode: '',
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
const lookingUpPostal = ref(false)
const locateMsg = ref('')

const NOM_HEADERS = {
  'Accept-Language': 'ja,zh-TW;q=0.8',
}

// ── Address autocomplete ──────────────────────────────────────────
interface AddressSuggestion {
  display_name: string
  lat: string
  lon: string
  address: Record<string, string>
}

const addressSuggestions = ref<AddressSuggestion[]>([])
const showSuggestions = ref(false)
const addressLoading = ref(false)
let addressDebounce: ReturnType<typeof setTimeout> | null = null

function onAddressInput(e: Event) {
  const val = (e.target as HTMLInputElement).value
  form.value.address = val
  if (addressDebounce) clearTimeout(addressDebounce)
  const q = val.trim()
  if (q.length < 2) {
    addressSuggestions.value = []
    showSuggestions.value = false
    return
  }
  addressDebounce = setTimeout(async () => {
    addressLoading.value = true
    try {
      const res = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(q)}&countrycodes=jp&limit=5&addressdetails=1`,
        { headers: NOM_HEADERS },
      )
      if (!res.ok) return
      const data: AddressSuggestion[] = await res.json()
      addressSuggestions.value = data
      showSuggestions.value = data.length > 0
    } catch (err) { console.error('[Nominatim]', err) } finally {
      addressLoading.value = false
    }
  }, 400)
}

function selectSuggestion(s: AddressSuggestion) {
  form.value.address = s.display_name.split(',')[0].trim()
  form.value.lat = parseFloat(s.lat)
  form.value.lng = parseFloat(s.lon)
  const addr = s.address
  const pref = addr.state ?? addr.province ?? ''
  const city = addr.city_district ?? addr.suburb ?? addr.city ?? addr.town ?? addr.county ?? ''
  if (pref && prefectures.includes(pref)) form.value.prefecture = pref
  if (city) form.value.city = city
  showSuggestions.value = false
  addressSuggestions.value = []
}

// ── Silent GPS/IP detection (only moves map, no UI) ──────────────
async function detectSilent() {
  try {
    await new Promise<void>((resolve, reject) => {
      if (!navigator.geolocation) { reject(new Error('not supported')); return }
      navigator.geolocation.getCurrentPosition(
        (pos) => {
          form.value.lat = pos.coords.latitude
          form.value.lng = pos.coords.longitude
          resolve()
        },
        reject,
        { timeout: 15000, maximumAge: 60000 },
      )
    })
  } catch {
    try {
      const controller = new AbortController()
      const timer = setTimeout(() => controller.abort(), 5000)
      try {
        const res = await fetch('https://ipapi.co/json/', { signal: controller.signal })
        if (res.ok) {
          const data = await res.json()
          form.value.lat = data.latitude
          form.value.lng = data.longitude
        }
      } finally {
        clearTimeout(timer)
      }
    } catch { /* stay at default Tokyo */ }
  }
}

onMounted(() => { detectSilent() })

/** Japan postal code lookup → fill prefecture, city, address */
async function lookupPostalCode() {
  const code = form.value.postalCode.replace(/[^0-9]/g, '')
  if (code.length !== 7) {
    locateMsg.value = '郵便番号は7桁で入力してください'
    return
  }
  lookingUpPostal.value = true
  locateMsg.value = '郵便番号検索中…'
  try {
    const res = await fetch(`https://zipcloud.ibsnet.co.jp/api/search?zipcode=${code}`)
    if (!res.ok) throw new Error('lookup failed')
    const data = await res.json()
    if (!data.results || data.results.length === 0) {
      locateMsg.value = '該当する住所が見つかりません'
      return
    }
    const r = data.results[0]
    const pref = r.address1 ?? ''
    const city = r.address2 ?? ''
    const town = r.address3 ?? ''
    if (pref && prefectures.includes(pref)) form.value.prefecture = pref
    if (city) form.value.city = city
    if (town) form.value.address = town
    locateMsg.value = '住所を自動入力しました'
  } catch {
    locateMsg.value = '郵便番号の検索に失敗しました'
  } finally {
    lookingUpPostal.value = false
  }
}


const prefectures = [
  '北海道',
  '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県',
  '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県', '東京都', '神奈川県',
  '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県',
  '岐阜県', '静岡県', '愛知県',
  '三重県', '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県',
  '鳥取県', '島根県', '岡山県', '広島県', '山口県',
  '徳島県', '香川県', '愛媛県', '高知県',
  '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県',
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
          <span class="font-mincho text-base font-semibold text-sumi">新增探訪</span>
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
        <p class="text-[11px] text-stone-400 uppercase tracking-widest mb-3">地點</p>

        <!-- Location card wrapper: relative so suggestions can position against it -->
        <div class="relative mb-4">
          <div class="bg-white rounded-2xl border border-sakura-50 shadow-sm overflow-hidden divide-y divide-stone-50">

            <!-- Postal code lookup -->
            <div class="px-4 py-3 flex items-start gap-2">
              <div class="flex-1">
                <label class="text-[10px] text-stone-400 tracking-wide block mb-1">郵便番号</label>
                <input
                  v-model="form.postalCode"
                  type="text"
                  inputmode="numeric"
                  placeholder="例：1500043"
                  maxlength="8"
                  class="w-full text-sm text-sumi bg-transparent outline-none placeholder-stone-300"
                  @keydown.enter.prevent="lookupPostalCode"
                />
                <p v-if="locateMsg" class="text-[10px] mt-1" :class="locateMsg.includes('失敗') || locateMsg.includes('見つかり') ? 'text-red-400' : 'text-sakura-400'">
                  {{ locateMsg }}
                </p>
              </div>
              <button
                type="button"
                class="shrink-0 mt-5 w-8 h-8 rounded-full bg-sakura-50 border border-sakura-200
                       flex items-center justify-center text-sakura-400
                       hover:bg-sakura-100 transition-colors disabled:opacity-40"
                :disabled="lookingUpPostal"
                aria-label="郵便番号検索"
                @click="lookupPostalCode"
              >
                <svg v-if="lookingUpPostal" class="animate-spin" width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4"/>
                </svg>
                <svg v-else width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round">
                  <circle cx="11" cy="11" r="7"/><line x1="16.5" y1="16.5" x2="22" y2="22"/>
                </svg>
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

            <!-- Detailed address: explicit :value + @input, no v-model -->
            <div class="px-4 py-3">
              <label class="text-[10px] text-stone-400 tracking-wide block mb-1">詳細地址</label>
              <div class="flex items-center gap-1">
                <input
                  :value="form.address"
                  type="text"
                  autocomplete="off"
                  placeholder="如：道玄坂1-2-3（輸入可搜尋地址）"
                  class="w-full text-sm text-sumi bg-transparent outline-none placeholder-stone-300"
                  @input="onAddressInput"
                />
                <svg v-if="addressLoading" class="animate-spin shrink-0" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="#E57696" stroke-width="2.5">
                  <path d="M12 2v4M12 18v4M4.93 4.93l2.83 2.83M16.24 16.24l2.83 2.83M2 12h4M18 12h4"/>
                </svg>
              </div>
            </div>
          </div>

          <!-- Suggestions dropdown: outside overflow-hidden, positioned absolutely -->
          <div
            v-if="showSuggestions && addressSuggestions.length > 0"
            class="absolute left-0 right-0 top-full mt-1 z-[100]
                   bg-white rounded-2xl border border-sakura-100 shadow-xl overflow-hidden"
          >
            <button
              v-for="s in addressSuggestions"
              :key="s.display_name"
              type="button"
              class="w-full px-4 py-3 text-left active:bg-sakura-50 transition-colors border-b border-stone-50 last:border-0"
              @click="selectSuggestion(s)"
            >
              <p class="text-xs text-sumi font-medium truncate">{{ s.display_name.split(',')[0].trim() }}</p>
              <p class="text-[10px] text-stone-400 truncate mt-0.5">{{ s.display_name.split(',').slice(1, 4).join(',') }}</p>
            </button>
          </div>
        </div>

        <!-- Overlay: closes suggestions when tapping outside (teleported to avoid stacking issues) -->
        <Teleport to="body">
          <div
            v-if="showSuggestions"
            class="fixed inset-0 z-[90]"
            @click="showSuggestions = false"
            @touchstart.passive="showSuggestions = false"
          />
        </Teleport>

        <!-- Map: view only -->
        <ShopMap
          :lat="form.lat"
          :lng="form.lng"
          name="新增探訪位置"
        />

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
