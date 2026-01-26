<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3>供應商採購統計</h3>
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
      <canvas ref="chartRef"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { useUserStore } from '@/stores/user'
import { generateChart } from '@/api/dashboard'

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
    const response = await generateChart({
      user_id: userStore.userId,
      user_role: userStore.userRole,
      chart_type: 'supplier_stats'
    })

    if (response.success && response.has_permission) {
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
    console.error('加载供应商统计数据失败:', err)
    error.value = '網絡錯誤，請稍後重試'
    loading.value = false
    emit('error', error.value)
  }
}

/**
 * 渲染图表
 */
const renderChart = async (config) => {
  console.log('[SupplierStatsChart] 开始渲染图表...')

  // 重試機制：等待 Canvas 元素渲染
  let retryCount = 0
  const maxRetries = 5

  while (retryCount < maxRetries) {
    if (chartRef.value) {
      console.log('[SupplierStatsChart] Canvas 元素已找到！')
      break
    }

    console.warn('[SupplierStatsChart] Canvas 元素不存在，等待 DOM 更新...')
    await nextTick()
    retryCount++
  }

  if (!chartRef.value) {
    console.error('[SupplierStatsChart] Canvas 元素不存在！')
    return
  }

  const ctx = chartRef.value.getContext('2d')

  // 深拷贝配置，避免修改原始数据
  const chartConfig = JSON.parse(JSON.stringify(config))

  // 更新图表配置
  if (chartConfig.options && chartConfig.options.plugins) {
    chartConfig.options.plugins.title = {
      display: true,
      text: '供應商採購統計',
      font: {
        size: 16,
        weight: 'bold'
      }
    }

    chartConfig.options.plugins.tooltip = {
      mode: 'index',
      intersect: false,
      callbacks: {
        label: function(context) {
          let label = context.dataset.label || ''
          if (label) {
            label += ': '
          }

          if (context.dataset.type === 'line') {
            label += context.parsed.y + ' 元'
          } else {
            label += context.parsed.y + ' 個商品'
          }

          return label
        }
      }
    }
  }

  chartConfig.options.responsive = true
  chartConfig.options.maintainAspectRatio = false

  console.log('[SupplierStatsChart] Chart 配置:', chartConfig.type)

  chartInstance.value = new Chart(ctx, chartConfig)
  console.log('[SupplierStatsChart] 图表创建成功！')
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
  position: relative;
  min-height: 500px;
}
</style>
