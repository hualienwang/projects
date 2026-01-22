import axios from 'axios'

// Create axios instance for main APIs
const mainApi = axios.create({
  baseURL: '/', // Base URL is root since we're proxying through Vite
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Request interceptor
mainApi.interceptors.request.use(
  config => {
    console.log('API Request:', config.method?.toUpperCase(), config.url, config.data)
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// Response interceptor
mainApi.interceptors.response.use(
  response => {
    console.log('API Response:', response.status, response.data)
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error.response?.data || error)
  }
)

// ==================== Main Backend APIs ====================

/**
 * Run workflow
 * POST /run
 */
export const runWorkflow = (data) => {
  return mainApi.post('/run', data)
}

/**
 * Stream run workflow
 * POST /stream_run
 */
export const streamRunWorkflow = (data) => {
  return mainApi.post('/stream_run', data)
}

/**
 * Run specific node
 * POST /node_run/{node_id}
 */
export const runNode = (nodeId, data) => {
  return mainApi.post(`/node_run/${nodeId}`, data)
}

/**
 * Cancel run
 * POST /cancel/{run_id}
 */
export const cancelRun = (runId) => {
  return mainApi.post(`/cancel/${runId}`)
}

/**
 * Get graph parameter
 * GET /graph_parameter
 */
export const getGraphParameter = () => {
  return mainApi.get('/graph_parameter')
}

/**
 * Health check
 * GET /health
 */
export const healthCheck = () => {
  return mainApi.get('/health')
}

/**
 * OpenAI compatible chat completions
 * POST /v1/chat/completions
 */
export const chatCompletions = (data) => {
  return mainApi.post('/v1/chat/completions', data)
}

// Export as default
export default mainApi