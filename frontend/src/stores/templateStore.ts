/**
 * 模板管理状态
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { PromptTemplate } from '../types'
import { templateService, type TemplateCreateRequest } from '../services/templateService'

export const useTemplateStore = defineStore('template', () => {
  // 状态
  const loading = ref(false)
  const error = ref<string | null>(null)
  const templates = ref<PromptTemplate[]>([])
  const currentTemplate = ref<PromptTemplate | null>(null)
  const total = ref(0)

  // 计算属性
  const hasTemplates = computed(() => templates.value.length > 0)

  // 方法
  async function fetchTemplates(params?: {
    task_type?: string
    domain?: string
    limit?: number
    skip?: number
  }): Promise<void> {
    loading.value = true
    error.value = null

    try {
      const response = await templateService.list(params)
      templates.value = response.templates
      total.value = response.total
    } catch (err: any) {
      error.value = err.message || '获取模板列表失败'
      console.error('获取模板列表错误:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchTemplate(templateId: string): Promise<void> {
    loading.value = true
    error.value = null

    try {
      currentTemplate.value = await templateService.get(templateId)
    } catch (err: any) {
      error.value = err.message || '获取模板失败'
      console.error('获取模板错误:', err)
    } finally {
      loading.value = false
    }
  }

  async function createTemplate(request: TemplateCreateRequest): Promise<PromptTemplate | null> {
    loading.value = true
    error.value = null

    try {
      const template = await templateService.create(request)
      templates.value.unshift(template)
      total.value += 1
      return template
    } catch (err: any) {
      error.value = err.message || '创建模板失败'
      console.error('创建模板错误:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function updateTemplate(
    templateId: string,
    updates: Partial<TemplateCreateRequest>
  ): Promise<PromptTemplate | null> {
    loading.value = true
    error.value = null

    try {
      const updated = await templateService.update(templateId, updates)
      
      // 更新列表中的模板
      const index = templates.value.findIndex(t => t.template_id === templateId)
      if (index !== -1) {
        templates.value[index] = updated
      }
      
      if (currentTemplate.value?.template_id === templateId) {
        currentTemplate.value = updated
      }

      return updated
    } catch (err: any) {
      error.value = err.message || '更新模板失败'
      console.error('更新模板错误:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  async function deleteTemplate(templateId: string): Promise<boolean> {
    loading.value = true
    error.value = null

    try {
      await templateService.delete(templateId)
      
      // 从列表中移除
      templates.value = templates.value.filter(t => t.template_id !== templateId)
      total.value -= 1
      
      if (currentTemplate.value?.template_id === templateId) {
        currentTemplate.value = null
      }

      return true
    } catch (err: any) {
      error.value = err.message || '删除模板失败'
      console.error('删除模板错误:', err)
      return false
    } finally {
      loading.value = false
    }
  }

  return {
    // 状态
    loading,
    error,
    templates,
    currentTemplate,
    total,
    // 计算属性
    hasTemplates,
    // 方法
    fetchTemplates,
    fetchTemplate,
    createTemplate,
    updateTemplate,
    deleteTemplate,
  }
})

