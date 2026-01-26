<template>
  <div class="test-dashboard-api">
    <h1>🔍 Dashboard API 調用測試</h1>

    <div class="test-panel">
      <h2>測試 1: 使用 axios 調用（Dashboard 方式）</h2>
      <button @click="testAxios" :disabled="loading1">
        {{ loading1 ? '測試中...' : '使用 axios 測試' }}
      </button>
      <div v-if="result1" class="result" :class="{ success: success1, error: !success1 }">
        <pre>{{ result1 }}</pre>
      </div>
    </div>

    <div class="test-panel">
      <h2>測試 2: 使用 fetch 調用（TestChart 方式）</h2>
      <button @click="testFetch" :disabled="loading2">
        {{ loading2 ? '測試中...' : '使用 fetch 測試' }}
      </button>
      <div v-if="result2" class="result" :class="{ success: success2, error: !success2 }">
        <pre>{{ result2 }}</pre>
      </div>
    </div>

    <div class="test-panel">
      <h2>測試 3: 完整的 getSalesTrend 調用</h2>
      <button @click="testGetSalesTrend" :disabled="loading3">
        {{ loading3 ? '測試中...' : '測試 getSalesTrend' }}
      </button>
      <div v-if="result3" class="result" :class="{ success: success3, error: !success3 }">
        <pre>{{ result3 }}</pre>
      </div>
    </div>

    <div class="test-panel">
      <h2>調試信息</h2>
      <table>
        <tbody>
          <tr>
            <td>axios 實例 baseURL:</td>
            <td>/api</td>
          </tr>
          <tr>
            <td>後端 API 地址:</td>
            <td>http://localhost:5000/api/dashboard/generate</td>
          </tr>
          <tr>
            <td>代理配置:</td>
            <td>/api → http://localhost:5000</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'
import { getSalesTrend } from '@/api/dashboard'

const loading1 = ref(false)
const loading2 = ref(false)
const loading3 = ref(false)
const result1 = ref(null)
const result2 = ref(null)
const result3 = ref(null)
const success1 = ref(false)
const success2 = ref(false)
const success3 = ref(false)

// 測試 1: 使用 axios 調用（完全模擬 dashboard.js 的方式）
const testAxios = async () => {
  loading1.value = true
  result1.value = '開始測試...'

  try {
    console.log('🚀 測試 1: 使用 axios 調用')

    // 創建 axios 實例（與 dashboard.js 相同）
    const api = axios.create({
      baseURL: '/api',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    const response = await api.post('/dashboard/generate', {
      user_id: 'test_user',
      user_role: 'viewer',
      chart_type: 'sales_trend'
    })

    console.log('✅ axios 響應:', response)
    console.log('📊 響應數據:', response.data)

    result1.value = `✅ axios 測試成功！

HTTP 狀態: ${response.status}
狀態文本: ${response.statusText}

響應數據:
${JSON.stringify(response.data, null, 2)}
`
    success1.value = true
  } catch (err) {
    console.error('❌ axios 測試失敗:', err)
    console.error('❌ 錯誤名稱:', err.name)
    console.error('❌ 錯誤消息:', err.message)

    let errorDetails = `❌ axios 測試失敗！

錯誤名稱: ${err.name}
錯誤消息: ${err.message}
`

    if (err.response) {
      errorDetails += `
服務器響應:
- 狀態碼: ${err.response.status}
- 狀態文本: ${err.response.statusText}
- 響應數據: ${JSON.stringify(err.response.data, null, 2)}
`
      console.error('❌ 服務器響應:', err.response.data)
    } else if (err.request) {
      errorDetails += `
請求詳情:
- 請求已發出，但沒有收到響應
- 請求 URL: ${err.config?.url || '未知'}
- 請求方法: ${err.config?.method || '未知'}
`
      console.error('❌ 請求配置:', err.config)
    } else {
      errorDetails += `\n設置錯誤:\n${err.stack}`
    }

    result1.value = errorDetails
    success1.value = false
  } finally {
    loading1.value = false
  }
}

// 測試 2: 使用 fetch 調用（與 TestChart 相同）
const testFetch = async () => {
  loading2.value = true
  result2.value = '開始測試...'

  try {
    console.log('🚀 測試 2: 使用 fetch 調用')

    const response = await fetch('/api/dashboard/generate', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        user_id: 'test_user',
        user_role: 'viewer',
        chart_type: 'sales_trend'
      })
    })

    console.log('📥 fetch 響應狀態:', response.status, response.statusText)

    // 檢查響應是否為空
    const responseText = await response.text()
    console.log('📄 響應文本長度:', responseText.length)
    console.log('📄 響應文本（前200字符）:', responseText.substring(0, 200))

    // 檢查響應是否為空
    if (!responseText.trim()) {
      throw new Error('服務器返回空響應')
    }

    // 解析 JSON
    let data
    try {
      data = JSON.parse(responseText)
      console.log('✅ fetch JSON 解析成功:', data)
    } catch (parseError) {
      console.error('❌ JSON 解析失敗:', parseError)
      throw new Error(`JSON 解析失敗: ${parseError.message}\n響應內容: ${responseText.substring(0, 200)}`)
    }

    if (response.ok) {
      result2.value = `✅ fetch 測試成功！

HTTP 狀態: ${response.status}
狀態文本: ${response.statusText}

響應數據:
${JSON.stringify(data, null, 2)}
`
      success2.value = true
    } else {
      throw new Error(`HTTP ${response.status}: ${data.message || response.statusText}`)
    }
  } catch (err) {
    console.error('❌ fetch 測試失敗:', err)
    console.error('❌ 錯誤堆棧:', err.stack)

    result2.value = `❌ fetch 測試失敗！

錯誤: ${err.message}

${err.stack ? `\n錯誤堆棧:\n${err.stack}` : ''}
`
    success2.value = false
  } finally {
    loading2.value = false
  }
}

