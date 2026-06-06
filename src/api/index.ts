import axios from 'axios'
import router from '@/router'
import type { Order, Review, ReviewCreate } from '@/types'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem('token')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

export const orderApi = {
  confirmReceipt: (orderId: number) =>
    api.post<Order>(`/orders/${orderId}/confirm-receipt`),

  submitReview: (orderId: number, data: ReviewCreate) =>
    api.post<Review>(`/orders/${orderId}/review`, data),

  getOrderReview: (orderId: number) =>
    api.get<Review | null>(`/orders/${orderId}/review`),
}

export const productApi = {
  getReviews: (productId: number, limit: number = 10) =>
    api.get<Review[]>(`/products/${productId}/reviews?limit=${limit}`),
}

export const artisanApi = {
  getDetail: (artisanId: number) =>
    api.get(`/artisans/${artisanId}`),

  getReviews: (artisanId: number, limit: number = 20) =>
    api.get<Review[]>(`/artisans/${artisanId}/reviews?limit=${limit}`),
}

export default api
