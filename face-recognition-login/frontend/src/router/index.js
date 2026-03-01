import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// 🔴 1. เปลี่ยนตรงนี้: ดึงหน้า LoginView มาเป็นหน้าแรกสุดแทน QuickLoginView
import HomeView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView // ตอนนี้เปิดมาจะเป็นหน้า Login ขาวๆ ม่วงๆ แล้วครับ
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/login',
      name: 'login',
      // 🔴 2. เปลี่ยนตรงนี้: ให้ชี้ไปที่หน้า LoginView
      component: () => import('../views/LoginView.vue')
    },
    {
      path: '/quick-login',
      name: 'quick-login',
      component: () => import('../views/QuickLoginView.vue')
    },
    {
      path: '/dashboard',
      name: 'dashboard',
      component: () => import('../views/QuickLoginView.vue'), // ตรงนี้ชี้ไปหน้า Dashboard เมื่อทำเสร็จ (ตอนนี้เอาไว้สแกนชั่วคราว)
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router