<template>
  <div class="prompt-compiler">
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- 左侧：输入区域 -->
      <div class="space-y-6">
        <div class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">输入您的需求</h2>
          
          <!-- 输入框 -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              描述您想要的 Prompt
            </label>
            <textarea
              v-model="userInput"
              rows="6"
              class="w-full px-3 py-2 border border-gray-300 rounded-md focus:ring-primary-500 focus:border-primary-500"
              placeholder="例如：帮我写一个分析财报的AI助手"
            ></textarea>
          </div>

          <!-- 优化级别选择 -->
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 mb-2">
              优化级别
            </label>
            <div class="flex space-x-4">
              <label v-for="level in optimizationLevels" :key="level.value" class="flex items-center">
                <input
                  type="radio"
                  :value="level.value"
                  v-model="optimizationLevel"
                  class="mr-2"
                />
                <span>{{ level.label }}</span>
              </label>
            </div>
          </div>

          <!-- 自动评估选项 -->
          <div class="mb-4">
            <label class="flex items-center">
              <input
                type="checkbox"
                v-model="autoEvaluate"
                class="mr-2"
              />
              <span class="text-sm text-gray-700">自动进行质量评估</span>
            </label>
          </div>

          <!-- 编译按钮 -->
          <button
            @click="handleCompile"
            :disabled="!userInput || loading"
            class="w-full bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition"
          >
            <span v-if="loading">{{ promptStore.progressText }}</span>
            <span v-else>编译 Prompt</span>
          </button>
          
          <!-- 进度指示器 -->
          <div v-if="loading && promptStore.progress" class="mt-4">
            <div class="flex items-center">
              <div class="flex-1 bg-gray-200 rounded-full h-2">
                <div 
                  class="bg-primary-600 h-2 rounded-full transition-all duration-500"
                  :style="{ width: progressPercentage + '%' }"
                ></div>
              </div>
              <span class="ml-3 text-sm text-gray-600">{{ promptStore.progressText }}</span>
            </div>
          </div>

          <!-- 错误提示 -->
          <div v-if="error" class="mt-4 p-3 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
            {{ error }}
          </div>
        </div>
      </div>

      <!-- 右侧：结果区域 -->
      <div class="space-y-6">
        <div v-if="hasPrompt" class="bg-white rounded-lg shadow p-6">
          <h2 class="text-xl font-semibold mb-4">编译结果</h2>

          <!-- 质量指标 -->
          <div v-if="currentMetrics" class="mb-6">
            <h3 class="text-sm font-medium text-gray-700 mb-3">质量评估</h3>
            <div class="grid grid-cols-2 gap-3">
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-xs text-gray-500">结构合规率</div>
                <div class="text-lg font-semibold">{{ (currentMetrics.structure_score * 100).toFixed(1) }}%</div>
              </div>
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-xs text-gray-500">目标一致性</div>
                <div class="text-lg font-semibold">{{ (currentMetrics.consistency_score * 100).toFixed(1) }}%</div>
              </div>
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-xs text-gray-500">语义完整度</div>
                <div class="text-lg font-semibold">{{ (currentMetrics.completeness_score * 100).toFixed(1) }}%</div>
              </div>
              <div class="bg-gray-50 p-3 rounded">
                <div class="text-xs text-gray-500">表达清晰度</div>
                <div class="text-lg font-semibold">{{ (currentMetrics.clarity_score * 100).toFixed(1) }}%</div>
              </div>
            </div>
            <div class="mt-3 p-3 rounded" :class="getOverallScoreClass(currentMetrics.overall_score)">
              <div class="text-sm font-medium">综合评分</div>
              <div class="text-2xl font-bold">{{ (currentMetrics.overall_score * 100).toFixed(1) }}%</div>
            </div>
          </div>

          <!-- 编译后的 Prompt -->
          <div class="mb-4">
            <h3 class="text-sm font-medium text-gray-700 mb-2">编译后的 Prompt</h3>
            <div class="bg-gray-50 p-4 rounded-lg overflow-auto max-h-96">
              <pre class="text-sm whitespace-pre-wrap">{{ currentPrompt?.full_prompt }}</pre>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="flex space-x-3">
            <button
              @click="copyPrompt"
              class="flex-1 bg-white border border-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-50 transition"
            >
              复制
            </button>
            <button
              @click="downloadPrompt"
              class="flex-1 bg-white border border-gray-300 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-50 transition"
            >
              下载
            </button>
          </div>

          <!-- 建议 -->
          <div v-if="suggestions.length > 0" class="mt-4">
            <h3 class="text-sm font-medium text-gray-700 mb-2">优化建议</h3>
            <ul class="space-y-1">
              <li
                v-for="(suggestion, index) in suggestions"
                :key="index"
                class="text-sm text-gray-600"
              >
                • {{ suggestion }}
              </li>
            </ul>
          </div>
        </div>

        <!-- 空状态 -->
        <div v-else class="bg-white rounded-lg shadow p-6 text-center text-gray-500">
          <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <p class="mt-2">输入您的需求并点击"编译 Prompt"开始</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { usePromptStore, CompileProgress } from '../stores/promptStore'
