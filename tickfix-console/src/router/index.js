import { createRouter, createWebHistory } from 'vue-router'
import { useUserStore } from '@/store/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { title: '登录', requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/views/Layout.vue'),
    redirect: '/dashboard',
    meta: { requiresAuth: true },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue'),
        meta: { title: '工作台', icon: 'Odometer' }
      },
      {
        path: 'orders',
        name: 'Orders',
        component: () => import('@/views/orders/OrderList.vue'),
        meta: { title: '接件单管理', icon: 'Document' }
      },
      {
        path: 'orders/create',
        name: 'OrderCreate',
        component: () => import('@/views/orders/OrderCreate.vue'),
        meta: { title: '新建接件单', hidden: true }
      },
      {
        path: 'orders/:id',
        name: 'OrderDetail',
        component: () => import('@/views/orders/OrderDetail.vue'),
        meta: { title: '接件单详情', hidden: true }
      },
      {
        path: 'inventory',
        name: 'Inventory',
        component: () => import('@/views/inventory/PartList.vue'),
        meta: { title: '零件仓库', icon: 'Box' }
      },
      {
        path: 'pickup',
        name: 'Pickup',
        component: () => import('@/views/Pickup.vue'),
        meta: { title: '取件查询', icon: 'Search' }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

router.beforeEach((to, from, next) => {
  const userStore = useUserStore()
  
  document.title = to.meta.title ? `${to.meta.title} - TickFix` : 'TickFix 钟表维修管理系统'
  
  if (to.meta.requiresAuth && !userStore.isLoggedIn) {
    next({ path: '/login', query: { redirect: to.fullPath } })
  } else if (to.path === '/login' && userStore.isLoggedIn) {
    next({ path: '/' })
  } else {
    next()
  }
})

export default router
