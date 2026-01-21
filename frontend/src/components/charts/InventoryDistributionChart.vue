<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3>庫存狀態分佈</h3>
      <div class="refresh-btn" @click="loadData">
        <span>🔄 刷新</span>
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
      <div class="chart-wrapper">
        <canvas ref="chartRef"></canvas>
      </div>
      <div v-if="inventoryData" class="inventory-summary">
        <div class="summary-item normal">
          <span class="label">正常庫存</span>
          <span class="value">{{ inventoryData.normal }}</span>
        </div>
        <div class="summary-item warning">
          <span class="label">低庫存預警</span>
          <span class="value">{{ inventoryData.low }}</span>
        </div>
        <div class="summary-item danger">
          <span class="label">缺貨</span>
          <span class="value">{{ inventoryData.out }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, computed } from 'vue'
import Chart from 'chart.js/auto'
import { useUserStore } from '@/stores/user'
import { getInventoryDistribution } from '@/api/dashboard'

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
const chartData = ref(null)

// 库存摘要数据
const inventoryData = computed(() => {
  if (!chartData.value || !chartData.value.labels || !chartData.value.datasets) {
    return null
  }
  
  const labels = chartData.value.labels
  const data = chartData.value.datasets[0].data
  
  return {
    normal: data[labels.indexOf('正常庫存')] || 0,
    low: data[labels.indexOf('低庫存預警')] || 0,
    out: data[labels.indexOf('缺貨')] || 0
  }
})

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
    const response = await getInventoryDistribution({
      user_id: userStore.userId,
      user_role: userStore.userRole
    })
    
    if (response.success && response.has_permission) {
      chartData.value = response.chart_data
      renderChart(response.chart_config)
      emit('data-loaded', response.chart_data)
    } else {
      error.value = response.message || '權限不足或數據加載失敗'
      emit('error', error.value)
    }
  } catch (err) {
    console.error('加载库存分布数据失败:', err)
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
  
  // 更新图表配置
  if (config.options && config.options.plugins) {
    config.options.plugins.title = {
      display: true,
      text: '庫存狀態分佈',
      font: {
        size: 16,
        weight: 'bold'
      }
    }
    
    config.options.plugins.legend = {
      position: 'bottom',
      labels: {
        padding: 20,
        font: {
          size: 14
        }
      }
    }
  }
  
  config.options.responsive = true
  config.options.maintainAspectRatio = true
  
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

.refresh-btn {
  padding: 8px 16px;
  background: #67c23a;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: background 0.3s;
}

.refresh-btn:hover {
  background: #85ce61;
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
  display: flex;
  flex-direction: column;
  align-items: center;
}

.chart-wrapper {
  width: 100%;
  max-width: 500px;
  margin: 0 auto;
}

.inventory-summary {
  display: flex;
  justify-content: space-around;
  width: 100%;
  max-width: 600px;
  margin-top: 30px;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.summary-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 10px 20px;
  border-radius: 8px;
  background: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.summary-item .label {
  font-size: 14px;
  color: #666;
  margin-bottom: 8px;
}

.summary-item .value {
  font-size: 24px;
  font-weight: bold;
}

.summary-item.normal .value {
  color: #67c23a;
}

.summary-item.warning .value {
  color: #e6a23c;
}

.summary-item.danger .value {
  color: #f56c6c;
}

@media (max-width: 768px) {
  .inventory-summary {
    flex-direction: column;
    gap: 10px;
  }
}
</style>
