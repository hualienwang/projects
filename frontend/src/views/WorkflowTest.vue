<template>
  <div class="workflow-test">
    <h1>🔧 工作流 API 測試</h1>
    <p class="subtitle">測試後端核心工作流 API：/run、/stream_run、/cancel、/node_run</p>

    <!-- 工作流選擇器 -->
    <div class="workflow-selector">
      <label for="workflow-select">選擇工作流：</label>
      <select id="workflow-select" v-model="selectedWorkflow" @change="onWorkflowChange">
        <option value="stock_alert">📦 庫存預警工作流 (Stock Alert)</option>
        <option value="order_processing">📋 訂單處理工作流 (Order Processing)</option>
      </select>
      <p class="workflow-info">{{ currentWorkflowInfo }}</p>
    </div>

    <div class="test-grid">
      <!-- 1. 同步執行工作流 -->
      <div class="test-panel">
        <h2>1️⃣ 同步執行工作流 (POST /run)</h2>
        <div class="input-section">
          <div class="form-group">
            <label for="run-payload">輸入參數 (JSON):</label>
            <textarea
              id="run-payload"
              v-model="runPayload"
              rows="6"
              placeholder='{"key": "value"}'
            ></textarea>
          </div>
          <button
            @click="testRun"
            :disabled="runLoading"
            class="btn btn-primary"
          >
            {{ runLoading ? '執行中...' : '🚀 執行工作流' }}
          </button>
        </div>

        <div v-if="runResult" class="result-section">
          <h3>✅ 執行結果</h3>
          <pre class="result-json">{{ JSON.stringify(runResult, null, 2) }}</pre>
          <p v-if="runResult.run_id" class="run-id">Run ID: <code>{{ runResult.run_id }}</code></p>
        </div>

        <div v-if="runError" class="error-section">
          <h3>❌ 執行失敗</h3>
          <pre class="error-message">{{ runError }}</pre>
        </div>
      </div>

      <!-- 2. 流式執行工作流 -->
      <div class="test-panel">
        <h2>2️⃣ 流式執行工作流 (POST /stream_run)</h2>
        <div class="input-section">
          <div class="form-group">
            <label for="stream-payload">輸入參數 (JSON):</label>
            <textarea
              id="stream-payload"
              v-model="streamPayload"
              rows="6"
              placeholder='{"key": "value"}'
            ></textarea>
          </div>
          <button
            @click="testStreamRun"
            :disabled="streamLoading"
            class="btn btn-primary"
          >
            {{ streamLoading ? '執行中...' : '🌊 流式執行工作流' }}
          </button>
          <button
            v-if="streamRunId"
            @click="testCancel"
            class="btn btn-danger"
          >
            🛑 取消執行
          </button>
        </div>

        <div v-if="streamRunId" class="info-section">
          <p>Run ID: <code>{{ streamRunId }}</code></p>
          <p>狀態: <span :class="streamLoading ? 'status-running' : 'status-completed'">
            {{ streamLoading ? '執行中...' : '已完成' }}
          </span></p>
        </div>

        <div v-if="streamMessages.length > 0" class="result-section">
          <h3>📨 流式消息 ({{ streamMessages.length }} 條)</h3>
          <div class="stream-messages">
            <div
              v-for="(msg, index) in streamMessages"
              :key="index"
              class="message-item"
            >
              <span class="message-index">#{{ index + 1 }}</span>
              <pre class="message-content">{{ JSON.stringify(msg, null, 2) }}</pre>
            </div>
          </div>
        </div>

        <div v-if="streamError" class="error-section">
          <h3>❌ 流式執行失敗</h3>
          <pre class="error-message">{{ streamError }}</pre>
        </div>
      </div>

      <!-- 3. 取消執行 -->
      <div class="test-panel">
        <h2>3️⃣ 取消執行 (POST /cancel/{run_id})</h2>
        <div class="input-section">
          <div class="form-group">
            <label for="cancel-run-id">Run ID:</label>
            <input
              id="cancel-run-id"
              v-model="cancelRunId"
              type="text"
              placeholder="從流式執行中獲取 Run ID"
            />
            <button @click="useStreamRunId" class="btn btn-small" :disabled="!streamRunId">
              使用當前流式 Run ID
            </button>
          </div>
          <button
            @click="testCancel"
            :disabled="cancelLoading"
            class="btn btn-danger"
          >
            {{ cancelLoading ? '取消中...' : '🛑 取消執行' }}
          </button>
        </div>

        <div v-if="cancelResult" class="result-section">
          <h3>✅ 取消結果</h3>
          <pre class="result-json">{{ JSON.stringify(cancelResult, null, 2) }}</pre>
        </div>

        <div v-if="cancelError" class="error-section">
          <h3>❌ 取消失敗</h3>
          <pre class="error-message">{{ cancelError }}</pre>
        </div>
      </div>

      <!-- 4. 執行單個節點 -->
      <div class="test-panel">
        <h2>4️⃣ 執行單個節點 (POST /node_run/{node_id})</h2>
        <div class="input-section">
          <div class="form-group">
            <label for="node-id">節點 ID:</label>
            <input
              id="node-id"
              v-model="nodeId"
              type="text"
              placeholder="例如: license_check_node"
            />
            <div class="node-hint">
              💡 可用節點：
              <span v-if="selectedWorkflow === 'stock_alert'">
                check_inventory_node, analyze_alert_node, generate_report_node, send_email_node, record_alert_node
              </span>
              <span v-else>
                validate_order_node, check_order_inventory_node, create_order_node, deduct_inventory_node, generate_shipping_order_node, notify_customer_node
              </span>
            </div>
          </div>
          <div class="form-group">
            <label for="node-payload">節點輸入參數 (JSON):</label>
            <textarea
              id="node-payload"
              v-model="nodePayload"
              rows="6"
              placeholder='{"key": "value"}'
            ></textarea>
          </div>
          <button
            @click="testRunNode"
            :disabled="nodeLoading"
            class="btn btn-primary"
          >
            {{ nodeLoading ? '執行中...' : '⚡ 執行節點' }}
          </button>
        </div>

        <div v-if="nodeResult" class="result-section">
          <h3>✅ 節點執行結果</h3>
          <pre class="result-json">{{ JSON.stringify(nodeResult, null, 2) }}</pre>
        </div>

        <div v-if="nodeError" class="error-section">
          <h3>❌ 節點執行失敗</h3>
          <pre class="error-message">{{ nodeError }}</pre>
        </div>
      </div>
    </div>

    <!-- 快捷操作面板 -->
    <div class="quick-actions">
      <h2>⚡ 快捷操作</h2>
      <div class="action-buttons">
        <button @click="loadSamplePayload('stock_alert')" class="btn btn-secondary">
          📦 加載庫存預警示例
        </button>
        <button @click="loadSamplePayload('order')" class="btn btn-secondary">
          📋 加載訂單處理示例
        </button>
        <button @click="loadSamplePayload('simple')" class="btn btn-secondary">
          🔧 加載簡單示例
        </button>
        <button @click="clearAll" class="btn btn-secondary">
          🧹 清空所有結果
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  runWorkflow,
  streamWorkflow,
  cancelWorkflow,
  runNode
} from '@/api/workflow'

