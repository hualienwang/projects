<template>
  <div class="test-chart">
    <h2>Chart.js 测试页面</h2>
    <div class="test-section">
      <h3>1. 基础图表测试（静态数据）</h3>
      <div class="chart-wrapper">
        <canvas ref="staticChartRef"></canvas>
      </div>
    </div>

    <div class="test-section">
      <h3>2. API 调用测试</h3>
      <button @click="testAPI" :disabled="loading">
        {{ loading ? '加载中...' : '测试 API' }}
      </button>
      <div v-if="apiResponse" class="response">
        <h4>API 响应:</h4>
        <pre>{{ JSON.stringify(apiResponse, null, 2) }}</pre>
      </div>
      <div v-if="apiError" class="error">
        <h4>API 错误:</h4>
        <p>{{ apiError }}</p>
      </div>
    </div>

    <div class="test-section">
      <h3>3. API 数据渲染测试</h3>
      <div class="chart-wrapper">
        <canvas ref="apiChartRef"></canvas>
      </div>
    </div>

    <div class="test-section">
      <h3>4. 调试信息</h3>
      <div class="debug-info">
        <p><strong>Chart.js 版本:</strong> {{ chartJsVersion }}</p>
        <p><strong>静态图表实例:</strong> {{ staticChartInstance ? '已创建' : '未创建' }}</p>
        <p><strong>API 图表实例:</strong> {{ apiChartInstance ? '已创建' : '未创建' }}</p>
        <p><strong>最后错误:</strong> {{ lastError || '无' }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import Chart from 'chart.js/auto'

const staticChartRef = ref(null)
const apiChartRef = ref(null)
const staticChartInstance = ref(null)
const apiChartInstance = ref(null)
const loading = ref(false)
const apiResponse = ref(null)
const apiError = ref(null)
const lastError = ref(null)
const chartJsVersion = ref('未知')

// 创建静态图表
const createStaticChart = () => {
  try {
    console.log('开始创建静态图表...')
    const ctx = staticChartRef.value.getContext('2d')

    const config = {
      type: 'line',
      data: {
        labels: ['一月', '二月', '三月', '四月', '五月', '六月'],
        datasets: [{
          label: '测试数据',
          data: [12, 19, 3, 5, 2, 3],
          borderColor: '#4CAF50',
          backgroundColor: 'rgba(76, 175, 80, 0.2)',
          fill: true,
          tension: 0.4
        }]
      },
      options: {
        responsive: true,
        plugins: {
          title: {
            display: true,
            text: 'Chart.js 静态图表测试'
          }
        }
      }
    }

    staticChartInstance.value = new Chart(ctx, config)
    console.log('静态图表创建成功!')
  } catch (err) {
    console.error('创建静态图表失败:', err)
    lastError.value = `创建静态图表失败: ${err.message}`
  }
}

// 测试 API 调用
const testAPI = async () => {
  loading.value = true
  apiResponse.value = null
  apiError.value = null

  try {
    console.log('开始测试 API 调用...')
    const response = await fetch('/api/dashboard/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: 'test_user',
        user_role: 'admin',
        chart_type: 'sales_trend'
      })
    })

    const data = await response.json()
    console.log('API 响应:', data)

    if (response.ok && data.success) {
      apiResponse.value = data
      renderAPIChart(data.chart_config)
    } else {
      apiError.value = data.message || 'API 返回错误'
      lastError.value = `API 错误: ${apiError.value}`
    }
  } catch (err) {
    console.error('API 调用失败:', err)
    apiError.value = err.message
    lastError.value = `API 调用失败: ${err.message}`
  } finally {
    loading.value = false
  }
}

// 渲染 API 数据图表
const renderAPIChart = (config) => {
  try {
    console.log('开始渲染 API 数据图表...')
    console.log('Chart config:', config)

    if (apiChartInstance.value) {
      apiChartInstance.value.destroy()
      apiChartInstance.value = null
    }

    const ctx = apiChartRef.value.getContext('2d')
    apiChartInstance.value = new Chart(ctx, config)
    console.log('API 数据图表渲染成功!')
  } catch (err) {
    console.error('渲染 API 数据图表失败:', err)
    lastError.value = `渲染 API 图表失败: ${err.message}`
  }
}

onMounted(() => {
  console.log('TestChart 组件已挂载')

  // 获取 Chart.js 版本
  chartJsVersion.value = Chart.version
  console.log('Chart.js 版本:', Chart.version)

  // 创建静态图表
  createStaticChart()
})

onBeforeUnmount(() => {
  if (staticChartInstance.value) {
    staticChartInstance.value.destroy()
  }
  if (apiChartInstance.value) {
    apiChartInstance.value.destroy()
  }
})
</script>

<style scoped>
.test-chart {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
}

h2 {
  color: #333;
  margin-bottom: 30px;
}

.test-section {
  background: white;
  padding: 20px;
  margin-bottom: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.test-section h3 {
  color: #666;
  margin-top: 0;
  margin-bottom: 15px;
}

.chart-wrapper {
  min-height: 400px;
  background: #f5f5f5;
  border-radius: 4px;
  padding: 20px;
}

button {
  padding: 10px 20px;
  background: #409eff;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

button:hover:not(:disabled) {
  background: #66b1ff;
}

button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.response, .error {
  margin-top: 20px;
  padding: 15px;
  border-radius: 4px;
  background: #f5f5f5;
}

.response h4, .error h4 {
  margin-top: 0;
  margin-bottom: 10px;
}

.error {
  background: #fef0f0;
  color: #f56c6c;
}

pre {
  overflow-x: auto;
  font-size: 12px;
}

.debug-info {
  background: #f0f9ff;
  padding: 15px;
  border-radius: 4px;
  border-left: 4px solid #409eff;
}

.debug-info p {
  margin: 8px 0;
}

.debug-info strong {
  color: #333;
}
</style>
