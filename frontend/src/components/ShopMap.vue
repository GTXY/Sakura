<script setup lang="ts">
import { onMounted, onUnmounted, ref, watch } from 'vue'
import maplibregl from 'maplibre-gl'
import 'maplibre-gl/dist/maplibre-gl.css'

const props = defineProps<{
  lat: number
  lng: number
  name: string
  pickable?: boolean   // if true: click on map to pick a new location
}>()

const emit = defineEmits<{
  (e: 'pick', lat: number, lng: number): void
}>()

const mapContainer = ref<HTMLDivElement>()
let map: maplibregl.Map | null = null
let marker: maplibregl.Marker | null = null

function createMarkerEl() {
  const el = document.createElement('div')
  el.innerHTML = `
    <div style="
      width:36px;height:36px;
      background:linear-gradient(135deg,#EEA0B8,#D9506F);
      border-radius:50% 50% 50% 0;
      transform:rotate(-45deg);
      box-shadow:0 4px 12px rgba(217,80,111,.45);
      border:2px solid white;
    "></div>`
  return el
}

onMounted(() => {
  if (!mapContainer.value) return

  map = new maplibregl.Map({
    container: mapContainer.value,
    style: 'https://basemaps.cartocdn.com/gl/voyager-gl-style/style.json',
    center: [props.lng, props.lat],
    zoom: 15,
    interactive: true,
    attributionControl: false,
  })

  map.addControl(new maplibregl.AttributionControl({ compact: true }), 'bottom-right')

  marker = new maplibregl.Marker({ element: createMarkerEl(), anchor: 'bottom' })
    .setLngLat([props.lng, props.lat])
    .addTo(map)

  if (props.pickable) {
    map.getCanvas().style.cursor = 'crosshair'
    map.on('click', (e) => {
      const { lat, lng } = e.lngLat
      marker?.setLngLat([lng, lat])
      emit('pick', lat, lng)
    })
  }
})

// Fly to new coordinates when props change (e.g. after geocoding)
watch(
  () => [props.lat, props.lng] as const,
  ([lat, lng]) => {
    if (!map) return
    map.flyTo({ center: [lng, lat], zoom: 15, duration: 800 })
    marker?.setLngLat([lng, lat])
  },
)

onUnmounted(() => {
  map?.remove()
})
</script>

<template>
  <div class="relative">
    <div ref="mapContainer" class="w-full h-52 rounded-2xl overflow-hidden" />
    <div
      v-if="pickable"
      class="absolute bottom-2 left-1/2 -translate-x-1/2
             bg-black/50 backdrop-blur-sm text-white text-[10px]
             px-3 py-1 rounded-full pointer-events-none"
    >
      點擊地圖設定精確位置
    </div>
  </div>
</template>
