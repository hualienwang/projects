<template>
  <div class="dashboard">
    <header class="dashboard-header">
      <div class="header-left">
        <h1>📊 瓊林圖書進銷存系統 - 數據可視化</h1>
      </div>
      <div class="header-right">
        <div class="user-info">
          <span class="user-label">當前角色:</span>
          <span class="user-role">{{ userStore.roleName }}</span>
        </div>
        <div class="role-selector">
          <select v-model="selectedRole" @change="handleRoleChange">
            <option v-for="(name, role) in userStore.availableRoles" :key="role" :value="role">
              {{ name }}
            </option>
          </select>
        </div>
      </div>
    </header>
    
    <div class="role-description">
      <p>📋 {{ userStore.roleDescription }}</p>
    </div>
    
    <div class="charts-grid">
      <!-- 销售趋势图 -->
      <div class="chart-card" :class="{ 'no-permission': !hasSalesTrendPermission }">
        <SalesTrendChart 
          v-if="hasSalesTrendPermission"
          @data-loaded="onDataLoaded"
          @error="onError"
        />
        <div v-else class="permission-denied">
          <p>🔒 您當前角色無權訪問此圖表</p>
        </div>
      </div>
      
      <!-- 商品销售排行 -->
      <div class="chart-card" :class="{ 'no-permission': !hasProductRankingPermission }">
        <ProductRankingChart 
          v-if="hasProductRankingPermission"
          @data-loaded="onDataLoaded"
          @error="onError"
        />
        <div v-else class="permission-denied">
          <p>🔒 您當前角色無權訪問此圖表</p>
        </div>
      </div>
      
      <!-- 库存状态分布 -->
      <div class="chart-card" :class="{ 'no-permission': !hasInventoryPermission }">
        <InventoryDistributionChart 
          v-if="hasInventoryPermission"
          @data-loaded="onDataLoaded"
          @error="onError"
        />
        <div v-else class="permission-denied">
          <p>🔒 您當前角色無權訪問此圖表</p>
        </div>
      </div>
      
      <!-- 客户消费分析 -->
      <div class="chart-card" :class="{ 'no-permission': !hasCustomerAnalysisPermission }">
        <CustomerAnalysisChart 
          v-if="hasCustomerAnalysisPermission"
          @data-loaded="onDataLoaded"
          @error="onError"
        />
        <div v-else class="permission-denied">
          <p>🔒 您當前角色無權訪問此圖表</p>
        </div>
      </div>
      
      <!-- 供应商采购统计 -->
      <div class="chart-card" :class="{ 'no-permission': !hasSupplierStatsPermission }">
        <SupplierStatsChart 
          v-if="hasSupplierStatsPermission"
          @data-loaded="onDataLoaded"
          @error="onError"
        />
        <div v-else class="permission-denied">
          <p>🔒 您當前角色無權訪問此圖表</p>
        </div>
      </div>
    </div>
    
    <!-- Toast 通知 -->
    <div v-if="toast.show" class="toast" :class="toast.type">
      {{ toast.message }}
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useUserStore } from '@/stores/user'
import SalesTrendChart from '@/components/charts/SalesTrendChart.vue'
import ProductRankingChart from '@/components/charts/ProductRankingChart.vue'
import InventoryDistributionChart from '@/components/charts/InventoryDistributionChart.vue'
import CustomerAnalysisChart from '@/components/charts/CustomerAnalysisChart.vue'
import SupplierStatsChart from '@/components/charts/SupplierStatsChart.vue'

const userStore = useUserStore()
const selectedRole = ref(userStore.userRole)
const toast = ref({
  show: false,
  message: '',
  type: 'success'
})

// 权限检查
const hasSalesTrendPermission = computed(() => {
  return ['admin', 'manager', 'staff', 'viewer'].includes(userStore.userRole)
})

const hasProductRankingPermission = computed(() => {
  return ['admin', 'manager', 'staff'].includes(userStore.userRole)
})

const hasInventoryPermission = computed(() => {
  return ['admin', 'manager'].includes(userStore.userRole)
})

const hasCustomerAnalysisPermission = computed(() => {
  return ['admin', 'manager'].includes(userStore.userRole)
})

const hasSupplierStatsPermission = computed(() => {
  return userStore.userRole === 'admin'
})

/**
 * 角色切换处理
 */
const handleRoleChange = () => {
  userStore.setRole(selectedRole.value)
  showToast(`角色已切換為: ${userStore.roleName}`, 'success')
}

/**
 * 数据加载成功
 */
const onDataLoaded = (data) => {
  console.log('图表数据加载成功:', data)
}

/**
 * 错误处理
 */
const onError = (error) => {
  showToast(`錯誤: ${error}`, 'error')
  console.error('图表加载错误:', error)
}

/**
 * 显示 Toast 通知
 */
const showToast = (message, type = 'success') => {
  toast.value = {
    show: true,
    message,
    type
  }
  
  setTimeout(() => {
    toast.value.show = false
  }, 3000)
}

onMounted(async () => {
  // 加载用户权限
  await userStore.loadPermissions()
})
</script>

<style scoped>
.dashboard {
  min-height: 100vh;
  padding: 20px;
  background: #f0f2f5;
}

.dashboard-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-left h1 {
  margin: 0;
  color: #333;
  font-size: 24px;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.user-label {
  color: #666;
  font-size: 14px;
}

.user-role {
  padding: 6px 12px;
  background: #409eff;
  color: white;
  border-radius: 4px;
  font-size: 14px;
  font-weight: bold;
}

.role-selector select {
  padding: 8px 12px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 14px;
  cursor: pointer;
  min-width: 120px;
}

.role-selector select:hover {
  border-color: #409eff;
}

.role-description {
  margin-bottom: 20px;
  padding: 12px 20px;
  background: #ecf5ff;
  border-left: 4px solid #409eff;
  border-radius: 4px;
  color: #606266;
}

.role-description p {
  margin: 0;
  font-size: 14px;
}

.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(500px, 1fr));
  gap: 20px;
}

.chart-card {
  background: white;
  border-radius: 8px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.chart-card.no-permission {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f5f7fa;
  border: 2px dashed #dcdfe6;
}

.permission-denied {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: #909399;
  font-size: 16px;
}

.toast {
  position: fixed;
  top: 20px;
  right: 20px;
  padding: 12px 20px;
  border-radius: 4px;
  color: white;
  font-size: 14px;
  z-index: 1000;
  animation: slideIn 0.3s ease;
}

.toast.success {
  background: #67c23a;
}

.toast.error {
  background: #f56c6c;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@media (max-width: 1200px) {
  .charts-grid {
    grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  }
}

@media (max-width: 768px) {
  .dashboard-header {
    flex-direction: column;
    gap: 15px;
    text-align: center;
  }
  
  .header-right {
    flex-direction: column;
    width: 100%;
  }
  
  .role-selector select {
    width: 100%;
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
</style>
