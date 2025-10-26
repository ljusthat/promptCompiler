/**
 * 模板相关 API 服务
 */
import apiClient from './api'
import type { PromptTemplate } from '../types'

export interface TemplateListResponse {
  success: boolean
  templates: PromptTemplate[]
  total: number
}

export interface TemplateCreateRequest {
  name: string
  description?: string
  role: string
  objective: string
  constraints?: string[]
  output_format: string
  context_vars?: Record<string, string>
  task_types?: string[]
  domains?: string[]
  tags?: string[]
}

export const templateService = {
  /**
   * 创建模板
   */
  async create(request: TemplateCreateRequest): Promise<PromptTemplate> {
    return apiClient.post('/templates/', request)
  },

  /**
   * 获取模板列表
   */
  async list(params?: {
    task_type?: string
    domain?: string
    limit?: number
    skip?: number
  }): Promise<TemplateListResponse> {
    return apiClient.get('/templates/', { params })
  },

  /**
   * 获取单个模板
   */
  async get(templateId: string): Promise<PromptTemplate> {
    return apiClient.get(`/templates/${templateId}`)
  },

  /**
   * 更新模板
   */
  async update(templateId: string, updates: Partial<TemplateCreateRequest>): Promise<PromptTemplate> {
    return apiClient.put(`/templates/${templateId}`, updates)
  },

  /**
   * 删除模板
   */
  async delete(templateId: string): Promise<{ success: boolean; message: string }> {
    return apiClient.delete(`/templates/${templateId}`)
  },
}

export default templateService

