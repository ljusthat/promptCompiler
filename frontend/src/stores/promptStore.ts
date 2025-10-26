/**
 * Prompt 编译状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type {
  CompileRequest,
  CompileResponse,
  OptimizeRequest,
  OptimizeResponse,
  CompiledPrompt,
  QualityMetrics,
} from '../types'
import { promptService } from '../services/promptService'
import { OptimizationLevel } from '../types'

// 编译进度状态
export enum CompileProgress {
  IDLE = 'idle',
  STARTING = 'starting',
  EXTRACTING_INTENT = 'extracting_intent',
  GENERATING_PROMPT = 'generating_prompt',
  OPTIMIZING = 'optimizing',
  SELF_CHECKING = 'self_checking',
  EVALUATING = 'evaluating',
  COMPLETED = 'completed',
  ERROR = 'error',
}

export const usePromptStore = defineStore('prompt', () => {
  // 状态
  const loading = ref(false)
  const progress = ref<CompileProgress>(CompileProgress.IDLE)
  const error = ref<string | null>(null)
  const currentPrompt = ref<CompiledPrompt | null>(null)
  const currentMetrics = ref<QualityMetrics | null>(null)
  const suggestions = ref<string[]>([])

  // 计算属性
  const hasPrompt = computed(() => currentPrompt.value !== null)
  const qualityScore = computed(() => currentMetrics.value?.overall_score || 0)
  
  // 获取进度文本
  const progressText = computed(() => {
    const progressMap = {
      [CompileProgress.IDLE]: '等待开始',
      [CompileProgress.STARTING]: '启动服务中...',
      [CompileProgress.EXTRACTING_INTENT]: '提取意图中...',
      [CompileProgress.GENERATING_PROMPT]: '生成 Prompt 中...',
      [CompileProgress.OPTIMIZING]: '优化中...',
      [CompileProgress.SELF_CHECKING]: '自检中...',
      [CompileProgress.EVALUATING]: '质量评估中...',
      [CompileProgress.COMPLETED]: '编译完成',
      [CompileProgress.ERROR]: '编译失败',
    }
    return progressMap[progress.value] || '处理中...'
  })

  // 方法
  async function compile(request: CompileRequest): Promise<CompileResponse | null> {
    loading.value = true
    error.value = null
    progress.value = CompileProgress.STARTING

    // 模拟进度更新
    const progressInterval = setInterval(() => {
      if (progress.value === CompileProgress.STARTING) {
        progress.value = CompileProgress.EXTRACTING_INTENT
      } else if (progress.value === CompileProgress.EXTRACTING_INTENT) {
        progress.value = CompileProgress.GENERATING_PROMPT
      } else if (progress.value === CompileProgress.GENERATING_PROMPT) {
        if (request.optimization_level !== OptimizationLevel.LOW) {
          progress.value = CompileProgress.OPTIMIZING
        } else {
          progress.value = CompileProgress.SELF_CHECKING
        }
      } else if (progress.value === CompileProgress.OPTIMIZING) {
        progress.value = CompileProgress.SELF_CHECKING
      } else if (progress.value === CompileProgress.SELF_CHECKING && request.auto_evaluate) {
        progress.value = CompileProgress.EVALUATING
      }
    }, 3000) // 每3秒更新一次进度

    try {
      const response = await promptService.compile(request)
      
      // 清除进度更新定时器
      clearInterval(progressInterval)
      
      // 确保response有正确的结构
      if (response && response.compiled_prompt) {
        currentPrompt.value = response.compiled_prompt
        currentMetrics.value = response.metrics || null
        suggestions.value = response.suggestions || []
        
        progress.value = CompileProgress.COMPLETED
      } else {
        throw new Error('响应格式不正确')
      }

      return response
    } catch (err: any) {
      clearInterval(progressInterval)
      progress.value = CompileProgress.ERROR
      
      // 改进错误信息显示
      let errorMessage = '编译失败'
      if (err?.message) {
        errorMessage = err.message
      } else if (typeof err === 'string') {
        errorMessage = err
      }
      
      error.value = errorMessage
      console.error('编译错误:', err)
      return null
    } finally {
      loading.value = false
      // 延迟后重置进度状态
      setTimeout(() => {
        if (progress.value !== CompileProgress.ERROR) {
          progress.value = CompileProgress.IDLE
        }
      }, 2000)
    }
  }

  async function optimize(request: OptimizeRequest): Promise<OptimizeResponse | null> {
    loading.value = true
    error.value = null

    try {
      const response = await promptService.optimize(request)
      return response
    } catch (err: any) {
      error.value = err.message || '优化失败'
      console.error('优化错误:', err)
      return null
    } finally {
      loading.value = false
    }
  }

  function reset() {
    currentPrompt.value = null
    currentMetrics.value = null
    suggestions.value = []
    error.value = null
  }

  return {
    // 状态
    loading,
    progress,
    error,
    currentPrompt,
    currentMetrics,
    suggestions,
    // 计算属性
    hasPrompt,
    qualityScore,
    progressText,
    // 方法
    compile,
    optimize,
    reset,
  }
})

