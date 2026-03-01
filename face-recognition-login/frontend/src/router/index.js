import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'

// ดึงหน้า LoginView มาเป็นหน้าแรกสุด
import HomeView from '../views/LoginView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'home',
      component: HomeView 
    },
    {
      path: '/register',
      name: 'register',
      component: () => import('../views/RegisterView.vue')
    },
    {
      path: '/login',
      name: 'login',
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
      // 🔴 แก้ไขตรงนี้: เปลี่ยนจาก QuickLoginView เป็น DashboardView เพื่อเข้าหน้าร้าน F1
      component: () => import('../views/DashboardView.vue'), 
      meta: { requiresAuth: true }
    }
  ]
})

// ระบบป้องกัน: ถ้ายังไม่ได้ล็อกอิน จะเข้าหน้า dashboard ไม่ได้ และโดนเตะกลับมาหน้า login
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router