// ========== 工作流選擇 ==========
const selectedWorkflow = ref('stock_alert')

const currentWorkflowInfo = computed(() => {
  if (selectedWorkflow.value === 'stock_alert') {
    return '📦 庫存預警工作流：檢查庫存狀況，發送預警郵件給管理者'
  } else {
    return '📋 訂單處理工作流：驗證訂單 → 檢查庫存 → 創建訂單 → 扣減庫存 → 生成發貨單 → 通知客戶'
  }
})

// 工作流切換
function onWorkflowChange() {
  clearAll()
  if (selectedWorkflow.value === 'order_processing') {
    loadSamplePayload('order')
  } else {
    loadSamplePayload('stock_alert')
  }
}

// ========== 狀態定義 ==========

// 1. 同步執行工作流
const runPayload = ref(JSON.stringify({
  email_recipients: ["manager@example.com"],
  check_overstock: true
}, null, 2))
const runLoading = ref(false)
const runResult = ref(null)
const runError = ref('')

// 2. 流式執行工作流
const streamPayload = ref(JSON.stringify({
  email_recipients: ["manager@example.com"],
  check_overstock: true
}, null, 2))
const streamLoading = ref(false)
const streamRunId = ref('')
const streamMessages = ref([])
const streamError = ref('')

// 3. 取消執行
const cancelRunId = ref('')
const cancelLoading = ref(false)
const cancelResult = ref(null)
const cancelError = ref('')

