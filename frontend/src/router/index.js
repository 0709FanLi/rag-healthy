import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import Login from '@/views/Login.vue'
import Chat from '@/views/Chat.vue'
import Report from '@/views/Report.vue'
import History from '@/views/History.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'Login',
      component: Login
    },
    {
      path: '/chat',
      name: 'Chat',
      component: Chat,
      meta: { requiresAuth: true }
    },
    {
      path: '/report', // 可以带参数 /report/:id
      name: 'Report',
      component: Report,
      meta: { requiresAuth: true }
    },
    {
      path: '/history', // 历史记录页面
      name: 'History',
      component: History,
      meta: { requiresAuth: true }
    }
  ]
})

router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()
  if (to.meta.requiresAuth && !authStore.token) {
    next({ name: 'Login' })
  } else {
    next()
  }
})

export default router

