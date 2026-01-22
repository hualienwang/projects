<template>
  <div id="app">
    <Navigation />
    <router-view />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Navigation from '@/components/Navigation.vue'

onMounted(() => {
  console.log('🚀 瓊林圖書進銷存系統 - 數據可視化前端已啟動')
})
</script>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

#app {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial,
    'Noto Sans', sans-serif, 'Apple Color Emoji', 'Segoe UI Emoji', 'Segoe UI Symbol',
    'Noto Color Emoji';
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

body {
  margin: 0;
  padding: 0;
}
</style>
