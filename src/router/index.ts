import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('@/pages/HomePage.vue'),
  },
  {
    path: '/products/:id',
    name: 'product-detail',
    component: () => import('@/pages/ProductDetail.vue'),
  },
  {
    path: '/order/new/:productId',
    name: 'custom-order',
    component: () => import('@/pages/CustomOrder.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/orders',
    name: 'orders',
    component: () => import('@/pages/OrderTrack.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/orders/:id',
    name: 'order-detail',
    component: () => import('@/pages/OrderTrack.vue'),
    meta: { requiresAuth: true },
  },
  {
    path: '/artisan/workspace',
    name: 'artisan-workspace',
    component: () => import('@/pages/ArtisanWorkspace.vue'),
    meta: { requiresAuth: true, roles: ['artisan', 'admin'] },
  },
  {
    path: '/login',
    name: 'login',
    component: () => import('@/pages/Login.vue'),
  },
  {
    path: '/register',
    name: 'register',
    component: () => import('@/pages/Register.vue'),
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
})

router.beforeEach(async (to) => {
  const authStore = useAuthStore()
  if (authStore.isLoggedIn && !authStore.user) {
    await authStore.fetchUser()
  }
  if (to.meta.requiresAuth && !authStore.isLoggedIn) {
    return { name: 'login', query: { redirect: to.fullPath } }
  }
  if (to.meta.roles && authStore.userRole && !(to.meta.roles as string[]).includes(authStore.userRole)) {
    return { name: 'home' }
  }
})

export default router
