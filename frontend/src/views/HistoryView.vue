<template>
  <div class="history-view">
    <div class="bg-white rounded-lg shadow">
      <div class="p-6 border-b border-gray-200">
        <h2 class="text-2xl font-semibold">历史记录</h2>
      </div>

      <div class="p-6">
        <div v-if="loading" class="text-center py-8 text-gray-500">
          加载中...
        </div>

        <div v-else-if="hasRecords" class="space-y-4">
          <div
            v-for="record in records"
            :key="record.version_id"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition cursor-pointer"
            @click="viewRecord(record)"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <div class="text-sm text-gray-500">
                  {{ formatDate(record.created_at) }}
                </div>
                <div class="mt-1 text-gray-700">
                  <span class="font-medium">输入：</span>{{ record.original_input }}
                </div>
                <div class="mt-2 flex items-center space-x-4 text-sm text-gray-600">
                  <span>任务类型: {{ record.intent.task_type }}</span>
                  <span>领域: {{ record.intent.domain }}</span>
                  <span>优化级别: {{ record.optimization_level }}</span>
                  <span v-if="record.optimized" class="text-green-600">✓ 已优化</span>
                </div>
              </div>
            </div>
          </div>

          <!-- 分页 -->
          <div class="flex justify-between items-center mt-6">
            <button
              @click="prevPage"
              :disabled="currentPage <= 1"
              class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              上一页
            </button>
            <span class="text-sm text-gray-600">
              第 {{ currentPage }} 页 / 共 {{ totalPages }} 页
            </span>
            <button
              @click="nextPage"
              :disabled="currentPage >= totalPages"
              class="px-4 py-2 border border-gray-300 rounded-md hover:bg-gray-50 disabled:bg-gray-100 disabled:cursor-not-allowed"
            >
              下一页
            </button>
          </div>
        </div>

        <div v-else class="text-center py-8 text-gray-500">
          暂无历史记录
        </div>
      </div>
    </div>

    <!-- 查看详情模态框 -->
    <div v-if="selectedRecord" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-4xl w-full max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-semibold mb-4">Prompt 详情</h3>
        <div class="space-y-4">
          <div>
            <div class="text-sm font-medium text-gray-700">原始输入</div>
            <div class="mt-1 p-3 bg-gray-50 rounded">{{ selectedRecord.original_input }}</div>
          </div>
          <div>
            <div class="text-sm font-medium text-gray-700">编译后的 Prompt</div>
            <div class="mt-1 p-3 bg-gray-50 rounded max-h-96 overflow-auto">
              <pre class="text-sm whitespace-pre-wrap">{{ selectedRecord.full_prompt }}</pre>
            </div>
          </div>
        </div>
        <div class="mt-6">
          <button
            @click="selectedRecord = null"
            class="w-full bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
          >
            关闭
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useHistoryStore } from '../stores/historyStore'
import type { CompiledPrompt } from '../types'

const historyStore = useHistoryStore()

const selectedRecord = ref<CompiledPrompt | null>(null)

const loading = computed(() => historyStore.loading)
const records = computed(() => historyStore.records)
const hasRecords = computed(() => historyStore.hasRecords)
const currentPage = computed(() => historyStore.currentPage)
const totalPages = computed(() => historyStore.totalPages)

onMounted(() => {
  historyStore.fetchHistory()
})

function formatDate(dateStr: string): string {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN')
}

function viewRecord(record: CompiledPrompt) {
  selectedRecord.value = record
}

function nextPage() {
  historyStore.nextPage()
}

function prevPage() {
  historyStore.prevPage()
}
</script>

