import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'
import type { Product, ProductListItem } from '@/types'

export const useProductStore = defineStore('product', () => {
  const products = ref<ProductListItem[]>([])
  const currentProduct = ref<Product | null>(null)
  const loading = ref(false)

  async function fetchProducts(category?: string) {
    loading.value = true
    try {
      const params: Record<string, string> = {}
      if (category && category !== 'all') params.category = category
      const { data } = await api.get('/products', { params })
      products.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchProduct(id: number) {
    loading.value = true
    try {
      const { data } = await api.get(`/products/${id}`)
      currentProduct.value = data
    } finally {
      loading.value = false
    }
  }

  return { products, currentProduct, loading, fetchProducts, fetchProduct }
})
