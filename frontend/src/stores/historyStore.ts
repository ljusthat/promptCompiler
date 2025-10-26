/**
 * 历史记录状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { CompiledPrompt } from '../types'
import { historyService } from '../services/historyService'

export const useHistoryStore = defineStore('history', () => {
  // 状态
  const loading = ref(false)
  const error = ref<string | null>(null)
  const records = ref<CompiledPrompt[]>([])
  const total = ref(0)
  const currentPage = ref(1)
  const pageSize = ref(20)

  // 计算属性
  const hasRecords = computed(() => records.value.length > 0)
  const totalPages = computed(() => Math.ceil(total.value / pageSize.value))

  // 方法
  async function fetchHistory(page: number = 1): Promise<void> {
    loading.value = true
    error.value = null
    currentPage.value = page

    const skip = (page - 1) * pageSize.value

    try {
      const response = await historyService.list({
        limit: pageSize.value,
        skip,
      })

      records.value = response.records
      total.value = response.total
    } catch (err: any) {
      error.value = err.message || '获取历史记录失败'
      console.error('获取历史记录错误:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchRecord(versionId: string): Promise<CompiledPrompt | null> {
    loading.value = true
    error.value = null

    try {
      const record = await historyService.get(versionId)
      return record
    } catch (err: any) {
      error.value = err.message || '获取历史记录失败'
      console.error('获取历史记录错误:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function searchHistory(query: string): Promise<CompiledPrompt[]> {
    loading.value = true
    error.value = null

    try {
      const response = await historyService.search(query, 50)
      return response.results
    } catch (err: any) {
      error.value = err.message || '搜索历史记录失败'
      console.error('搜索历史记录错误:', err)
      return []
    } finally {
      loading.value = false
    }
  }

  function nextPage() {
    if (currentPage.value < totalPages.value) {
      fetchHistory(currentPage.value + 1)
    }
  }

  function prevPage() {
    if (currentPage.value > 1) {
      fetchHistory(currentPage.value - 1)
    }
  }

  return {
    // 状态
    loading,
    error,
    records,
    total,
    currentPage,
    pageSize,
    // 计算属性
    hasRecords,
    totalPages,
    // 方法
    fetchHistory,
    fetchRecord,
    searchHistory,
    nextPage,
    prevPage,
  }
})

