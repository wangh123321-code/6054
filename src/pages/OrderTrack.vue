<template>
  <div class="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <template v-if="!isDetailMode">
      <h1 class="text-2xl font-bold text-gray-900 mb-6">我的订单</h1>
      <div v-if="orderStore.loading" class="text-center py-20 text-gray-400">加载中...</div>
      <div v-else-if="orderStore.orders.length === 0" class="text-center py-20 text-gray-400">暂无订单</div>
      <div v-else class="space-y-4">
        <div
          v-for="order in orderStore.orders"
          :key="order.id"
          class="bg-white rounded-xl p-5 shadow-sm hover:shadow-md transition"
        >
          <div @click="router.push(`/orders/${order.id}`)" class="cursor-pointer">
            <div class="flex items-center justify-between">
              <div>
                <p class="font-semibold text-gray-900">{{ order.order_no }}</p>
                <p class="text-sm text-gray-500 mt-1">{{ formatDate(order.created_at) }}</p>
              </div>
              <div class="text-right">
                <span :class="['badge', statusBadgeClass(order.status)]">{{ statusLabel(order.status) }}</span>
                <p class="text-[var(--color-primary)] font-bold mt-1">¥{{ order.total_price }}</p>
              </div>
            </div>
          </div>
          <div class="flex gap-2 mt-4 pt-4 border-t border-gray-100">
            <button
              v-if="order.status === 'shipped'"
              @click.stop="handleConfirmReceipt(order.id)"
              class="btn-primary text-sm flex-1"
            >
              确认收货
            </button>
            <button
              v-if="order.status === 'awaiting_review'"
              @click.stop="router.push(`/orders/${order.id}/review`)"
              class="btn-primary text-sm flex-1"
            >
              去评价
            </button>
            <button
              v-if="order.status === 'completed'"
              @click.stop="router.push(`/orders/${order.id}/review`)"
              class="btn-outline text-sm flex-1"
            >
              查看评价
            </button>
          </div>
        </div>
      </div>
    </template>

    <template v-else>
      <button @click="router.push('/orders')" class="flex items-center gap-1 text-sm text-gray-500 hover:text-red-600 mb-4">
        <ChevronLeft class="w-4 h-4" /> 返回订单列表
      </button>

      <div v-if="orderStore.loading" class="text-center py-20 text-gray-400">加载中...</div>

      <div v-else-if="order" class="space-y-6">
        <div class="bg-white rounded-xl p-6 shadow-sm">
          <div class="flex items-center justify-between mb-4">
            <h1 class="text-xl font-bold text-gray-900">订单 {{ order.order_no }}</h1>
            <span :class="['badge', statusBadgeClass(order.status)]">{{ statusLabel(order.status) }}</span>
          </div>
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div><span class="text-gray-500">价格</span><p class="font-semibold text-[var(--color-primary)]">¥{{ order.total_price }}</p></div>
            <div><span class="text-gray-500">尺寸</span><p class="font-medium">{{ order.custom_size || '-' }}</p></div>
            <div><span class="text-gray-500">配色</span><p class="font-medium">{{ order.custom_color || '-' }}</p></div>
            <div><span class="text-gray-500">原创设计</span><p class="font-medium">{{ order.is_original ? '是' : '否' }}</p></div>
          </div>
          <div v-if="order.custom_message" class="mt-3 text-sm"><span class="text-gray-500">祝福语：</span>{{ order.custom_message }}</div>
          <div v-if="order.reference_image_url" class="mt-3 text-sm"><span class="text-gray-500">参考图：</span><a :href="order.reference_image_url" target="_blank" class="text-blue-600 hover:underline">查看图片</a></div>
        </div>

        <div class="bg-white rounded-xl p-6 shadow-sm">
          <h2 class="font-semibold text-gray-900 mb-6">订单进度</h2>
          <div class="flex items-center justify-between relative">
            <div class="absolute top-4 left-0 right-0 h-0.5 bg-gray-200"></div>
            <div class="absolute top-4 left-0 h-0.5 bg-[var(--color-primary)] transition-all duration-500" :style="{ width: progressPercent + '%' }"></div>
            <div v-for="(step, idx) in statusSteps" :key="step.key" class="relative flex flex-col items-center z-10">
              <div :class="['w-8 h-8 rounded-full flex items-center justify-center text-xs font-bold border-2 transition', stepIndex >= idx ? 'bg-[var(--color-primary)] text-white border-[var(--color-primary)]' : 'bg-white text-gray-400 border-gray-200']">
                {{ idx + 1 }}
              </div>
              <span class="text-xs mt-2" :class="stepIndex >= idx ? 'text-[var(--color-primary)] font-medium' : 'text-gray-400'">{{ step.label }}</span>
            </div>
          </div>
        </div>

        <div v-if="order.status === 'shipped' || order.status === 'awaiting_review' || order.status === 'completed'" class="bg-white rounded-xl p-6 shadow-sm">
          <h2 class="font-semibold text-gray-900 mb-4">评价操作</h2>
          <div class="flex gap-3">
            <button
              v-if="order.status === 'shipped'"
              @click="handleConfirmReceipt(order.id)"
              class="btn-primary flex-1"
            >
              确认收货
            </button>
            <button
              v-if="order.status === 'awaiting_review'"
              @click="router.push(`/orders/${order.id}/review`)"
              class="btn-primary flex-1"
            >
              去评价
            </button>
            <button
              v-if="order.status === 'completed'"
              @click="router.push(`/orders/${order.id}/review`)"
              class="btn-outline flex-1"
            >
              查看评价
            </button>
          </div>
        </div>

        <div v-if="order.assignments.length > 0" class="bg-white rounded-xl p-6 shadow-sm">
          <h2 class="font-semibold text-gray-900 mb-4">匠人信息</h2>
          <div v-for="a in order.assignments" :key="a.id" class="flex items-center gap-3">
            <div class="w-10 h-10 rounded-full bg-red-100 flex items-center justify-center text-red-600 font-bold">匠</div>
            <div>
              <p class="font-medium text-gray-900">匠人 #{{ a.artisan_id }}</p>
              <p class="text-sm text-gray-500">分配于 {{ formatDate(a.assigned_at) }}</p>
              <p v-if="a.deadline" class="text-sm text-gray-500">截止 {{ formatDate(a.deadline) }}</p>
            </div>
          </div>
        </div>

        <div v-if="order.progress_photos.length > 0" class="bg-white rounded-xl p-6 shadow-sm">
          <h2 class="font-semibold text-gray-900 mb-4">进度照片</h2>
          <div class="space-y-4">
            <div v-for="photo in order.progress_photos" :key="photo.id" class="flex gap-4">
              <div class="w-2 h-2 rounded-full bg-[var(--color-primary)] mt-2 shrink-0"></div>
              <div class="w-24 h-24 rounded-lg overflow-hidden shrink-0">
                <img :src="photo.image_url" :alt="photo.description" class="w-full h-full object-cover" />
              </div>
              <div>
                <p v-if="photo.description" class="text-sm text-gray-700">{{ photo.description }}</p>
                <p class="text-xs text-gray-400 mt-1">{{ formatDate(photo.uploaded_at) }}</p>
              </div>
            </div>
          </div>
        </div>

        <div v-if="isAdmin" class="bg-white rounded-xl p-6 shadow-sm space-y-4">
          <h2 class="font-semibold text-gray-900">管理操作</h2>
          <div class="flex flex-wrap gap-3">
            <select v-model="newStatus" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none">
              <option v-for="s in statusSteps" :key="s.key" :value="s.key">{{ s.label }}</option>
              <option value="cancelled">取消订单</option>
            </select>
            <button @click="handleUpdateStatus" class="btn-primary text-sm">修改状态</button>
          </div>
          <div v-if="order.status === 'pending'" class="flex flex-wrap gap-3 items-end">
            <div>
              <label class="text-sm text-gray-600">匠人ID</label>
              <input v-model.number="assignForm.artisan_id" type="number" class="border border-gray-300 rounded-lg px-3 py-2 text-sm w-24 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none" />
            </div>
            <div>
              <label class="text-sm text-gray-600">截止日期</label>
              <input v-model="assignForm.deadline" type="date" class="border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none" />
            </div>
            <button @click="handleAssignArtisan" class="btn-primary text-sm">分配匠人</button>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronLeft } from 'lucide-vue-next'
