<template>
  <nav class="navigation">
    <div class="nav-container">
      <div class="nav-brand">
        <h2>琼林图书进销存系统</h2>
      </div>
      <ul class="nav-menu">
        <li class="nav-item">
          <router-link to="/" class="nav-link" :class="{ active: $route.path === '/' }">
            <span class="icon">📊</span>
            <span>仪表板</span>
          </router-link>
        </li>
        <li class="nav-item">
          <router-link to="/api-test" class="nav-link" :class="{ active: $route.path === '/api-test' }">
            <span class="icon">🔧</span>
            <span>API测试</span>
          </router-link>
        </li>
      </ul>
    </div>
  </nav>
</template>

<script setup>
// Navigation component for switching between dashboard and API test page
</script>

<style scoped>
.navigation {
  background-color: #2c3e50;
  padding: 0;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  position: sticky;
  top: 0;
  z-index: 100;
}

.nav-container {
  max-width: 1200px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0 20px;
}

.nav-brand h2 {
  color: white;
  margin: 0;
  font-size: 1.5rem;
}

.nav-menu {
  display: flex;
  list-style: none;
  margin: 0;
  padding: 0;
  gap: 10px;
}

.nav-item {
  margin: 0;
}

.nav-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 15px 20px;
  color: #bdc3c7;
  text-decoration: none;
  transition: all 0.3s ease;
  border-radius: 4px;
}

.nav-link:hover {
  background-color: #34495e;
  color: #ecf0f1;
}

.nav-link.active {
  background-color: #3498db;
  color: white;
}

.icon {
  font-size: 1.2em;
}

@media (max-width: 768px) {
  .nav-container {
    flex-direction: column;
    gap: 10px;
    padding: 10px;
  }
  
  .nav-menu {
    width: 100%;
    justify-content: center;
  }
}
</style>