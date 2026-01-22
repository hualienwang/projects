<template>
  <div class="api-test-page">
    <header class="page-header">
      <h1>🔧 後端API接口測試面板</h1>
      <p>用於測試和調用後端所有可用的API接口</p>
    </header>

    <div class="api-sections">
      <!-- Dashboard APIs -->
      <div class="api-group">
        <h2>📊 數據可視化APIs</h2>
        
        <div class="api-card">
          <h3>GET /api/dashboard/charts - 獲取可用圖表列表</h3>
          <button @click="testGetCharts" :disabled="loading.charts">測試接口</button>
          <div v-if="results.charts" class="result">
            <h4>響應結果：</h4>
            <pre>{{ JSON.stringify(results.charts, null, 2) }}</pre>
          </div>
        </div>

        <div class="api-card">
          <h3>GET /api/dashboard/permissions/{user_role} - 查詢用戶權限</h3>
          <div class="input-group">
            <label>用戶角色：</label>
            <select v-model="roleForPermission">
              <option value="admin">admin</option>
              <option value="manager">manager</option>
              <option value="staff">staff</option>
              <option value="viewer">viewer</option>
            </select>
            <button @click="testGetPermissions" :disabled="loading.permissions">測試接口</button>
          </div>
          <div v-if="results.permissions" class="result">
            <h4>響應結果：</h4>
            <pre>{{ JSON.stringify(results.permissions, null, 2) }}</pre>
          </div>
        </div>

        <div class="api-card">
          <h3>POST /api/dashboard/generate - 生成數據可視化圖表</h3>
          <div class="input-group">
            <label>用戶ID：</label>
            <input v-model="chartRequest.user_id" placeholder="輸入用戶ID" />
          </div>
          <div class="input-group">
            <label>用戶角色：</label>
            <select v-model="chartRequest.user_role">
              <option value="admin">admin</option>
              <option value="manager">manager</option>
              <option value="staff">staff</option>
              <option value="viewer">viewer</option>
            </select>
          </div>
          <div class="input-group">
            <label>圖表類型：</label>
            <select v-model="chartRequest.chart_type">
              <option value="sales_trend">sales_trend</option>
              <option value="product_ranking">product_ranking</option>
              <option value="inventory_distribution">inventory_distribution</option>
              <option value="customer_analysis">customer_analysis</option>
              <option value="supplier_stats">supplier_stats</option>
            </select>
          </div>
          <div class="input-group">
            <label>開始日期：</label>
            <input v-model="chartRequest.start_date" type="date" />
          </div>
          <div class="input-group">
            <label>結束日期：</label>
            <input v-model="chartRequest.end_date" type="date" />
          </div>
          <button @click="testGenerateChart" :disabled="loading.generate">測試接口</button>
          <div v-if="results.generate" class="result">
            <h4>響應結果：</h4>
            <pre>{{ JSON.stringify(results.generate, null, 2) }}</pre>
          </div>
        </div>
      </div>

      <!-- Main APIs -->
      <div class="api-group">
        <h2>⚙️ 主要APIs</h2>
        
        <div class="api-card">
          <h3>POST /run - 運行工作流</h3>
          <div class="input-group">
            <label>請求體：</label>
            <textarea v-model="runPayload" placeholder='{"input": "your input"}' rows="4"></textarea>
          </div>
          <button @click="testRun" :disabled="loading.run">測試接口</button>
          <div v-if="results.run" class="result">
            <h4>響應結果：</h4>
            <pre>{{ JSON.stringify(results.run, null, 2) }}</pre>
          </div>
        </div>

        <div class="api-card">
          <h3>POST /stream_run - 流式運行工作流</h3>
          <div class="input-group">
            <label>請求體：</label>
            <textarea v-model="streamPayload" placeholder='{"input": "your input"}' rows="4"></textarea>
          </div>
          <button @click="testStreamRun" :disabled="loading.streamRun">測試接口</button>
          <div v-if="results.streamRun" class="result">
            <h4>響應結果：</h4>
            <pre>{{ JSON.stringify(results.streamRun, null, 2) }}</pre>
          </div>
        </div>

        <div class="api-card">
          <h3>POST /node_run/{node_id} - 運行指定節點</h3>
          <div class="input-group">
            <label>節點ID：</label>
            <input v-model="nodeId" placeholder="輸入節點ID" />
          </div>
          <div class="input-group">
            <label>請求體：</label>
            <textarea v-model="nodePayload" placeholder='{"input": "your input"}' rows="4"></textarea>
          </div>
          <button @click="testNodeRun" :disabled="loading.nodeRun">測試接口</button>
          <div v-if="results.nodeRun" class="result">
            <h4>響應結果：</h4>
            <pre>{{ JSON.stringify(results.nodeRun, null, 2) }}</pre>
          </div>
        </div>

        <div class="api-card">
          <h3>POST /cancel/{run_id} - 取消執行</h3>
          <div class="input-group">
            <label>運行ID：</label>
            <input v-model="runIdToCancel" placeholder="輸入運行ID" />
          </div>
          <button @click="testCancelRun" :disabled="loading.cancelRun">測試接口</button>
          <div v-if="results.cancelRun" class="result">
            <h4>響應結果：</h4>
            <pre>{{ JSON.stringify(results.cancelRun, null, 2) }}</pre>
          </div>
        </div>

        <div class="api-card">
          <h3>GET /graph_parameter - 獲取工作流參數</h3>
          <button @click="testGraphParameter" :disabled="loading.graphParameter">測試接口</button>
          <div v-if="results.graphParameter" class="result">
            <h4>響應結果：</h4>
            <pre>{{ JSON.stringify(results.graphParameter, null, 2) }}</pre>
          </div>
        </div>

        <div class="api-card">
          <h3>GET /health - 健康檢查</h3>
          <button @click="testHealthCheck" :disabled="loading.health">測試接口</button>
          <div v-if="results.health" class="result">
            <h4>響應結果：</h4>
            <pre>{{ JSON.stringify(results.health, null, 2) }}</pre>
          </div>
        </div>
      </div>
      
      <!-- Loading indicator -->
      <div v-if="overallLoading" class="loading-overlay">
        <div class="spinner">處理中...</div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import * as dashboardAPI from '@/api/dashboard'
