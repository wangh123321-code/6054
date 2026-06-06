import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import api from '@/api'
import type { Notification } from '@/types'

export const useNotificationStore = defineStore('notification', () => {
  const notifications = ref<Notification[]>([])
  const unreadCount = ref(0)

  async function fetchNotifications() {
    const { data } = await api.get('/notifications')
    notifications.value = data
  }

  async function markRead(id: number) {
    await api.patch(`/notifications/${id}/read`)
    const n = notifications.value.find((item) => item.id === id)
    if (n) n.is_read = true
    unreadCount.value = Math.max(0, unreadCount.value - 1)
  }

  async function fetchUnreadCount() {
    const { data } = await api.get('/notifications/unread-count')
    unreadCount.value = data.count
  }

  return { notifications, unreadCount, fetchNotifications, markRead, fetchUnreadCount }
})
