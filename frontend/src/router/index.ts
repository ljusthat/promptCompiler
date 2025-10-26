import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import PromptCompiler from '../views/PromptCompiler.vue'
import TemplateManagement from '../views/TemplateManagement.vue'
import HistoryView from '../views/HistoryView.vue'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'PromptCompiler',
    component: PromptCompiler,
    meta: { title: 'Prompt 编译器' }
  },
  {
    path: '/templates',
    name: 'Templates',
    component: TemplateManagement,
    meta: { title: '模板管理' }
  },
  {
    path: '/history',
    name: 'History',
    component: HistoryView,
    meta: { title: '历史记录' }
  }
]

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes
})

// 路由守卫 - 设置页面标题
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title || 'Prompt Compiler'} - Prompt Compiler`
  next()
})

export default router

