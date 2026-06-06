<template>
  <nav class="bg-white shadow-sm sticky top-0 z-40">
    <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-center justify-between h-16">
        <div class="flex items-center gap-8">
          <router-link to="/" class="flex items-center gap-2 text-red-700 font-bold text-xl">
            <Scissors class="w-6 h-6" />
            <span>莆田剪纸</span>
          </router-link>
          <div class="hidden md:flex items-center gap-6">
            <router-link to="/" class="text-gray-700 hover:text-red-600 transition font-medium">首页</router-link>
            <router-link to="/orders" class="text-gray-700 hover:text-red-600 transition font-medium">我的订单</router-link>
            <router-link v-if="authStore.userRole === 'artisan' || authStore.userRole === 'admin'" to="/artisan/workspace" class="text-gray-700 hover:text-red-600 transition font-medium">匠人工作台</router-link>
            <router-link v-if="authStore.userRole === 'admin'" to="/admin" class="text-gray-700 hover:text-red-600 transition font-medium">管理</router-link>
          </div>
        </div>
        <div class="flex items-center gap-4">
          <NotificationBell v-if="authStore.isLoggedIn" />
          <template v-if="authStore.isLoggedIn">
            <div class="flex items-center gap-2 text-gray-700">
              <User class="w-5 h-5" />
              <span class="text-sm font-medium">{{ authStore.user?.username }}</span>
            </div>
            <button @click="authStore.logout()" class="text-sm text-gray-500 hover:text-red-600 transition">退出</button>
          </template>
          <template v-else>
            <router-link to="/login" class="px-4 py-2 text-sm text-red-700 border border-red-700 rounded-lg hover:bg-red-50 transition">登录</router-link>
            <router-link to="/register" class="px-4 py-2 text-sm text-white bg-red-700 rounded-lg hover:bg-red-800 transition">注册</router-link>
          </template>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup lang="ts">
import { Scissors, User } from 'lucide-vue-next'
import { useAuthStore } from '@/stores/auth'
import NotificationBell from '@/components/NotificationBell.vue'

const authStore = useAuthStore()
</script>
