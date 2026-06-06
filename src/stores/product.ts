import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api, { productApi } from '@/api'
import type { Product, ProductListItem, Review } from '@/types'

export const useProductStore = defineStore('product', () => {
  const products = ref<ProductListItem[]>([])
  const currentProduct = ref<Product | null>(null)
  const currentProductReviews = ref<Review[]>([])
  const loading = ref(false)
  const reviewsLoading = ref(false)

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

  async function fetchProductReviews(productId: number, limit: number = 10) {
    reviewsLoading.value = true
    try {
      const { data } = await productApi.getReviews(productId, limit)
      currentProductReviews.value = data
    } finally {
      reviewsLoading.value = false
    }
  }

  return {
    products,
    currentProduct,
    currentProductReviews,
    loading,
    reviewsLoading,
    fetchProducts,
    fetchProduct,
    fetchProductReviews,
  }
})
