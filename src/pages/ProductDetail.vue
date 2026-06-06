<template>
  <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
    <div v-if="productStore.loading" class="text-center py-20 text-gray-400">加载中...</div>

    <div v-else-if="product" class="grid grid-cols-1 lg:grid-cols-2 gap-10">
      <div class="space-y-4">
        <div class="aspect-square rounded-xl overflow-hidden bg-gray-100">
          <img :src="currentImage" :alt="product.name" class="w-full h-full object-cover" />
        </div>
        <div v-if="product.images.length > 1" class="flex gap-3 overflow-x-auto pb-2">
          <img
            v-for="img in product.images"
            :key="img.id"
            :src="img.image_url"
            :alt="product.name"
            @click="selectedImage = img.image_url"
            :class="['w-20 h-20 rounded-lg object-cover cursor-pointer border-2 transition', selectedImage === img.image_url ? 'border-[var(--color-primary)]' : 'border-transparent hover:border-gray-300']"
          />
        </div>
      </div>

      <div>
        <div class="flex items-center gap-3 mb-4">
          <h1 class="text-2xl font-bold text-gray-900">{{ product.name }}</h1>
          <span :class="['badge', categoryBadgeClass(product.category)]">{{ categoryLabel(product.category) }}</span>
        </div>
        <p class="text-3xl font-bold text-[var(--color-primary)] mb-6">¥{{ product.price_base }}</p>
        <p v-if="product.description" class="text-gray-600 leading-relaxed mb-6">{{ product.description }}</p>
        <div class="flex items-center gap-2 mb-8">
          <span :class="['w-2 h-2 rounded-full', product.stock > 0 ? 'bg-green-500' : 'bg-red-500']"></span>
          <span class="text-sm" :class="product.stock > 0 ? 'text-green-600' : 'text-red-600'">
            {{ product.stock > 0 ? `有货 (库存${product.stock})` : '暂时缺货' }}
          </span>
        </div>
        <button
          @click="router.push(`/order/new/${product.id}`)"
          :disabled="product.stock <= 0"
          class="btn-primary w-full text-center disabled:opacity-50 disabled:cursor-not-allowed"
        >
          立即定制
        </button>
      </div>
    </div>

    <div v-else class="text-center py-20 text-gray-400">作品不存在</div>

    <section class="mt-16">
      <h2 class="text-xl font-bold text-gray-900 mb-6">更多作品推荐</h2>
      <div class="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-4">
        <div
          v-for="p in recommendedProducts"
          :key="p.id"
          @click="navigateToProduct(p.id)"
          class="bg-white rounded-lg shadow-sm overflow-hidden cursor-pointer hover:shadow-md transition"
        >
          <div class="aspect-square overflow-hidden bg-gray-100">
            <img :src="p.template_image_url || `https://picsum.photos/seed/${p.id}/300/300`" :alt="p.name" class="w-full h-full object-cover" />
          </div>
          <div class="p-3">
            <h3 class="text-sm font-medium text-gray-900 truncate">{{ p.name }}</h3>
            <p class="text-[var(--color-primary)] font-bold text-sm mt-1">¥{{ p.price_base }}</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useProductStore } from '@/stores/product'

const route = useRoute()
const router = useRouter()
const productStore = useProductStore()
const selectedImage = ref<string | null>(null)

const product = computed(() => productStore.currentProduct)
const currentImage = computed(() => selectedImage.value || product.value?.images?.[0]?.image_url || product.value?.template_image_url || `https://picsum.photos/seed/${route.params.id}/600/600`)
const recommendedProducts = computed(() => productStore.products.filter((p) => p.id !== Number(route.params.id)).slice(0, 4))

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

function navigateToProduct(id: number) {
  router.push(`/products/${id}`)
}

async function loadProduct() {
  const id = Number(route.params.id)
  if (id) {
    selectedImage.value = null
    await productStore.fetchProduct(id)
  }
}

onMounted(() => {
  loadProduct()
  if (productStore.products.length === 0) productStore.fetchProducts()
})

watch(() => route.params.id, loadProduct)
</script>