import { 
  runWorkflow, 
  streamRunWorkflow, 
  runNode, 
  cancelRun, 
  getGraphParameter, 
  healthCheck 
} from '@/api/main'

// Loading states
const loading = ref({
  charts: false,
  permissions: false,
  generate: false,
  run: false,
  streamRun: false,
  nodeRun: false,
  cancelRun: false,
  graphParameter: false,
  health: false
})

// Results
const results = ref({
  charts: null,
  permissions: null,
  generate: null,
  run: null,
  streamRun: null,
  nodeRun: null,
  cancelRun: null,
  graphParameter: null,
  health: null
})

// Form data
const roleForPermission = ref('viewer')
const chartRequest = ref({
  user_id: 'test_user',
  user_role: 'viewer',
  chart_type: 'sales_trend',
  start_date: '',
  end_date: ''
})
const runPayload = ref('{"input": "test input"}')
const streamPayload = ref('{"input": "test stream input"}')
const nodeId = ref('')
const nodePayload = ref('{"input": "test node input"}')
const runIdToCancel = ref('')

// Computed property for overall loading state
const overallLoading = computed(() => {
  return Object.values(loading.value).some(status => status === true)
})

// Test functions
const testGetCharts = async () => {
  loading.value.charts = true
  try {
    const response = await dashboardAPI.getCharts()
    results.value.charts = response
  } catch (error) {
    results.value.charts = { error: error.message }
  } finally {
    loading.value.charts = false
  }
}

const testGetPermissions = async () => {
  loading.value.permissions = true
  try {
    const response = await dashboardAPI.getPermissions(roleForPermission.value)
    results.value.permissions = response
  } catch (error) {
    results.value.permissions = { error: error.message }
  } finally {
    loading.value.permissions = false
  }
}

