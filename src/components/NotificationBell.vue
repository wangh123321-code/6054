<template>
  <div class="relative">
    <button @click="open = !open" class="relative p-2 rounded-full hover:bg-red-50 transition">
      <Bell class="w-5 h-5 text-gray-600" />
      <span v-if="notificationStore.unreadCount > 0" class="absolute -top-0.5 -right-0.5 bg-red-600 text-white text-xs rounded-full w-4 h-4 flex items-center justify-center">
        {{ notificationStore.unreadCount > 9 ? '9+' : notificationStore.unreadCount }}
      </span>
    </button>
    <div v-if="open" class="absolute right-0 top-full mt-2 w-80 bg-white rounded-lg shadow-xl border border-gray-100 z-50">
      <div class="p-3 border-b border-gray-100 flex items-center justify-between">
        <span class="font-semibold text-gray-800">通知</span>
        <button @click="open = false" class="text-gray-400 hover:text-gray-600 text-sm">关闭</button>
      </div>
      <div class="max-h-80 overflow-y-auto">
        <div
          v-for="n in notificationStore.notifications"
          :key="n.id"
          @click="handleClick(n)"
          :class="['p-3 border-b border-gray-50 cursor-pointer hover:bg-red-50 transition', !n.is_read ? 'bg-red-50/50' : '']"
        >
          <div class="flex items-start gap-2">
            <span v-if="!n.is_read" class="w-2 h-2 rounded-full bg-red-500 mt-1.5 shrink-0"></span>
            <div :class="n.is_read ? 'pl-4' : ''">
              <p class="text-sm font-medium text-gray-800">{{ n.title }}</p>
              <p v-if="n.content" class="text-xs text-gray-500 mt-0.5 line-clamp-2">{{ n.content }}</p>
              <p class="text-xs text-gray-400 mt-1">{{ formatTime(n.created_at) }}</p>
            </div>
          </div>
        </div>
        <div v-if="notificationStore.notifications.length === 0" class="p-6 text-center text-gray-400 text-sm">
          暂无通知
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { Bell } from 'lucide-vue-next'
import { useNotificationStore } from '@/stores/notification'
import type { Notification } from '@/types'

const notificationStore = useNotificationStore()
const open = ref(false)

function handleClick(n: Notification) {
  if (!n.is_read) notificationStore.markRead(n.id)
}

function formatTime(dateStr: string) {
  const d = new Date(dateStr)
  const now = new Date()
  const diff = now.getTime() - d.getTime()
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return d.toLocaleDateString('zh-CN')
}

function handleClickOutside(e: MouseEvent) {
  const el = (e.target as HTMLElement).closest('.relative')
  if (!el?.contains(e.target as Node)) open.value = false
}

onMounted(() => {
  notificationStore.fetchNotifications()
  notificationStore.fetchUnreadCount()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>