// 4. 執行單個節點
const nodeId = ref('check_inventory_node')
const nodePayload = ref(JSON.stringify({
  check_overstock: true
}, null, 2))
const nodeLoading = ref(false)
const nodeResult = ref(null)
const nodeError = ref('')

// ========== 測試函數 ==========

/**
 * 測試 1: 同步執行工作流
 */
async function testRun() {
  runLoading.value = true
  runResult.value = null
  runError.value = ''

  try {
    const payload = JSON.parse(runPayload.value)
    console.log('🚀 執行工作流:', payload)

    const result = await runWorkflow(payload)
    runResult.value = result

    console.log('✅ 工作流執行完成:', result)
  } catch (error) {
    console.error('❌ 工作流執行失敗:', error)
    runError.value = error.response?.data?.detail || error.message || '執行失敗'
  } finally {
    runLoading.value = false
  }
}

/**
 * 測試 2: 流式執行工作流
 */
async function testStreamRun() {
  streamLoading.value = true
  streamRunId.value = ''
  streamMessages.value = []
  streamError.value = ''

  try {
    const payload = JSON.parse(streamPayload.value)
    console.log('🌊 流式執行工作流:', payload)

    await streamWorkflow(
      payload,
      (message) => {
        // 消息回調
        console.log('📨 收到消息:', message)
        streamMessages.value.push(message)

        // 提取 run_id
        if (message.run_id && !streamRunId.value) {
          streamRunId.value = message.run_id
        }
      },
      (error) => {
        // 錯誤回調
        console.error('❌ 流式執行錯誤:', error)
        streamError.value = error.message || '流式執行失敗'
      },
      () => {
        // 完成回調
        console.log('✅ 流式執行完成')
        streamLoading.value = false
      }
    )
  } catch (error) {
    console.error('❌ 流式執行失敗:', error)
    streamError.value = error.message || '流式執行失敗'
    streamLoading.value = false
  }
}

/**
 * 測試 3: 取消執行
 */
async function testCancel() {
  const runIdToCancel = cancelRunId.value || streamRunId.value

  if (!runIdToCancel) {
    alert('請先執行流式工作流以獲取 Run ID')
    return
  }

  cancelLoading.value = true
  cancelResult.value = null
  cancelError.value = ''

  try {
    console.log('🛑 取消工作流:', runIdToCancel)

    const result = await cancelWorkflow(runIdToCancel)
    cancelResult.value = result

    if (result.status === 'success') {
      streamLoading.value = false
    }

    console.log('✅ 取消成功:', result)
  } catch (error) {
    console.error('❌ 取消失敗:', error)
    cancelError.value = error.response?.data?.detail || error.message || '取消失敗'
  } finally {
    cancelLoading.value = false
  }
}

/**
 * 測試 4: 執行單個節點
 */
async function testRunNode() {
  if (!nodeId.value) {
    alert('請輸入節點 ID')
    return
  }

  nodeLoading.value = true
  nodeResult.value = null
  nodeError.value = ''

  try {
    const payload = JSON.parse(nodePayload.value)
    console.log('⚡ 執行節點:', nodeId.value, payload)

    const result = await runNode(nodeId.value, payload)
    nodeResult.value = result

    console.log('✅ 節點執行完成:', result)
  } catch (error) {
    console.error('❌ 節點執行失敗:', error)
    nodeError.value = error.response?.data?.detail || error.message || '節點執行失敗'
  } finally {
    nodeLoading.value = false
  }
}

// ========== 快捷操作 ==========

/**
 * 使用當前流式 Run ID
 */
function useStreamRunId() {
  if (streamRunId.value) {
    cancelRunId.value = streamRunId.value
  }
}

/**
 * 加載示例數據
 */
