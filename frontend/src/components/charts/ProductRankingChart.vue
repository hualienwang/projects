<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3>商品銷售排行</h3>
      <div class="controls">
        <select v-model="days" @change="loadData">
          <option :value="7">最近 7 天</option>
          <option :value="30">最近 30 天</option>
          <option :value="90">最近 90 天</option>
        </select>
        <select v-model="topN" @change="loadData">
          <option :value="5">Top 5</option>
          <option :value="10">Top 10</option>
          <option :value="20">Top 20</option>
        </select>
      </div>
    </div>
    
    <div v-if="loading" class="loading">
      <div class="spinner"></div>
      <p>載入中...</p>
    </div>
    
    <div v-else-if="error" class="error">
      <p>{{ error }}</p>
      <button @click="loadData" class="retry-btn">重試</button>
    </div>
    
    <div v-else class="chart-content">
      <canvas ref="chartRef"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch } from 'vue'
import Chart from 'chart.js/auto'
import { useUserStore } from '@/stores/user'
import { getProductRanking } from '@/api/dashboard'

const props = defineProps({
  autoLoad: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['data-loaded', 'error'])

const userStore = useUserStore()
const chartRef = ref(null)
const chartInstance = ref(null)
const loading = ref(false)
const error = ref('')
const days = ref(30)
const topN = ref(10)

/**
 * 加载数据
 */
const loadData = async () => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
    chartInstance.value = null
  }
  
  loading.value = true
  error.value = ''
  
  try {
    const response = await getProductRanking({
      user_id: userStore.userId,
      user_role: userStore.userRole,
      days: days.value,
      top_n: topN.value
    })
    
    if (response.success && response.has_permission) {
      renderChart(response.chart_config)
      emit('data-loaded', response.chart_data)
    } else {
      error.value = response.message || '權限不足或數據加載失敗'
      emit('error', error.value)
    }
  } catch (err) {
    console.error('加载商品排行数据失败:', err)
    error.value = '網絡錯誤，請稍後重試'
    emit('error', error.value)
  } finally {
    loading.value = false
  }
}

/**
 * 渲染图表
 */
const renderChart = (config) => {
  if (!chartRef.value) return
  
  const ctx = chartRef.value.getContext('2d')
  
  // 更新图表标题
  if (config.options && config.options.plugins) {
    config.options.plugins.title = {
      display: true,
      text: `商品銷售排行 Top ${topN.value} - 最近 ${days.value} 天`,
      font: {
        size: 16,
        weight: 'bold'
      }
    }
  }
  
  chartInstance.value = new Chart(ctx, config)
}

/**
 * 监听用户角色变化
 */
watch(() => userStore.userRole, () => {
  if (props.autoLoad) {
    loadData()
  }
})

onMounted(() => {
  if (props.autoLoad) {
    loadData()
  }
})

onBeforeUnmount(() => {
  if (chartInstance.value) {
    chartInstance.value.destroy()
  }
})

defineExpose({
  loadData
})
</script>

<style scoped>
.chart-container {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  color: #333;
  font-size: 18px;
}

.controls {
  display: flex;
  gap: 10px;
}

.controls select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 14px;
  cursor: pointer;
}

.controls select:hover {
  border-color: #409eff;
}

.loading, .error {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 300px;
  color: #666;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid #f3f3f3;
  border-top: 3px solid #409eff;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 10px;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.retry-btn {
  margin-top: 10px;
  padding: 8px 16px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.retry-btn:hover {
  background: #66b1ff;
}

.chart-content {
  position: relative;
  min-height: 400px;
}
</style>