// 測試 3: 使用 getSalesTrend 函數（與 Dashboard 相同）
const testGetSalesTrend = async () => {
  loading3.value = true
  result3.value = '開始測試...'

  try {
    console.log('🚀 測試 3: 使用 getSalesTrend 函數')

    const response = await getSalesTrend({
      user_id: 'user123',
      user_role: 'viewer',
      days: 30
    })

    console.log('✅ getSalesTrend 響應:', response)

    result3.value = `✅ getSalesTrend 測試成功！

響應數據:
${JSON.stringify(response, null, 2)}
`
    success3.value = true
  } catch (err) {
    console.error('❌ getSalesTrend 測試失敗:', err)
    console.error('❌ 錯誤名稱:', err.name)
    console.error('❌ 錯誤消息:', err.message)

    let errorDetails = `❌ getSalesTrend 測試失敗！

錯誤名稱: ${err.name}
錯誤消息: ${err.message}
`

    if (err.response) {
      errorDetails += `
服務器響應:
- 狀態碼: ${err.response.status}
- 響應數據: ${JSON.stringify(err.response.data, null, 2)}
`
      console.error('❌ 服務器響應:', err.response.data)
    } else if (err.request) {
      errorDetails += `
請求詳情:
- 請求已發出，但沒有收到響應
`
      console.error('❌ 請求配置:', err.config)
    } else {
      errorDetails += `\n堆棧:\n${err.stack}`
    }

    result3.value = errorDetails
    success3.value = false
  } finally {
    loading3.value = false
  }
}
</script>

<style scoped>
.test-dashboard-api {
  max-width: 1200px;
  margin: 20px auto;
  padding: 20px;
  font-family: Arial, sans-serif;
}

h1 {
  color: #333;
  border-bottom: 2px solid #4CAF50;
  padding-bottom: 10px;
}

.test-panel {
  background: white;
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.test-panel h2 {
  margin-top: 0;
  color: #555;
}

button {
  background: #4CAF50;
  color: white;
  border: none;
  padding: 12px 24px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  margin: 10px 0;
}

button:hover:not(:disabled) {
  background: #45a049;
}

button:disabled {
  background: #cccccc;
  cursor: not-allowed;
}

.result {
  background: #f8f9fa;
  padding: 15px;
  border-radius: 4px;
  margin-top: 15px;
  overflow-x: auto;
  max-height: 400px;
  overflow-y: auto;
}

.result.success {
  background: #d4edda;
  color: #155724;
}

.result.error {
  background: #f8d7da;
  color: #721c24;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.6;
}

table {
  width: 100%;
  border-collapse: collapse;
  margin: 10px 0;
}

table td {
  padding: 10px;
  border: 1px solid #ddd;
}

table td:first-child {
  background: #f0f0f0;
  font-weight: bold;
  width: 200px;
}
</style>
