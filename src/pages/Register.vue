<template>
  <div class="min-h-[80vh] flex items-center justify-center px-4">
    <div class="w-full max-w-md">
      <div class="text-center mb-8">
        <h1 class="text-3xl font-bold text-[var(--color-primary)]">莆田剪纸</h1>
        <p class="text-gray-500 mt-2">创建新账户</p>
      </div>
      <form @submit.prevent="handleRegister" class="bg-white rounded-xl p-8 shadow-sm space-y-5">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">用户名</label>
          <input v-model="form.username" type="text" required class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">邮箱</label>
          <input v-model="form.email" type="email" required class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">密码</label>
          <input v-model="form.password" type="password" required class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">手机号</label>
          <input v-model="form.phone" type="tel" class="w-full border border-gray-300 rounded-lg px-4 py-2.5 focus:ring-2 focus:ring-red-500 focus:border-red-500 outline-none transition" />
        </div>
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-2">角色</label>
          <div class="flex gap-4">
            <label :class="['flex-1 text-center py-2.5 rounded-lg border-2 cursor-pointer transition font-medium', form.role === 'customer' ? 'border-[var(--color-primary)] text-[var(--color-primary)] bg-red-50' : 'border-gray-200 text-gray-600 hover:border-gray-300']">
              <input type="radio" v-model="form.role" value="customer" class="sr-only" />客户
            </label>
            <label :class="['flex-1 text-center py-2.5 rounded-lg border-2 cursor-pointer transition font-medium', form.role === 'artisan' ? 'border-[var(--color-primary)] text-[var(--color-primary)] bg-red-50' : 'border-gray-200 text-gray-600 hover:border-gray-300']">
              <input type="radio" v-model="form.role" value="artisan" class="sr-only" />匠人
            </label>
          </div>
        </div>
        <p v-if="error" class="text-sm text-red-600">{{ error }}</p>
        <button type="submit" :disabled="submitting" class="btn-primary w-full text-center disabled:opacity-50">
          {{ submitting ? '注册中...' : '注册' }}
        </button>
        <p class="text-center text-sm text-gray-500">
          已有账号？<router-link to="/login" class="text-[var(--color-primary)] hover:underline">去登录</router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const error = ref('')
const submitting = ref(false)
const form = reactive({
  username: '',
  email: '',
  password: '',
  phone: '',
  role: 'customer',
})

async function handleRegister() {
  error.value = ''
  submitting.value = true
  try {
    await authStore.register({
      username: form.username,
      email: form.email,
      password: form.password,
      phone: form.phone || undefined,
      role: form.role,
    })
    router.push('/')
  } catch {
    error.value = '注册失败，请重试'
  } finally {
    submitting.value = false
  }
}
</script>
