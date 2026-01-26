<template>
  <div class="chart-container">
    <div class="chart-header">
      <h3>銷售趨勢分析</h3>
      <div class="date-selector">
        <select v-model="days" @change="loadData">
          <option :value="7">最近 7 天</option>
          <option :value="30">最近 30 天</option>
          <option :value="90">最近 90 天</option>
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

    <div v-else class="chart-content" ref="chartContentRef">
      <canvas ref="chartRef"></canvas>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount, watch, nextTick } from 'vue'
import Chart from 'chart.js/auto'
import { useUserStore } from '@/stores/user'
import { getSalesTrend } from '@/api/dashboard'

const props = defineProps({
  autoLoad: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['data-loaded', 'error'])

const userStore = useUserStore()
const chartRef = ref(null)
const chartContentRef = ref(null)
const chartInstance = ref(null)
const loading = ref(false)
const error = ref('')
const days = ref(30)

console.log('[SalesTrendChart] 组件已创建')

/**
 * 加载数据
 */
const loadData = async () => {
  console.log('[SalesTrendChart] 开始加载数据...')

  // 销毁现有图表
  if (chartInstance.value) {
    console.log('[SalesTrendChart] 销毁现有图表')
    chartInstance.value.destroy()
    chartInstance.value = null
  }

  loading.value = true
  error.value = ''

  try {
    const response = await getSalesTrend({
      user_id: userStore.userId,
      user_role: userStore.userRole,
      days: days.value
    })

    console.log('[SalesTrendChart] API 响应:', response)

    if (response.success && response.has_permission) {
      // 先設置 loading = false，讓 Canvas 元素渲染
      loading.value = false

      // 等待 DOM 更新，確保 Canvas 元素已經渲染
      await nextTick()
      await nextTick()  // 雙重 nextTick 確保 DOM 完全穩定

      await renderChart(response.chart_config)
      emit('data-loaded', response.chart_data)
    } else {
      error.value = response.message || '權限不足或數據加載失敗'
      console.error('[SalesTrendChart]', error.value)
      emit('error', error.value)
      loading.value = false
    }
  } catch (err) {
    console.error('[SalesTrendChart] 加载销售趋势数据失败:', err)
    console.error('[SalesTrendChart] 错误名称:', err.name)
    console.error('[SalesTrendChart] 错误消息:', err.message)
    console.error('[SalesTrendChart] 错误堆栈:', err.stack)

    // 生成详细的错误信息
    let errorMessage = '加载失败'

    if (err.response) {
      // 服务器返回了错误响应
      errorMessage = `服务器错误: ${err.response.status} - ${err.response.statusText}`
      console.error('[SalesTrendChart] 服务器响应:', err.response.data)
    } else if (err.request) {
      // 请求已发出但无响应
      errorMessage = '网络错误: 无法连接到服务器'
      console.error('[SalesTrendChart] 请求配置:', err.config)
    } else {
      // 其他错误
      errorMessage = `错误: ${err.message}`
    }

    error.value = errorMessage
    loading.value = false
    emit('error', errorMessage)
  }
}

/**
 * 渲染图表
 */
const renderChart = async (config) => {
  console.log('[SalesTrendChart] 开始渲染图表...')

  // 重試機制：等待 Canvas 元素渲染
  let retryCount = 0
  const maxRetries = 5

  while (retryCount < maxRetries) {
    console.log(`[SalesTrendChart] 嘗試獲取 Canvas 元素 (嘗試 ${retryCount + 1}/${maxRetries})`)

    // 检查 canvas 是否存在
    if (chartRef.value) {
      console.log('[SalesTrendChart] Canvas 元素已找到！')
      break
    }

    console.warn('[SalesTrendChart] Canvas 元素不存在，等待 DOM 更新...')
    await nextTick()
    retryCount++
  }

  // 最終檢查
  if (!chartRef.value) {
    console.error('[SalesTrendChart] Canvas 元素仍然不存在！')
    throw new Error('Canvas 元素不存在')
  }

  // 检查容器尺寸
  if (chartContentRef.value) {
    const rect = chartContentRef.value.getBoundingClientRect()
    console.log('[SalesTrendChart] 容器尺寸:', {
      width: rect.width,
      height: rect.height,
      display: window.getComputedStyle(chartContentRef.value).display
    })

    if (rect.width === 0 || rect.height === 0) {
      console.warn('[SalesTrendChart] 容器尺寸为 0，等待渲染...')
      await nextTick()
      await nextTick()
    }
  }

  const ctx = chartRef.value.getContext('2d')
  console.log('[SalesTrendChart] Canvas 上下文获取成功')

  // 深拷贝配置，避免修改原始数据
  const chartConfig = JSON.parse(JSON.stringify(config))

  // 更新图表标题
  if (chartConfig.options && chartConfig.options.plugins) {
    chartConfig.options.plugins.title = {
      display: true,
      text: `銷售趨勢 - 最近 ${days.value} 天`,
      font: {
        size: 16,
        weight: 'bold'
      }
    }
  }

  console.log('[SalesTrendChart] Chart 配置:', chartConfig.type)

  chartInstance.value = new Chart(ctx, chartConfig)
  console.log('[SalesTrendChart] 图表创建成功！')
}

/**
 * 监听用户角色变化
 */
watch(() => userStore.userRole, () => {
  console.log('[SalesTrendChart] 用户角色变化:', userStore.userRole)
  if (props.autoLoad) {
    loadData()
  }
})

onMounted(async () => {
  console.log('[SalesTrendChart] 组件已挂载')

  if (props.autoLoad) {
    // 等待 DOM 完全渲染後再加載數據
    await nextTick()
    await nextTick()
    loadData()
  }
})

onBeforeUnmount(() => {
  console.log('[SalesTrendChart] 组件即将卸载')
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

.date-selector select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 14px;
  cursor: pointer;
}

.date-selector select:hover {
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
  width: 100%;
  height: 400px;
  min-height: 400px;
}

.chart-content canvas {
  width: 100% !important;
  height: 100% !important;
}
</style>
