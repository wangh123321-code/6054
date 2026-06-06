<template>
  <div class="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div v-if="!product" class="text-center py-20 text-gray-400">加载中...</div>

    <div v-else>
      <div class="flex items-center gap-4 mb-8 bg-white rounded-xl p-4 shadow-sm">
        <img :src="product.template_image_url || `https://picsum.photos/seed/${product.id}/80/80`" :alt="product.name" class="w-16 h-16 rounded-lg object-cover" />
        <div>
          <h2 class="font-semibold text-gray-900">{{ product.name }}</h2>
          <p class="text-[var(--color-primary)] font-bold">¥{{ product.price_base }}</p>
        </div>
      </div>

      <form @submit.prevent="handleSubmit" class="bg-white rounded-xl p-6 shadow-sm space-y-6">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">尺寸选择</label>
          <select v-model="form.custom_size" class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition">
            <option value="30cm">30cm</option>
            <option value="50cm">50cm</option>
            <option value="80cm">80cm</option>
            <option value="100cm">100cm</option>
          </select>
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">配色选择</label>
          <select v-model="form.custom_color" class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition">
            <option value="中国红">中国红</option>
            <option value="金色">金色</option>
            <option value="蓝色">蓝色</option>
            <option value="紫色">紫色</option>
            <option value="自定义">自定义</option>
          </select>
          <input
            v-if="form.custom_color === '自定义'"
            v-model="customColorInput"
            type="text"
            placeholder="请输入自定义颜色"
            class="w-full border border-gray-300 rounded-lg px-4 py-2.5 mt-2 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition"
          />
        </div>

        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">祝福语</label>
          <textarea
            v-model="form.custom_message"
            rows="3"
            placeholder="请输入您想刻在作品上的祝福语"
            class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition resize-none"
          ></textarea>
        </div>

        <div class="flex items-center justify-between">
          <label class="text-sm font-medium text-gray-700">原创设计</label>
          <button
            type="button"
            @click="form.is_original = !form.is_original"
            :class="['relative inline-flex h-6 w-11 items-center rounded-full transition', form.is_original ? 'bg-[var(--color-primary)]' : 'bg-gray-300']"
          >
            <span :class="['inline-block h-4 w-4 transform rounded-full bg-white transition-transform', form.is_original ? 'translate-x-6' : 'translate-x-1']"></span>
          </button>
        </div>

        <div v-if="form.is_original">
          <label class="block text-sm font-medium text-gray-700 mb-2">参考图URL</label>
          <input
            v-model="form.reference_image_url"
            type="url"
            placeholder="请输入参考图片链接"
            class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition"
          />
        </div>

        <div class="border-t border-gray-100 pt-6">
          <div class="flex items-center justify-between mb-6">
            <span class="text-gray-700">预估价格</span>
            <span class="text-2xl font-bold text-[var(--color-primary)]">¥{{ calculatedPrice }}</span>
          </div>
          <button type="submit" :disabled="submitting" class="btn-primary w-full text-center disabled:opacity-50">
            {{ submitting ? '提交中...' : '提交订单' }}
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '@/stores/product'
import { useOrderStore } from '@/stores/order'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const orderStore = useOrderStore()
const submitting = ref(false)
const customColorInput = ref('')

const form = reactive({
  custom_size: '50cm',
  custom_color: '中国红',
  custom_message: '',
  reference_image_url: '',
  is_original: false,
})

const product = computed(() => productStore.currentProduct)

const calculatedPrice = computed(() => {
  if (!product.value) return 0
  let price = product.value.price_base
  const sizeMap: Record<string, number> = { '30cm': 0.8, '50cm': 1, '80cm': 1.5, '100cm': 2 }
  price *= sizeMap[form.custom_size] ?? 1
  if (form.is_original) price += 200
  return Math.round(price)
})

async function handleSubmit() {
  submitting.value = true
  try {
    const color = form.custom_color === '自定义' ? customColorInput.value : form.custom_color
    const order = await orderStore.placeOrder({
      product_id: Number(route.params.productId),
      total_price: calculatedPrice.value,
      custom_size: form.custom_size,
      custom_color: color,
      custom_message: form.custom_message || undefined,
      reference_image_url: form.is_original ? form.reference_image_url || undefined : undefined,
      is_original: form.is_original,
    })
    router.push(`/orders/${order.id}`)
  } catch {
    alert('提交失败，请重试')
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  productStore.fetchProduct(Number(route.params.productId))
})
</script>
