import { ref, watch, onUnmounted } from 'vue'
import { fetchShops, PAGE_SIZE } from '../api/shops'
import type { ShopListParams } from '../api/shops'
import type { Shop } from '../types/shop'

/**
 * Infinite-scroll composable for shop lists.
 *
 * Usage:
 *   const { shops, loading, loadingMore, hasMore, reset, sentinelRef } = useInfiniteShops(params)
 *
 * Mount <div ref="sentinelRef" /> at the bottom of your list.
 * When it enters the viewport, the next page loads automatically.
 */
export function useInfiniteShops(getParams: () => Omit<ShopListParams, 'limit' | 'offset'>) {
  const shops = ref<Shop[]>([])
  const loading = ref(true)      // first page loading
  const loadingMore = ref(false) // subsequent pages
  const hasMore = ref(true)
  const offset = ref(0)
  const sentinelRef = ref<HTMLElement | null>(null)

  let observer: IntersectionObserver | null = null

  async function loadPage(isFirst: boolean) {
    if (isFirst) {
      loading.value = true
    } else {
      loadingMore.value = true
    }
    try {
      const result = await fetchShops({
        ...getParams(),
        limit: PAGE_SIZE,
        offset: offset.value,
      })
      if (isFirst) {
        shops.value = result
      } else {
        shops.value = [...shops.value, ...result]
      }
      hasMore.value = result.length === PAGE_SIZE
      offset.value += result.length
    } catch (e) {
      console.error('Failed to load shops:', e)
    } finally {
      loading.value = false
      loadingMore.value = false
    }
  }

  function reset() {
    shops.value = []
    offset.value = 0
    hasMore.value = true
    loadPage(true)
  }

  function setupObserver() {
    if (observer) observer.disconnect()
    observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting && hasMore.value && !loading.value && !loadingMore.value) {
          loadPage(false)
        }
      },
      { rootMargin: '120px' },
    )
    if (sentinelRef.value) observer.observe(sentinelRef.value)
  }

  // Re-attach observer whenever sentinelRef changes (e.g. after DOM update)
  watch(sentinelRef, (el) => {
    if (observer) observer.disconnect()
    if (el && hasMore.value) observer?.observe(el)
  })

  onUnmounted(() => {
    observer?.disconnect()
  })

  // Initial load
  reset()

  return { shops, loading, loadingMore, hasMore, reset, sentinelRef, setupObserver }
}
