<template>
  <div class="template-management">
    <div class="bg-white rounded-lg shadow">
      <div class="p-6 border-b border-gray-200">
        <div class="flex justify-between items-center">
          <h2 class="text-2xl font-semibold">模板管理</h2>
          <button
            @click="showCreateModal = true"
            class="bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700 transition"
          >
            创建模板
          </button>
        </div>
      </div>

      <!-- 模板列表 -->
      <div class="p-6">
        <div v-if="loading" class="text-center py-8 text-gray-500">
          加载中...
        </div>

        <div v-else-if="hasTemplates" class="space-y-4">
          <div
            v-for="template in templates"
            :key="template.template_id"
            class="border border-gray-200 rounded-lg p-4 hover:shadow-md transition"
          >
            <div class="flex justify-between items-start">
              <div class="flex-1">
                <h3 class="text-lg font-medium">{{ template.name }}</h3>
                <p class="text-sm text-gray-600 mt-1">{{ template.description }}</p>
                <div class="mt-2 flex flex-wrap gap-2">
                  <span
                    v-for="tag in template.tags"
                    :key="tag"
                    class="inline-block bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded"
                  >
                    {{ tag }}
                  </span>
                </div>
                <div class="mt-2 text-sm text-gray-500">
                  使用次数: {{ template.usage_count }} | 
                  平均评分: {{ (template.avg_quality_score * 100).toFixed(1) }}%
                </div>
              </div>
              <div class="flex space-x-2">
                <button
                  @click="viewTemplate(template)"
                  class="text-primary-600 hover:text-primary-700"
                >
                  查看
                </button>
                <button
                  @click="deleteTemplateConfirm(template)"
                  class="text-red-600 hover:text-red-700"
                >
                  删除
                </button>
              </div>
            </div>
          </div>
        </div>

        <div v-else class="text-center py-8 text-gray-500">
          暂无模板，点击"创建模板"开始
        </div>
      </div>
    </div>

    <!-- 创建模板模态框（简化版） -->
    <div v-if="showCreateModal" class="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div class="bg-white rounded-lg p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <h3 class="text-xl font-semibold mb-4">创建模板</h3>
        <div class="space-y-4">
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">模板名称</label>
            <input
              v-model="newTemplate.name"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="输入模板名称"
            />
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">描述</label>
            <textarea
              v-model="newTemplate.description"
              rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="简要描述模板用途"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">角色定义</label>
            <textarea
              v-model="newTemplate.role"
              rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="例如：你是一位专业的数据分析专家"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">任务目标</label>
            <textarea
              v-model="newTemplate.objective"
              rows="2"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="描述任务的核心目标"
            ></textarea>
          </div>
          <div>
            <label class="block text-sm font-medium text-gray-700 mb-1">输出格式</label>
            <input
              v-model="newTemplate.output_format"
              type="text"
              class="w-full px-3 py-2 border border-gray-300 rounded-md"
              placeholder="描述期望的输出格式"
            />
          </div>
        </div>
        <div class="mt-6 flex space-x-3">
          <button
            @click="handleCreateTemplate"
            class="flex-1 bg-primary-600 text-white py-2 px-4 rounded-md hover:bg-primary-700"
          >
            创建
          </button>
          <button
            @click="showCreateModal = false"
            class="flex-1 bg-gray-200 text-gray-700 py-2 px-4 rounded-md hover:bg-gray-300"
          >
            取消
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useTemplateStore } from '../stores/templateStore'
import type { TemplateCreateRequest } from '../services/templateService'

const templateStore = useTemplateStore()

const showCreateModal = ref(false)
const newTemplate = ref<TemplateCreateRequest>({
  name: '',
  description: '',
  role: '',
  objective: '',
  output_format: '',
  constraints: [],
  context_vars: {},
  task_types: [],
  domains: [],
  tags: [],
})

const loading = computed(() => templateStore.loading)
const templates = computed(() => templateStore.templates)
const hasTemplates = computed(() => templateStore.hasTemplates)

onMounted(() => {
  templateStore.fetchTemplates()
})

async function handleCreateTemplate() {
  if (!newTemplate.value.name || !newTemplate.value.role || !newTemplate.value.objective) {
    alert('请填写必填字段')
    return
  }

  const result = await templateStore.createTemplate(newTemplate.value)
  if (result) {
    showCreateModal.value = false
    // 重置表单
    newTemplate.value = {
      name: '',
      description: '',
      role: '',
      objective: '',
      output_format: '',
      constraints: [],
      context_vars: {},
      task_types: [],
      domains: [],
      tags: [],
    }
  }
}

function viewTemplate(template: any) {
  // 简化版，仅显示alert
  alert(`模板详情：\n\n${JSON.stringify(template, null, 2)}`)
}

async function deleteTemplateConfirm(template: any) {
  if (confirm(`确定要删除模板"${template.name}"吗？`)) {
    await templateStore.deleteTemplate(template.template_id)
  }
}
</script>

