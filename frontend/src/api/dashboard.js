import axios from 'axios'

// 创建 axios 实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器
api.interceptors.request.use(
  config => {
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    console.error('API Error:', error)
    return Promise.reject(error.response?.data || error)
  }
)

// ==================== API 接口 ====================

/**
 * 获取可用图表列表
 */
export const getCharts = () => {
  return api.get('/dashboard/charts')
}

/**
 * 查询用户权限
 * @param {string} userRole - 用户角色
 */
export const getPermissions = (userRole) => {
  return api.get(`/dashboard/permissions/${userRole}`)
}

/**
 * 生成图表
 * @param {Object} data - 图表请求参数
 */
export const generateChart = (data) => {
  return api.post('/dashboard/generate', data)
}

/**
 * 获取图表类型列表
 */
export const getChartTypes = () => {
  return api.get('/dashboard/chart-types')
}

/**
 * 获取角色列表
 */
export const getRoles = () => {
  return api.get('/dashboard/roles')
}

/**
 * 快速获取销售趋势图
 * @param {Object} params - 查询参数
 */
export const getSalesTrend = (params) => {
  return api.post('/dashboard/generate', {
    user_id: params.user_id,
    user_role: params.user_role || 'viewer',
    chart_type: 'sales_trend',
    start_date: params.start_date,
    end_date: params.end_date
  })
}

/**
 * 快速获取商品销售排行
 * @param {Object} params - 查询参数
 */
export const getProductRanking = (params) => {
  return api.post('/dashboard/product-ranking', null, { params })
}

/**
 * 快速获取库存状态分布
 * @param {Object} params - 查询参数
 */
export const getInventoryDistribution = (params) => {
  return api.post('/dashboard/inventory-distribution', null, { params })
}

// 默认导出
export default api
