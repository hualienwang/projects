/**
 * 工作流 API 调用工具
 * 提供核心工作流 API 的调用功能
 */
import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

/**
 * 同步执行工作流
 * @param {Object} payload - 工作流输入参数
 * @returns {Promise<Object>} 工作流执行结果
 */
export async function runWorkflow(payload) {
  try {
    const response = await api.post('/run', payload)
    return response.data
  } catch (error) {
    console.error('执行工作流失败:', error)
    throw error
  }
}

/**
 * 流式执行工作流（SSE）
 * @param {Object} payload - 工作流输入参数
 * @param {Function} onMessage - 消息回调函数 (message) => void
 * @param {Function} onError - 错误回调函数 (error) => void
 * @param {Function} onComplete - 完成回调函数 () => void
 * @returns {Promise<void>}
 */
export async function streamWorkflow(payload, onMessage, onError, onComplete) {
  try {
    const response = await fetch('/api/stream_run', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(payload)
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''

    while (true) {
      const { done, value } = await reader.read()

      if (done) {
        if (onComplete) onComplete()
        break
      }

      // 解码数据
      buffer += decoder.decode(value, { stream: true })

      // 处理 SSE 格式
      const lines = buffer.split('\n')
      buffer = lines.pop() || '' // 保留未完整的行

      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const data = line.slice(6)
          try {
            const message = JSON.parse(data)
            if (onMessage) onMessage(message)
          } catch (e) {
            console.warn('解析消息失败:', data)
          }
        }
      }
    }
  } catch (error) {
    console.error('流式执行工作流失败:', error)
    if (onError) onError(error)
    throw error
  }
}

/**
 * 取消执行
 * @param {string} runId - 执行 ID
 * @returns {Promise<Object>} 取消结果
 */
export async function cancelWorkflow(runId) {
  try {
    const response = await api.post(`/cancel/${runId}`)
    return response.data
  } catch (error) {
    console.error('取消工作流失败:', error)
    throw error
  }
}

/**
 * 执行单个节点
 * @param {string} nodeId - 节点 ID
 * @param {Object} payload - 节点输入参数
 * @returns {Promise<Object>} 节点执行结果
 */
export async function runNode(nodeId, payload) {
  try {
    const response = await api.post(`/node_run/${nodeId}`, payload)
    return response.data
  } catch (error) {
    console.error('执行节点失败:', error)
    throw error
  }
}

/**
 * 获取工作流输入输出 Schema
 * @returns {Promise<Object>} 工作流 Schema
 */
export async function getWorkflowSchema() {
  try {
    const response = await api.get('/graph_inout_schema')
    return response.data
  } catch (error) {
    console.error('获取工作流 Schema 失败:', error)
    throw error
  }
}

/**
 * 获取工作流节点列表
 * @returns {Promise<Object>} 节点信息
 */
export async function getWorkflowNodes() {
  try {
    // 这个接口可能不存在，先尝试调用
    const response = await api.get('/graph_nodes')
    return response.data
  } catch (error) {
    console.error('获取工作流节点失败:', error)
    throw error
  }
}
