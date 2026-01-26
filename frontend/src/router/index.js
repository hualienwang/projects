import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '@/views/Dashboard.vue'
import TestChart from '@/views/TestChart.vue'
import DashboardSimple from '@/views/DashboardSimple.vue'
import TestDashboardAPI from '@/views/TestDashboardAPI.vue'
import DiagnoseAPI from '@/views/DiagnoseAPI.vue'
import TestNavigation from '@/views/TestNavigation.vue'
import WorkflowTest from '@/views/WorkflowTest.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard,
    meta: {
      title: '數據儀表板 - 瓊林圖書進銷存系統'
    }
  },
  {
    path: '/dashboard',
    redirect: '/'
  },
  {
    path: '/test-chart',
    name: 'TestChart',
    component: TestChart,
    meta: {
      title: 'Chart.js 測試頁面'
    }
  },
  {
    path: '/dashboard-simple',
    name: 'DashboardSimple',
    component: DashboardSimple,
    meta: {
      title: '簡化版 Dashboard - 診斷模式'
    }
  },
  {
    path: '/test-dashboard-api',
    name: 'TestDashboardAPI',
    component: TestDashboardAPI,
    meta: {
      title: 'Dashboard API 測試頁面'
    }
  },
  {
    path: '/diagnose-api',
    name: 'DiagnoseAPI',
    component: DiagnoseAPI,
    meta: {
      title: 'API 診斷工具'
    }
  },
  {
    path: '/test-navigation',
    name: 'TestNavigation',
    component: TestNavigation,
    meta: {
      title: 'Navigation 測試頁面'
    }
  },
  {
    path: '/workflow-test',
    name: 'WorkflowTest',
    component: WorkflowTest,
    meta: {
      title: '工作流 API 測試'
    }
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/'
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由标题设置
router.beforeEach((to, from, next) => {
  if (to.meta.title) {
    document.title = to.meta.title
  }
  next()
})

export default router