const testGenerateChart = async () => {
  loading.value.generate = true
  try {
    const response = await dashboardAPI.generateChart(chartRequest.value)
    results.value.generate = response
  } catch (error) {
    results.value.generate = { error: error.message }
  } finally {
    loading.value.generate = false
  }
}

const testRun = async () => {
  loading.value.run = true
  try {
    const payload = JSON.parse(runPayload.value)
    const response = await runWorkflow(payload)
    results.value.run = response
  } catch (error) {
    results.value.run = { error: error.message }
  } finally {
    loading.value.run = false
  }
}

const testStreamRun = async () => {
  loading.value.streamRun = true
  try {
    const payload = JSON.parse(streamPayload.value)
    const response = await streamRunWorkflow(payload)
    results.value.streamRun = response
  } catch (error) {
    results.value.streamRun = { error: error.message }
  } finally {
    loading.value.streamRun = false
  }
}

const testNodeRun = async () => {
  loading.value.nodeRun = true
  try {
    const payload = JSON.parse(nodePayload.value)
    const response = await runNode(nodeId.value, payload)
    results.value.nodeRun = response
  } catch (error) {
    results.value.nodeRun = { error: error.message }
  } finally {
    loading.value.nodeRun = false
  }
}

const testCancelRun = async () => {
  loading.value.cancelRun = true
  try {
    const response = await cancelRun(runIdToCancel.value)
    results.value.cancelRun = response
  } catch (error) {
    results.value.cancelRun = { error: error.message }
  } finally {
    loading.value.cancelRun = false
  }
}

const testGraphParameter = async () => {
  loading.value.graphParameter = true
  try {
    const response = await getGraphParameter()
    results.value.graphParameter = response
  } catch (error) {
    results.value.graphParameter = { error: error.message }
  } finally {
    loading.value.graphParameter = false
  }
}

const testHealthCheck = async () => {
  loading.value.health = true
  try {
    const response = await healthCheck()
    results.value.health = response
  } catch (error) {
    results.value.health = { error: error.message }
  } finally {
    loading.value.health = false
  }
}
</script>

<style scoped>
.api-test-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
  background-color: #f5f5f5;
  min-height: 100vh;
}

.page-header {
  text-align: center;
  margin-bottom: 30px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.page-header h1 {
  color: #333;
  margin-bottom: 10px;
}

.api-sections {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.api-group {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.api-group h2 {
  color: #444;
  border-bottom: 2px solid #eee;
  padding-bottom: 10px;
  margin-top: 0;
}

.api-card {
  border: 1px solid #eee;
  padding: 15px;
  margin: 15px 0;
  border-radius: 6px;
  background-color: #fafafa;
}

.api-card h3 {
  color: #555;
  margin-top: 0;
  font-size: 16px;
}

.input-group {
  margin: 10px 0;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
}

.input-group label {
  min-width: 100px;
  font-weight: bold;
  color: #666;
}

.input-group input,
.input-group select,
.input-group textarea {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  flex: 1;
  min-width: 200px;
}

.input-group textarea {
  min-height: 100px;
  resize: vertical;
}

button {
  background-color: #409eff;
  color: white;
  border: none;
  padding: 10px 20px;
  border-radius: 4px;
  cursor: pointer;
  margin-top: 10px;
}

button:hover:not(:disabled) {
  background-color: #66b1ff;
}

button:disabled {
  background-color: #a0cfff;
  cursor: not-allowed;
}

.result {
  margin-top: 15px;
  padding: 15px;
  background-color: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  overflow-x: auto;
}

.result h4 {
  margin-top: 0;
  color: #444;
}

.result pre {
  margin: 10px 0 0 0;
  white-space: pre-wrap;
  word-wrap: break-word;
  color: #333;
  font-size: 14px;
}

.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0,0,0,0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.spinner {
  background: white;
  padding: 20px;
  border-radius: 8px;
  font-weight: bold;
  color: #409eff;
}
</style>