<template>
  <div>
    <section class="relative overflow-hidden" style="background: linear-gradient(135deg, var(--color-primary) 0%, var(--color-gold) 100%)">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20 text-center">
        <h1 class="text-4xl md:text-5xl font-bold text-white mb-4">莆田剪纸·指尖上的艺术</h1>
        <p class="text-lg md:text-xl text-white/90 mb-8">千年技艺，匠心传承——每一刀都是文化的温度</p>
        <router-link to="/" class="inline-block bg-white text-[var(--color-primary)] px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition">
          探索作品
        </router-link>
      </div>
    </section>

    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div class="flex items-center gap-3 mb-8 overflow-x-auto pb-2">
        <button
          v-for="cat in categories"
          :key="cat.key"
          @click="activeCategory = cat.key"
          :class="[
            'px-5 py-2 rounded-full text-sm font-medium transition whitespace-nowrap',
            activeCategory === cat.key
              ? 'bg-[var(--color-primary)] text-white'
              : 'bg-white text-gray-600 border border-gray-200 hover:border-red-300 hover:text-red-600'
          ]"
        >
          {{ cat.label }}
        </button>
      </div>

      <div v-if="productStore.loading" class="text-center py-20 text-gray-400">加载中...</div>

      <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <div
          v-for="product in productStore.products"
          :key="product.id"
          class="bg-white rounded-xl shadow-sm hover:shadow-md transition overflow-hidden cursor-pointer group"
          @click="router.push(`/products/${product.id}`)"
        >
          <div class="aspect-square overflow-hidden bg-gray-100">
            <img :src="product.template_image_url || `https://picsum.photos/seed/${product.id}/400/400`" :alt="product.name" class="w-full h-full object-cover group-hover:scale-105 transition duration-300" />
          </div>
          <div class="p-4">
            <div class="flex items-center justify-between mb-2">
              <h3 class="font-semibold text-gray-900 truncate">{{ product.name }}</h3>
              <span :class="['badge', categoryBadgeClass(product.category)]">{{ categoryLabel(product.category) }}</span>
            </div>
            <div class="flex items-center justify-between">
              <span class="text-[var(--color-primary)] font-bold text-lg">¥{{ product.price_base }}</span>
              <button @click.stop="router.push(`/order/new/${product.id}`)" class="btn-primary text-sm !px-4 !py-1.5">立即定制</button>
            </div>
          </div>
        </div>
      </div>

      <div v-if="!productStore.loading && productStore.products.length === 0" class="text-center py-20 text-gray-400">暂无作品</div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '@/stores/product'

const router = useRouter()
const productStore = useProductStore()
const activeCategory = ref('all')

const categories = [
  { key: 'all', label: '全部' },
  { key: 'wedding', label: '婚庆' },
  { key: 'enterprise', label: '企业' },
  { key: 'festival', label: '节庆' },
  { key: 'custom', label: '定制' },
]

function categoryLabel(cat: string) {
  const map: Record<string, string> = { wedding: '婚庆', enterprise: '企业', festival: '节庆', custom: '定制' }
  return map[cat] ?? cat
}

function categoryBadgeClass(cat: string) {
  const map: Record<string, string> = {
    wedding: 'bg-red-100 text-red-700',
    enterprise: 'bg-blue-100 text-blue-700',
    festival: 'bg-amber-100 text-amber-700',
    custom: 'bg-purple-100 text-purple-700',
  }
  return map[cat] ?? 'bg-gray-100 text-gray-700'
}

watch(activeCategory, (val) => {
  productStore.fetchProducts(val === 'all' ? undefined : val)
})

onMounted(() => {
  productStore.fetchProducts()
})
</script>
