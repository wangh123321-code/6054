import { defineStore } from 'pinia'
import { ref } from 'vue'
import api, { orderApi } from '@/api'
import type { Order, ProgressPhoto, Review, ReviewCreate } from '@/types'

export const useOrderStore = defineStore('order', () => {
  const orders = ref<Order[]>([])
  const currentOrder = ref<Order | null>(null)
  const currentReview = ref<Review | null>(null)
  const loading = ref(false)

  async function placeOrder(data: {
    product_id: number
    total_price: number
    custom_size: string
    custom_color: string
    custom_message?: string
    reference_image_url?: string
    is_original: boolean
  }) {
    const { data: order } = await api.post('/orders', data)
    currentOrder.value = order
    return order
  }

  async function fetchOrders() {
    loading.value = true
    try {
      const { data } = await api.get('/orders')
      orders.value = data
    } finally {
      loading.value = false
    }
  }

  async function fetchOrder(id: number) {
    loading.value = true
    try {
      const { data } = await api.get(`/orders/${id}`)
      currentOrder.value = data
    } finally {
      loading.value = false
    }
  }

  async function updateStatus(orderId: number, status: string) {
    const { data } = await api.put(`/orders/${orderId}/status`, { status })
    if (currentOrder.value?.id === orderId) currentOrder.value = data
  }

  async function assignArtisan(orderId: number, payload: { artisan_id: number; deadline?: string }) {
    const { data } = await api.post(`/orders/${orderId}/assign`, payload)
    if (currentOrder.value?.id === orderId) currentOrder.value = data
  }

  async function uploadProgressPhoto(orderId: number, payload: { image_url: string; description?: string }) {
    const { data } = await api.post(`/orders/${orderId}/progress-photo`, payload)
    return data
  }

  async function fetchProgressPhotos(orderId: number) {
    const { data } = await api.get(`/orders/${orderId}/progress-photos`)
    return data as ProgressPhoto[]
  }

  async function confirmReceipt(orderId: number) {
    const { data } = await orderApi.confirmReceipt(orderId)
    if (currentOrder.value?.id === orderId) currentOrder.value = data
    const idx = orders.value.findIndex((o) => o.id === orderId)
    if (idx !== -1) orders.value[idx] = data
    return data
  }

  async function submitReview(orderId: number, reviewData: ReviewCreate) {
    const { data } = await orderApi.submitReview(orderId, reviewData)
    currentReview.value = data
    await fetchOrder(orderId)
    return data
  }

  async function fetchOrderReview(orderId: number) {
    const { data } = await orderApi.getOrderReview(orderId)
    currentReview.value = data
    return data
  }

  return {
    orders,
    currentOrder,
    currentReview,
    loading,
    placeOrder,
    fetchOrders,
    fetchOrder,
    updateStatus,
    assignArtisan,
    uploadProgressPhoto,
    fetchProgressPhotos,
    confirmReceipt,
    submitReview,
    fetchOrderReview,
  }
})
