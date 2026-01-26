<template>
  <nav class="navigation">
    <div class="nav-container">
      <div class="nav-brand">
        <h1>📊 瓊林圖書進銷存系統</h1>
      </div>

      <div class="nav-menu">
        <router-link to="/" class="nav-link" active-class="active">
          <span class="nav-icon">📊</span>
          <span class="nav-text">數據儀表板</span>
        </router-link>

        <router-link to="/test-chart" class="nav-link" active-class="active">
          <span class="nav-icon">📈</span>
          <span class="nav-text">圖表測試</span>
        </router-link>

        <router-link to="/dashboard-simple" class="nav-link" active-class="active">
          <span class="nav-icon">🔍</span>
          <span class="nav-text">診斷模式</span>
        </router-link>

        <router-link to="/test-dashboard-api" class="nav-link" active-class="active">
          <span class="nav-icon">🧪</span>
          <span class="nav-text">API 測試</span>
        </router-link>

        <router-link to="/diagnose-api" class="nav-link" active-class="active">
          <span class="nav-icon">🔧</span>
          <span class="nav-text">API 診斷</span>
        </router-link>

        <router-link to="/workflow-test" class="nav-link" active-class="active">
          <span class="nav-icon">⚙️</span>
          <span class="nav-text">工作流測試</span>
        </router-link>
      </div>

      <div class="nav-user">
        <div class="user-info">
          <span class="user-avatar">👤</span>
          <span class="user-name">{{ userName }}</span>
        </div>
      </div>
    </div>
  </nav>
</template>

<script setup>
import { ref } from 'vue'

const userName = ref('Admin')
</script>

<style scoped>
.navigation {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
  position: sticky;
  top: 0;
  z-index: 1000;
}

.nav-container {
  max-width: 1400px;
  margin: 0 auto;
  padding: 0 20px;
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 60px;
}

.nav-brand h1 {
  color: white;
  font-size: 18px;
  margin: 0;
  white-space: nowrap;
}

.nav-menu {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}

.nav-link {
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  padding: 8px 16px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  gap: 6px;
  transition: all 0.3s ease;
  font-size: 14px;
}

.nav-link:hover {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.nav-link.active {
  background: rgba(255, 255, 255, 0.3);
  color: white;
  font-weight: 600;
}

.nav-icon {
  font-size: 16px;
}

.nav-text {
  white-space: nowrap;
}

.nav-user {
  display: flex;
  align-items: center;
  gap: 10px;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  color: white;
  background: rgba(255, 255, 255, 0.2);
  padding: 6px 12px;
  border-radius: 20px;
}

.user-avatar {
  font-size: 16px;
}

.user-name {
  font-size: 14px;
  font-weight: 500;
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    height: auto;
    padding: 10px;
  }

  .nav-brand h1 {
    font-size: 16px;
    margin-bottom: 10px;
  }

  .nav-menu {
    width: 100%;
    justify-content: center;
  }

  .nav-link {
    padding: 6px 12px;
    font-size: 12px;
  }

  .nav-user {
    display: none;
  }
}
</style>
