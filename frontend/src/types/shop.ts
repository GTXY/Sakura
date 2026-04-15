export type ShopCategory =
  | '餐飲'
  | '購物'
  | '娛樂'
  | '美容養生'
  | '生活服務'
  | '文化藝術'
  | '自然景點'
  | '住宿'

export const CATEGORIES: ShopCategory[] = [
  '餐飲', '購物', '娛樂', '美容養生', '生活服務', '文化藝術', '自然景點', '住宿',
]

export const CATEGORY_ICON: Record<ShopCategory, string> = {
  '餐飲':   '🍜',
  '購物':   '🛍️',
  '娛樂':   '🎮',
  '美容養生': '💆',
  '生活服務': '🔧',
  '文化藝術': '🏛️',
  '自然景點': '🌿',
  '住宿':   '🏨',
}

export const CATEGORY_TAGS: Record<ShopCategory, string[]> = {
  '餐飲': ['拉麵', '壽司', '居酒屋', '咖啡', '甜點', '烤肉', '定食', '天婦羅', '和食', '燒鳥', '串揚', '烏冬', '海鮮', '火鍋', '便當'],
  '購物': ['百貨公司', '藥妝', '雜貨', '二手', '書店', '服飾', '電器', '伴手禮', '市場', '超市', '文具'],
  '娛樂': ['卡拉OK', '遊戲廳', '電影院', '保齡球', '密室逃脫', '漫畫喫茶', '主題樂園', '夜店', '撞球'],
  '美容養生': ['按摩', 'SPA', '溫泉', '足浴', '美容院', '指甲彩繪', '美髮', '岩盤浴', '芳療'],
  '生活服務': ['理髮', '洗衣', '銀行', '郵局', '診所', '健身房', '圖書館'],
  '文化藝術': ['博物館', '美術館', '神社', '寺廟', '城堡', '庭園', '展覽', '音樂廳', '劇場'],
  '自然景點': ['公園', '海灘', '山岳', '花園', '動物園', '水族館', '瀑布', '湖泊'],
  '住宿': ['旅館', '民宿', '飯店', '膠囊旅館', '溫泉旅館', '青年旅舍'],
}

export interface Shop {
  id: string
  name: string
  prefecture: string
  city: string
  address?: string
  category: ShopCategory
  tag: string
  visitDate: string
  rating: number
  oneLiner: string
  description: string
  coverImage: string
  photos: string[]
  featured: boolean
  lat: number
  lng: number
  phone?: string
  hours?: string
}
