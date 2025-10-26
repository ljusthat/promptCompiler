/**
 * 历史记录相关 API 服务
 */
import apiClient from './api'
import type { CompiledPrompt } from '../types'

export interface HistoryListResponse {
  success: boolean
  records: CompiledPrompt[]
  total: number
  page: number
  page_size: number
}

export const historyService = {
  /**
   * 获取历史记录列表
   */
  async list(params?: {
    limit?: number
    skip?: number
  }): Promise<HistoryListResponse> {
    return apiClient.get('/history/', { params })
  },

  /**
   * 获取单个历史记录
   */
  async get(versionId: string): Promise<CompiledPrompt> {
    return apiClient.get(`/history/${versionId}`)
  },

  /**
   * 搜索历史记录
   */
  async search(query: string, limit?: number): Promise<{
    success: boolean
    results: CompiledPrompt[]
    count: number
  }> {
    return apiClient.get('/history/search/', {
      params: { q: query, limit }
    })
  },

  /**
   * 获取统计信息
   */
  async getStatistics(): Promise<{
    success: boolean
    statistics: any
  }> {
    return apiClient.get('/history/stats/summary')
  },
}

export default historyService

