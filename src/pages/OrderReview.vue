<template>
  <div class="max-w-2xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <button @click="router.push('/orders')" class="flex items-center gap-1 text-sm text-gray-500 hover:text-red-600 mb-6">
      <ChevronLeft class="w-4 h-4" /> 返回订单列表
    </button>

    <div v-if="orderStore.loading" class="text-center py-20 text-gray-400">加载中...</div>

    <div v-else-if="order" class="space-y-6">
      <div class="bg-white rounded-xl p-6 shadow-sm">
        <h1 class="text-xl font-bold text-gray-900 mb-4">订单评价</h1>
        <div class="flex items-center justify-between text-sm text-gray-600 mb-4">
          <span>订单号：{{ order.order_no }}</span>
          <span>金额：<span class="text-[var(--color-primary)] font-bold">¥{{ order.total_price }}</span></span>
        </div>
        <div v-if="order.custom_message" class="text-sm text-gray-500">
          祝福语：{{ order.custom_message }}
        </div>
      </div>

      <div v-if="order.status === 'awaiting_review'" class="bg-white rounded-xl p-6 shadow-sm">
        <h2 class="font-semibold text-gray-900 mb-6">请为您的订单评分</h2>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-3">商品评分</label>
          <div class="flex items-center gap-2">
            <button
              v-for="star in 5"
              :key="star"
              @click="rating = star"
              class="focus:outline-none transition-transform hover:scale-110"
            >
              <Star
                :class="['w-10 h-10', rating >= star ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300']"
              />
            </button>
            <span class="ml-3 text-lg font-medium text-gray-700">{{ ratingText }}</span>
          </div>
        </div>

        <div class="mb-6">
          <label class="block text-sm font-medium text-gray-700 mb-2">评价内容（选填）</label>
          <textarea
            v-model="comment"
            rows="4"
            placeholder="分享您的购物体验，帮助其他用户做出选择..."
            class="w-full border border-gray-300 rounded-lg px-4 py-3 text-sm focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none resize-none"
          ></textarea>
          <p class="text-xs text-gray-400 mt-1">最多500字</p>
        </div>

        <div v-if="error" class="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 text-sm rounded-lg">
          {{ error }}
        </div>

        <button
          @click="handleSubmit"
          :disabled="submitting || rating === 0"
          class="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {{ submitting ? '提交中...' : '提交评价' }}
        </button>
      </div>

      <div v-else-if="order.status === 'completed' && existingReview" class="bg-white rounded-xl p-6 shadow-sm">
        <div class="flex items-center gap-2 mb-4">
          <CheckCircle class="w-6 h-6 text-green-500" />
          <h2 class="font-semibold text-gray-900">您已完成评价</h2>
        </div>
        <div class="flex items-center gap-1 mb-3">
          <Star
            v-for="star in 5"
            :key="star"
            :class="['w-5 h-5', existingReview.rating >= star ? 'text-yellow-400 fill-yellow-400' : 'text-gray-300']"
          />
          <span class="ml-2 text-sm text-gray-600">{{ existingReview.rating }} 星</span>
        </div>
        <p v-if="existingReview.comment" class="text-gray-700 text-sm">{{ existingReview.comment }}</p>
        <p class="text-xs text-gray-400 mt-3">评价时间：{{ formatDate(existingReview.created_at) }}</p>
      </div>

      <div v-else class="bg-white rounded-xl p-6 shadow-sm text-center py-10">
        <AlertCircle class="w-12 h-12 text-gray-300 mx-auto mb-3" />
        <p class="text-gray-500">该订单暂不可评价</p>
        <p class="text-sm text-gray-400 mt-1">请先确认收货后再进行评价</p>
      </div>
    </div>

    <div v-else class="text-center py-20 text-gray-400">订单不存在</div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ChevronLeft, Star, CheckCircle, AlertCircle } from 'lucide-vue-next'
import { useOrderStore } from '@/stores/order'
import type { Review } from '@/types'

const route = useRoute()
const router = useRouter()
const orderStore = useOrderStore()

const rating = ref(0)
const comment = ref('')
const submitting = ref(false)
const error = ref('')
const existingReview = ref<Review | null>(null)

const order = computed(() => orderStore.currentOrder)

const ratingText = computed(() => {
  const texts: Record<number, string> = {
    1: '非常差',
    2: '差',
    3: '一般',
    4: '满意',
    5: '非常满意',
  }
  return texts[rating.value] || '请点击星星评分'
})

function formatDate(dateStr: string) {
  return new Date(dateStr).toLocaleString('zh-CN')
}

async function handleSubmit() {
  if (rating.value === 0) {
    error.value = '请选择评分'
    return
  }
  if (comment.value.length > 500) {
    error.value = '评价内容不能超过500字'
    return
  }

  submitting.value = true
  error.value = ''

  try {
    const orderId = Number(route.params.id)
    await orderStore.submitReview(orderId, {
      rating: rating.value,
      comment: comment.value || undefined,
    })
    alert('评价提交成功！')
    router.push('/orders')
  } catch (e: any) {
    error.value = e.response?.data?.detail || '提交失败，请重试'
  } finally {
    submitting.value = false
  }
}

async function loadData() {
  const orderId = Number(route.params.id)
  if (orderId) {
    await orderStore.fetchOrder(orderId)
    try {
      const review = await orderStore.fetchOrderReview(orderId)
      existingReview.value = review
    } catch {
      existingReview.value = null
    }
  }
}

onMounted(() => {
  loadData()
})
</script>