import { useOrderStore } from '@/stores/order'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const orderStore = useOrderStore()
const authStore = useAuthStore()

const isAdmin = computed(() => authStore.userRole === 'admin')
const isDetailMode = computed(() => !!route.params.id)
const order = computed(() => orderStore.currentOrder)

const newStatus = ref('')
const assignForm = reactive({ artisan_id: 0, deadline: '' })

const statusSteps = [
  { key: 'pending', label: '待分配' },
  { key: 'assigned', label: '已分配' },
  { key: 'in_progress', label: '制作中' },
  { key: 'qc', label: '质检中' },
  { key: 'shipped', label: '已发货' },
  { key: 'awaiting_review', label: '待评价' },
  { key: 'completed', label: '已完成' },
]

const stepIndex = computed(() => {
  if (!order.value) return -1
  return statusSteps.findIndex((s) => s.key === order.value!.status)
})

const progressPercent = computed(() => {
  if (stepIndex.value <= 0) return 0
  return (stepIndex.value / (statusSteps.length - 1)) * 100
})

function statusLabel(status: string) {
  const map: Record<string, string> = {
    pending: '待分配', assigned: '已分配', in_progress: '制作中',
    qc: '质检中', shipped: '已发货', awaiting_review: '待评价',
    completed: '已完成', cancelled: '已取消',
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
    awaiting_review: 'bg-amber-100 text-amber-700',
    completed: 'bg-gray-100 text-gray-700',
    cancelled: 'bg-red-100 text-red-700',
  }
  return map[status] ?? 'bg-gray-100 text-gray-700'
}

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function handleUpdateStatus() {
  if (!newStatus.value || !order.value) return
  await orderStore.updateStatus(order.value.id, newStatus.value)
  await orderStore.fetchOrder(order.value.id)
}

async function handleAssignArtisan() {
  if (!order.value || !assignForm.artisan_id) return
  await orderStore.assignArtisan(order.value.id, {
    artisan_id: assignForm.artisan_id,
    deadline: assignForm.deadline || undefined,
  })
  await orderStore.fetchOrder(order.value.id)
}

async function handleConfirmReceipt(orderId: number) {
  if (!confirm('确认已收到商品吗？')) return
  try {
    await orderStore.confirmReceipt(orderId)
    if (isDetailMode.value) {
      await orderStore.fetchOrder(orderId)
    } else {
      await orderStore.fetchOrders()
    }
    alert('确认收货成功，请对商品进行评价')
  } catch (e: any) {
    alert(e.response?.data?.detail || '操作失败，请重试')
  }
}

onMounted(() => {
  if (isDetailMode.value) {
    orderStore.fetchOrder(Number(route.params.id))
  } else {
    orderStore.fetchOrders()
  }
})
</script>