function loadSamplePayload(type) {
  console.log('📋 loadSamplePayload 被調用，type:', type)
  console.log('📋 當前選中的工作流:', selectedWorkflow.value)

  // 自動切換到對應的工作流
  if (type === 'order' && selectedWorkflow.value !== 'order_processing') {
    console.log('📋 自動切換到訂單處理工作流')
    selectedWorkflow.value = 'order_processing'
  } else if (type === 'stock_alert' && selectedWorkflow.value !== 'stock_alert') {
    console.log('📋 自動切換到庫存預警工作流')
    selectedWorkflow.value = 'stock_alert'
  }

  if (type === 'stock_alert') {
    // 库存预警工作流示例
    console.log('📋 加載庫存預警示例數據')
    runPayload.value = JSON.stringify({
      email_recipients: ["manager@example.com", "admin@example.com"],
      check_overstock: true
    }, null, 2)
    streamPayload.value = JSON.stringify({
      email_recipients: ["manager@example.com", "admin@example.com"],
      check_overstock: true
    }, null, 2)
    nodeId.value = 'check_inventory_node'
    nodePayload.value = JSON.stringify({
      check_overstock: true
    }, null, 2)
  } else if (type === 'order') {
    // 訂單處理工作流示例
    console.log('📋 加載訂單處理示例數據')
    runPayload.value = JSON.stringify({
      customer_id: 1,
      items: [
        { product_id: 1, quantity: 2 },
        { product_id: 2, quantity: 1 }
      ]
    }, null, 2)
    streamPayload.value = JSON.stringify({
      customer_id: 1,
      items: [
        { product_id: 1, quantity: 2 },
        { product_id: 2, quantity: 1 }
      ]
    }, null, 2)
    nodeId.value = 'validate_order_node'
    nodePayload.value = JSON.stringify({
      customer_id: 1,
      items: [
        { product_id: 1, quantity: 2 },
        { product_id: 2, quantity: 1 }
      ]
    }, null, 2)
  } else if (type === 'simple') {
    // 简单示例
    console.log('📋 加載簡單示例數據')
    if (selectedWorkflow.value === 'order_processing') {
      runPayload.value = JSON.stringify({
        customer_id: 1,
        items: [{ product_id: 1, quantity: 1 }]
      }, null, 2)
      streamPayload.value = JSON.stringify({
        customer_id: 1,
        items: [{ product_id: 1, quantity: 1 }]
      }, null, 2)
      nodeId.value = 'validate_order_node'
      nodePayload.value = JSON.stringify({
        customer_id: 1,
        items: [{ product_id: 1, quantity: 1 }]
      }, null, 2)
    } else {
      runPayload.value = JSON.stringify({
        email_recipients: ["manager@example.com"],
        check_overstock: false
      }, null, 2)
      streamPayload.value = JSON.stringify({
        email_recipients: ["manager@example.com"],
        check_overstock: false
      }, null, 2)
      nodeId.value = 'check_inventory_node'
      nodePayload.value = JSON.stringify({
        check_overstock: false
      }, null, 2)
    }
  }

  console.log('✅ 示例數據加載完成')
  alert(`✅ 已加載 ${type === 'order' ? '訂單處理' : type === 'stock_alert' ? '庫存預警' : '簡單'}示例數據\n📌 工作流已切換為：${selectedWorkflow.value === 'order_processing' ? '訂單處理' : '庫存預警'}`)
}

/**
 * 清空所有結果
 */
function clearAll() {
  runResult.value = null
  runError.value = ''
  streamRunId.value = ''
  streamMessages.value = []
  streamError.value = ''
  cancelResult.value = null
  cancelError.value = ''
  nodeResult.value = null
  nodeError.value = ''
}
</script>

