<template>
  <div class="dashboard-simple" style="padding: 20px;">
    <h1>🔍 簡化版 Dashboard - 用於診斷</h1>

    <div class="test-panel">
      <h2>API 連接測試</h2>
      <button @click="testAPI" :disabled="loading">
        {{ loading ? '測試中...' : '測試 API 連接' }}
      </button>

      <div v-if="testResult" class="result">
        <h3>測試結果</h3>
        <pre>{{ testResult }}</pre>
      </div>
    </div>

    <div class="debug-info">
      <h2>調試信息</h2>
      <table>
        <tbody>
          <tr>
            <td>用戶 ID:</td>
            <td>{{ userId }}</td>
          </tr>
          <tr>
            <td>用戶角色:</td>
            <td>{{ userRole }}</td>
          </tr>
          <tr>
            <td>API 基礎路徑:</td>
            <td>/api</td>
          </tr>
          <tr>
            <td>當前時間:</td>
            <td>{{ new Date().toLocaleString("zh-TW") }}</td>
          </tr>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import axios from 'axios'

const loading = ref(false)
const testResult = ref(null)
const userId = ref('user123')
const userRole = ref('viewer')

const testAPI = async () => {
  loading.value = true
  testResult.value = '開始測試...'

  try {
    console.log('🚀 開始測試 API 連接...')
    console.log('📝 請求 URL:', '/api/dashboard/charts')

    const response = await axios.get('/api/dashboard/charts', {
      timeout: 10000
    })

    console.log('✅ API 響應成功:', response)
    console.log('📊 響應數據:', response.data)

    testResult.value = `✅ 測試成功！

HTTP 狀態: ${response.status}
狀態文本: ${response.statusText}

響應數據:
${JSON.stringify(response.data, null, 2)}
`

  } catch (error) {
    console.error('❌ API 響應失敗:', error)

    let errorDetails = `❌ 測試失敗！

錯誤名稱: ${error.name}
錯誤消息: ${error.message}
`

    // 顯示詳細錯誤信息
    if (error.response) {
      // 服務器返回了響應，但狀態碼不在 2xx 範圍內
      errorDetails += `
服務器響應:
- 狀態碼: ${error.response.status}
- 狀態文本: ${error.response.statusText}
- 響應數據: ${JSON.stringify(error.response.data, null, 2)}
`
    } else if (error.request) {
      // 請求已發出，但沒有收到響應
      errorDetails += `
請求詳情:
- 請求已發出，但沒有收到響應
- 請求 URL: ${error.config?.url || '未知'}
- 請求方法: ${error.config?.method || '未知'}
`
      console.log('📤 請求配置:', error.config)
    } else {
      // 在設置請求時觸發了錯誤
      errorDetails += `
設置錯誤:
${error.stack}
`
    }

    testResult.value = errorDetails
  } finally {
    loading.value = false
  }
}

// 頁面加載時自動測試
testAPI()
</script>

<style scoped>
.dashboard-simple {
  font-family: Arial, sans-serif;
  max-width: 1200px;
  margin: 0 auto;
}

.test-panel, .debug-info {
  background: white;
  padding: 20px;
  margin: 20px 0;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.test-panel h2, .debug-info h2 {
  margin-top: 0;
  color: #333;
  border-bottom: 2px solid #4CAF50;
  padding-bottom: 10px;
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
}

.result h3 {
  margin-top: 0;
  color: #333;
}

pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 14px;
  line-height: 1.6;
}

.debug-info table {
  width: 100%;
  border-collapse: collapse;
}

.debug-info td {
  padding: 10px;
  border: 1px solid #ddd;
}

.debug-info td:first-child {
  background: #f0f0f0;
  font-weight: bold;
  width: 150px;
}
</style>
