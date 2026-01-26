<script setup>
import { onMounted } from 'vue'

onMounted(() => {
  // 重定向到靜態診斷頁面
  window.location.href = '/diagnose-api.html'
})
</script>