<style scoped>
.workflow-test {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

h1 {
  color: #333;
  margin-bottom: 10px;
}

.subtitle {
  color: #666;
  margin-bottom: 10px;
}

.workflow-selector {
  background: #fff3e0;
  border-left: 4px solid #ff9800;
  padding: 16px;
  border-radius: 4px;
  margin-bottom: 30px;
}

.workflow-selector label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.workflow-selector select {
  width: 100%;
  max-width: 400px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  cursor: pointer;
}

.workflow-selector select:focus {
  outline: none;
  border-color: #ff9800;
  box-shadow: 0 0 0 2px rgba(255, 152, 0, 0.2);
}

.workflow-info {
  margin-top: 12px;
  color: #666;
  font-size: 14px;
}

.info-note {
  color: #2196F3;
  margin-bottom: 30px;
  font-size: 14px;
  padding: 12px;
  background: #e3f2fd;
  border-radius: 4px;
  border-left: 4px solid #2196F3;
}

.info-note strong {
  color: #1565c0;
}

.test-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
  margin-bottom: 30px;
}

.test-panel {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.test-panel h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  border-bottom: 2px solid #4CAF50;
  padding-bottom: 10px;
}

.input-section {
  margin-bottom: 20px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  margin-bottom: 8px;
  color: #555;
  font-weight: 500;
}

.form-group textarea,
.form-group input {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  font-size: 14px;
  box-sizing: border-box;
}

.form-group textarea {
  resize: vertical;
  min-height: 150px;
}

.form-group input {
  min-height: 40px;
}

.node-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #666;
  background: #f5f5f5;
  padding: 8px;
  border-radius: 4px;
}

.btn {
  padding: 12px 24px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  transition: all 0.3s ease;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-primary {
  background: #4CAF50;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #45a049;
}

.btn-danger {
  background: #f44336;
  color: white;
}

.btn-danger:hover:not(:disabled) {
  background: #da190b;
}

.btn-secondary {
  background: #2196F3;
  color: white;
}

.btn-secondary:hover:not(:disabled) {
  background: #0b7dda;
}

.btn-small {
  padding: 6px 12px;
  font-size: 12px;
  margin-top: 8px;
}

.result-section {
  background: #e8f5e9;
  border-left: 4px solid #4CAF50;
  padding: 16px;
  border-radius: 4px;
  margin-top: 20px;
}

.result-section h3 {
  margin: 0 0 10px 0;
  color: #2e7d32;
  font-size: 16px;
}

.result-json {
  background: white;
  padding: 12px;
  border-radius: 4px;
  font-size: 12px;
  max-height: 300px;
  overflow: auto;
  margin: 0;
}

.run-id {
  margin-top: 10px;
  color: #666;
}

.run-id code {
  background: #f5f5f5;
  padding: 4px 8px;
  border-radius: 4px;
  font-family: 'Courier New', monospace;
  color: #e91e63;
}

.error-section {
  background: #ffebee;
  border-left: 4px solid #f44336;
  padding: 16px;
  border-radius: 4px;
  margin-top: 20px;
}

.error-section h3 {
  margin: 0 0 10px 0;
  color: #c62828;
  font-size: 16px;
}

.error-message {
  background: white;
  padding: 12px;
  border-radius: 4px;
  color: #c62828;
  font-size: 12px;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 300px;
  overflow: auto;
  margin: 0;
}

.info-section {
  background: #e3f2fd;
  border-left: 4px solid #2196F3;
  padding: 12px;
  border-radius: 4px;
  margin-top: 16px;
}

.info-section p {
  margin: 4px 0;
  color: #1565c0;
}

.status-running {
  color: #ff9800;
  font-weight: bold;
}

.status-completed {
  color: #4CAF50;
  font-weight: bold;
}

.stream-messages {
  max-height: 400px;
  overflow-y: auto;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.message-item {
  padding: 12px;
  border-bottom: 1px solid #eee;
  display: flex;
  gap: 12px;
}

.message-item:last-child {
  border-bottom: none;
}

.message-index {
  min-width: 50px;
  color: #999;
  font-size: 12px;
  text-align: right;
}

.message-content {
  flex: 1;
  font-size: 11px;
  background: #fafafa;
  padding: 8px;
  border-radius: 4px;
  margin: 0;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.quick-actions {
  background: white;
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.quick-actions h2 {
  margin: 0 0 20px 0;
  color: #333;
  font-size: 20px;
  border-bottom: 2px solid #2196F3;
  padding-bottom: 10px;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

@media (max-width: 768px) {
  .test-grid {
    grid-template-columns: 1fr;
  }

  .action-buttons {
    flex-direction: column;
  }
}
</style>
