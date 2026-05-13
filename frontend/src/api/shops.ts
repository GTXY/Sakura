import type { Shop, ShopCategory } from '../types/shop'

const API_BASE = `${import.meta.env.BASE_URL}api`

export interface Stats {
  total: number
  prefectures: number
}

export const PAGE_SIZE = 10

export interface ShopListParams {
  sort?: 'recent' | 'featured' | 'mine'
  category?: string
  pref?: string
  search?: string
  limit?: number
  offset?: number
}

export interface CreateShopPayload {
  name: string
  prefecture: string
  city: string
  address?: string
  category: ShopCategory | string
  tag: string
  phone?: string
  hours?: string
  lat: number
  lng: number
  coverImage: string
  oneLiner: string
  description: string
  rating: number
  visitDate: string
  featured: boolean
}

function getAuthHeaders(): Record<string, string> {
  const token = localStorage.getItem('sakura_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      'Content-Type': 'application/json',
      ...getAuthHeaders(),
      ...init?.headers,
    },
  })
  if (!res.ok) {
    const text = await res.text().catch(() => '')
    throw new Error(`API ${res.status}: ${text}`)
  }
  return res.json() as Promise<T>
}

// ── Stats ────────────────────────────────────────────────────────

export function fetchStats(): Promise<Stats> {
  return request<Stats>(`${API_BASE}/shops/stats`)
}

// ── Shop list ────────────────────────────────────────────────────

export function fetchShops(params: ShopListParams = {}): Promise<Shop[]> {
  const q = new URLSearchParams()
  if (params.sort) q.set('sort', params.sort)
  if (params.category) q.set('category', params.category)
  if (params.pref) q.set('prefecture', params.pref)
  if (params.search) q.set('q', params.search)
  q.set('limit', String(params.limit ?? PAGE_SIZE))
  q.set('offset', String(params.offset ?? 0))
  return request<Shop[]>(`${API_BASE}/shops?${q.toString()}`)
}

// ── Single shop ──────────────────────────────────────────────────

export function fetchShop(id: string): Promise<Shop> {
  return request<Shop>(`${API_BASE}/shops/${id}`)
}

// ── Create shop ──────────────────────────────────────────────────

export function createShop(payload: CreateShopPayload): Promise<Shop> {
  return request<Shop>(`${API_BASE}/shops`, {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

// ── Upload cover image ───────────────────────────────────────────

export async function uploadCover(file: File): Promise<string> {
  const fd = new FormData()
  fd.append('file', file)
  const res = await fetch(`${API_BASE}/uploads`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: fd,
  })
  if (!res.ok) throw new Error(`Upload failed: ${res.status}`)
  const data = (await res.json()) as { url: string }
  return data.url
}

// ── Upload gallery photos ────────────────────────────────────────

export async function uploadPhotos(shopId: string, files: File[]): Promise<void> {
  const fd = new FormData()
  files.forEach((f) => fd.append('files', f))
  const res = await fetch(`${API_BASE}/shops/${shopId}/photos`, {
    method: 'POST',
    headers: getAuthHeaders(),
    body: fd,
  })
  if (!res.ok) throw new Error(`Photo upload failed: ${res.status}`)
}