import { OptimizationLevel } from '../types'
import type { CompileRequest } from '../types'

const promptStore = usePromptStore()

// 响应式状态
const userInput = ref('')
const optimizationLevel = ref<OptimizationLevel>(OptimizationLevel.MEDIUM)
const autoEvaluate = ref(true)

// 优化级别选项
const optimizationLevels = [
  { value: OptimizationLevel.LOW, label: '低' },
  { value: OptimizationLevel.MEDIUM, label: '中' },
  { value: OptimizationLevel.HIGH, label: '高' },
]

// 从 store 获取状态
const loading = computed(() => promptStore.loading)
const error = computed(() => promptStore.error)
const currentPrompt = computed(() => promptStore.currentPrompt)
const currentMetrics = computed(() => promptStore.currentMetrics)
const suggestions = computed(() => promptStore.suggestions)
const hasPrompt = computed(() => promptStore.hasPrompt)

// 计算进度百分比
const progressPercentage = computed(() => {
  const progressMap: Record<CompileProgress, number> = {
    [CompileProgress.IDLE]: 0,
    [CompileProgress.STARTING]: 10,
    [CompileProgress.EXTRACTING_INTENT]: 25,
    [CompileProgress.GENERATING_PROMPT]: 40,
    [CompileProgress.OPTIMIZING]: 60,
    [CompileProgress.SELF_CHECKING]: 80,
    [CompileProgress.EVALUATING]: 90,
    [CompileProgress.COMPLETED]: 100,
    [CompileProgress.ERROR]: 0,
  }
  return progressMap[promptStore.progress] || 0
})

// 编译 Prompt
async function handleCompile() {
  if (!userInput.value) return

  const request: CompileRequest = {
    user_input: userInput.value,
    optimization_level: optimizationLevel.value,
    auto_evaluate: autoEvaluate.value,
  }

  await promptStore.compile(request)
}

// 复制 Prompt
function copyPrompt() {
  if (currentPrompt.value) {
    navigator.clipboard.writeText(currentPrompt.value.full_prompt)
    alert('已复制到剪贴板')
  }
}

// 下载 Prompt
function downloadPrompt() {
  if (currentPrompt.value) {
    const blob = new Blob([currentPrompt.value.full_prompt], { type: 'text/plain' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `prompt_${currentPrompt.value.version_id}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }
}

// 获取综合评分的样式类
function getOverallScoreClass(score: number): string {
  if (score >= 0.8) return 'bg-green-100 text-green-800'
  if (score >= 0.6) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}
</script>

<style scoped>
.prompt-compiler {
  /* 组件样式 */
}
</style>

