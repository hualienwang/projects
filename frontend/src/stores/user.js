import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { getPermissions } from '@/api/dashboard'

export const useUserStore = defineStore('user', () => {
  // 用户 ID
  const userId = ref('user123')
  
  // 用户角色
  const userRole = ref('viewer')
  
  // 权限缓存
  const permissions = ref({})
  
  // 可用角色列表
  const availableRoles = {
    admin: '系統管理員',
    manager: '經理',
    staff: '員工',
    viewer: '查看者'
  }
  
  // 角色描述
  const roleDescriptions = {
    admin: '擁有所有權限，可查看所有圖表',
    manager: '可查看銷售趨勢、商品排行、庫存分佈、客戶分析',
    staff: '可查看銷售趨勢、商品排行',
    viewer: '只能查看銷售趨勢'
  }
  
  // 计算属性：当前角色名称
  const roleName = computed(() => availableRoles[userRole.value] || '未知角色')
  
  // 计算属性：角色描述
  const roleDescription = computed(() => roleDescriptions[userRole.value] || '')
  
  // 计算属性：是否有管理员权限
  const isAdmin = computed(() => userRole.value === 'admin')
  
  // 计算属性：是否有经理权限
  const isManager = computed(() => ['admin', 'manager'].includes(userRole.value))
  
  // 计算属性：是否有员工权限
  const isStaff = computed(() => ['admin', 'manager', 'staff'].includes(userRole.value))
  
  /**
   * 设置用户角色
   * @param {string} role - 角色名称
   */
  const setRole = (role) => {
    if (availableRoles[role]) {
      userRole.value = role
      permissions.value = {}
      console.log(`角色已切换为: ${roleName.value}`)
    } else {
      console.error(`无效的角色: ${role}`)
    }
  }
  
  /**
   * 加载用户权限
   */
  const loadPermissions = async () => {
    try {
      const response = await getPermissions(userRole.value)
      if (response.success) {
        permissions.value = response.permissions
        return response.permissions
      }
    } catch (error) {
      console.error('加载权限失败:', error)
    }
    return {}
  }
  
  /**
   * 检查是否有权限访问指定图表
   * @param {string} chartType - 图表类型
   */
  const hasPermission = (chartType) => {
    return permissions.value[chartType] === true
  }
  
  /**
   * 重置用户状态
   */
  const reset = () => {
    userId.value = 'user123'
    userRole.value = 'viewer'
    permissions.value = {}
  }
  
  return {
    // 状态
    userId,
    userRole,
    permissions,
    availableRoles,
    roleDescriptions,
    
    // 计算属性
    roleName,
    roleDescription,
    isAdmin,
    isManager,
    isStaff,
    
    // 方法
    setRole,
    loadPermissions,
    hasPermission,
    reset
  }
})
