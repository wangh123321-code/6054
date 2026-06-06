<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <h1 class="text-2xl font-bold text-gray-900 mb-6">匠人工作台</h1>

    <div v-if="schedule" class="grid grid-cols-2 gap-4 mb-8">
      <div class="bg-white rounded-xl p-5 shadow-sm text-center">
        <p class="text-sm text-gray-500">本月任务</p>
        <p class="text-3xl font-bold text-[var(--color-primary)] mt-1">{{ schedule.assigned_count }}</p>
      </div>
      <div class="bg-white rounded-xl p-5 shadow-sm text-center">
        <p class="text-sm text-gray-500">产能上限</p>
        <p class="text-3xl font-bold text-[var(--color-gold)] mt-1">{{ schedule.capacity }}</p>
      </div>
    </div>

    <div v-if="loading" class="text-center py-20 text-gray-400">加载中...</div>

    <div v-else-if="tasks.length === 0" class="text-center py-20 text-gray-400">暂无任务</div>

    <div v-else class="bg-white rounded-xl shadow-sm overflow-hidden">
      <table class="w-full">
        <thead class="bg-gray-50">
          <tr>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">订单号</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">状态</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">分配时间</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">截止日期</th>
            <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">操作</th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-100">
          <tr v-for="task in tasks" :key="task.order_id" class="hover:bg-gray-50">
            <td class="px-6 py-4 text-sm font-medium text-gray-900">{{ task.order_no }}</td>
            <td class="px-6 py-4"><span :class="['badge', statusBadgeClass(task.status)]">{{ statusLabel(task.status) }}</span></td>
            <td class="px-6 py-4 text-sm text-gray-500">{{ formatDate(task.assigned_at) }}</td>
            <td class="px-6 py-4 text-sm text-gray-500">{{ task.deadline ? formatDate(task.deadline) : '-' }}</td>
            <td class="px-6 py-4">
              <button @click="toggleExpand(task.order_id)" class="text-sm text-[var(--color-primary)] hover:underline">
                {{ expandedTaskId === task.order_id ? '收起' : '展开' }}
              </button>
            </td>
          </tr>
        </tbody>
      </table>

      <div v-if="expandedTaskId" class="border-t border-gray-100 p-6 bg-gray-50 space-y-4">
        <h3 class="font-medium text-gray-900">上传进度照片</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm text-gray-600 mb-1">图片URL</label>
            <input v-model="photoForm.image_url" type="url" placeholder="请输入图片链接" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none" />
          </div>
          <div>
            <label class="block text-sm text-gray-600 mb-1">描述</label>
            <input v-model="photoForm.description" type="text" placeholder="照片描述" class="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none" />
          </div>
        </div>
        <button @click="handleUploadPhoto" class="btn-primary text-sm">上传照片</button>

        <div class="flex flex-wrap gap-3 items-center pt-2">
          <label class="text-sm text-gray-600">修改状态：</label>
          <select v-model="taskNewStatus" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none">
            <option value="in_progress">制作中</option>
            <option value="qc">质检中</option>
            <option value="completed">已完成</option>
          </select>
          <button @click="handleTaskStatusUpdate" class="btn-primary text-sm">确认修改</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import api from '@/api'
import { useOrderStore } from '@/stores/order'
import type { ArtisanTask, ArtisanSchedule } from '@/types'

const orderStore = useOrderStore()
const loading = ref(false)
const tasks = ref<ArtisanTask[]>([])
const schedule = ref<ArtisanSchedule | null>(null)
const expandedTaskId = ref<number | null>(null)
const taskNewStatus = ref('in_progress')
const photoForm = reactive({ image_url: '', description: '' })

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '待分配', assigned: '已分配', in_progress: '制作中',
    qc: '质检中', shipped: '已发货', completed: '已完成', cancelled: '已取消',
  }
  return map[status] ?? status
}

function statusBadgeClass(status: string) {
  const map: Record<string, string> = {
    pending: 'bg-yellow-100 text-yellow-700',
    assigned: 'bg-blue-100 text-blue-700',
    in_progress: 'bg-orange-100 text-orange-700',
    qc: 'bg-purple-100 text-purple-700',
    shipped: 'bg-green-100 text-green-700',
    completed: 'bg-gray-100 text-gray-700',
    cancelled: 'bg-red-100 text-red-700',
  }
  return map[status] ?? 'bg-gray-100 text-gray-700'
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

function toggleExpand(orderId: number) {
  expandedTaskId.value = expandedTaskId.value === orderId ? null : orderId
  photoForm.image_url = ''
  photoForm.description = ''
  taskNewStatus.value = 'in_progress'
}

async function handleUploadPhoto() {
  if (!expandedTaskId.value || !photoForm.image_url) return
  await orderStore.uploadProgressPhoto(expandedTaskId.value, {
    image_url: photoForm.image_url,
    description: photoForm.description || undefined,
  })
  photoForm.image_url = ''
  photoForm.description = ''
}

async function handleTaskStatusUpdate() {
  if (!expandedTaskId.value) return
  await orderStore.updateStatus(expandedTaskId.value, taskNewStatus.value)
  await loadTasks()
}

async function loadTasks() {
  loading.value = true
  try {
    const { data } = await api.get('/artisans/my-tasks')
    tasks.value = data
  } finally {
    loading.value = false
  }
}

async function loadSchedule() {
  try {
    const { data } = await api.get('/artisans/my-schedule')
    schedule.value = data
  } catch {}
}

onMounted(() => {
  loadTasks()
  loadSchedule()
})
</script>
