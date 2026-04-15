import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'
import HomeView from '../views/HomeView.vue'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'home',
    component: HomeView,
    meta: { title: '首頁' },
  },
  {
    path: '/shops',
    name: 'shops',
    component: () => import('../views/ShopsView.vue'),
    meta: { title: '店舖列表' },
  },
  {
    path: '/shops/new',
    name: 'shop-new',
    component: () => import('../views/ShopNewView.vue'),
    meta: { title: '新增店舖' },
  },
  {
    path: '/shops/:id',
    name: 'shop-detail',
    component: () => import('../views/ShopDetailView.vue'),
    meta: { title: '店舖詳情' },
  },
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes,
  scrollBehavior(_, __, savedPosition) {
    if (savedPosition) return savedPosition
    return { top: 0 }
  },
})

router.beforeEach((to) => {
  const title = to.meta?.title as string | undefined
  document.title = title ? `${title} · 桜探記` : '桜探記'
})

export default router
