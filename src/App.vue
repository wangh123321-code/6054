<template>
  <NavBar />
  <main class="min-h-screen">
    <router-view />
  </main>
</template>

<script setup lang="ts">
import NavBar from '@/components/NavBar.vue'
</script>
