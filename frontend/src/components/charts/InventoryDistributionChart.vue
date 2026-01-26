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
import { ref, onMounted, onBeforeUnmount, watch, computed, nextTick } from 'vue'
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
  if (!chartData.value) {
    return null
  }

  // 优先使用 API 返回的结构化数据
  if (chartData.value.low_stock !== undefined) {
    return {
      normal: (chartData.value.total_products || 0) - (chartData.value.low_stock || 0) - (chartData.value.out_of_stock || 0) - (chartData.value.overstock || 0),
      low: chartData.value.low_stock || 0,
      out: chartData.value.out_of_stock || 0
    }
  }

  // 兼容图表数据结构
  if (!chartData.value.labels || !chartData.value.datasets) {
    return null
  }

  const labels = chartData.value.labels
  const data = chartData.value.datasets[0].data

  // 支持多种标签名称
  const getLabelIndex = (keywords) => {
    for (let i = 0; i < labels.length; i++) {
      for (const keyword of keywords) {
        if (labels[i].includes(keyword)) {
          return i
        }
      }
    }
    return -1
  }

  const normalIndex = getLabelIndex(['正常', 'normal'])
  const lowIndex = getLabelIndex(['低庫存', '預警', 'low', 'warning'])
  const outIndex = getLabelIndex(['庫存不足', '缺貨', 'out', 'danger'])

  return {
    normal: normalIndex >= 0 ? (data[normalIndex] || 0) : 0,
    low: lowIndex >= 0 ? (data[lowIndex] || 0) : 0,
    out: outIndex >= 0 ? (data[outIndex] || 0) : 0
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
      loading.value = false

      // 等待 DOM 更新，確保 Canvas 元素已經渲染
      await nextTick()
      await nextTick()

      renderChart(response.chart_config)
      emit('data-loaded', response.chart_data)
    } else {
      error.value = response.message || '權限不足或數據加載失敗'
      emit('error', error.value)
      loading.value = false
    }
  } catch (err) {
    console.error('加载库存分布数据失败:', err)
    error.value = '網絡錯誤，請稍後重試'
    loading.value = false
    emit('error', error.value)
  }
}

/**
 * 渲染图表
 */
const renderChart = async (config) => {
  console.log('[InventoryDistributionChart] 开始渲染图表...')

  // 重試機制：等待 Canvas 元素渲染
  let retryCount = 0
  const maxRetries = 5

  while (retryCount < maxRetries) {
    if (chartRef.value) {
      console.log('[InventoryDistributionChart] Canvas 元素已找到！')
      break
    }

    console.warn('[InventoryDistributionChart] Canvas 元素不存在，等待 DOM 更新...')
    await nextTick()
    retryCount++
  }

  if (!chartRef.value) {
    console.error('[InventoryDistributionChart] Canvas 元素不存在！')
    return
  }

  const ctx = chartRef.value.getContext('2d')

  // 深拷贝配置，避免修改原始数据
  const chartConfig = JSON.parse(JSON.stringify(config))

  // 更新图表配置
  if (chartConfig.options && chartConfig.options.plugins) {
    chartConfig.options.plugins.title = {
      display: true,
      text: '庫存狀態分佈',
      font: {
        size: 16,
        weight: 'bold'
      }
    }

    chartConfig.options.plugins.legend = {
      position: 'bottom',
      labels: {
        padding: 20,
        font: {
          size: 14
        }
      }
    }
  }

  chartConfig.options.responsive = true
  chartConfig.options.maintainAspectRatio = true

  console.log('[InventoryDistributionChart] Chart 配置:', chartConfig.type)

  chartInstance.value = new Chart(ctx, chartConfig)
  console.log('[InventoryDistributionChart] 图表创建成功！')
}

/**
 * 监听用户角色变化
 */
watch(() => userStore.userRole, () => {
  if (props.autoLoad) {
    loadData()
  }
})

onMounted(async () => {
  if (props.autoLoad) {
    await nextTick()
    await nextTick()
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
