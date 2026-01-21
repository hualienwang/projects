# 瓊林圖書進銷存系統 - 前端使用指南

## 📖 概述

本前端項目是基於 Vue3 + Vite + Chart.js 開發的數據可視化系統，對接後端 LangGraph 工作流 API，提供豐富的數據分析圖表和基於角色的訪問控制（RBAC）。

## 🚀 快速開始

### 環境要求

- Node.js >= 16.x
- npm >= 8.x 或 pnpm >= 7.x
- 現代瀏覽器（Chrome、Firefox、Safari、Edge）

### 安裝依賴

```bash
cd frontend
npm install
```

### 啟動開發服務器

```bash
npm run dev
```

訪問 http://localhost:3000 查看應用。

### 構建生產版本

```bash
npm run build
```

### 預覽生產版本

```bash
npm run preview
```

## 📁 項目結構

```
frontend/
├── public/                 # 靜態資源
├── src/
│   ├── api/               # API 接口封裝
│   │   └── dashboard.js  # 數據可視化 API
│   ├── components/        # 組件
│   │   └── charts/       # 圖表組件
│   │       ├── SalesTrendChart.vue           # 銷售趨勢圖
│   │       ├── ProductRankingChart.vue      # 商品銷售排行
│   │       ├── InventoryDistributionChart.vue  # 庫存分佈
│   │       ├── CustomerAnalysisChart.vue     # 客戶消費分析
│   │       └── SupplierStatsChart.vue        # 供應商統計
│   ├── router/            # 路由配置
│   │   └── index.js
│   ├── stores/            # Pinia 狀態管理
│   │   └── user.js       # 用戶角色和權限管理
│   ├── views/             # 頁面視圖
│   │   └── Dashboard.vue  # 數據儀表板主頁
│   ├── App.vue            # 根組件
│   ├── main.js            # 入口文件
│   └── style.css          # 全局樣式
├── index.html             # HTML 模板
├── vite.config.js         # Vite 配置
├── package.json           # 項目配置
└── .gitignore             # Git 忽略文件
```

## 🔑 權限管理

### 角色定義

| 角色 | 名稱 | 權限 |
|------|------|------|
| `admin` | 系統管理員 | 所有圖表 |
| `manager` | 經理 | 銷售趨勢、商品排行、庫存分佈、客戶分析 |
| `staff` | 員工 | 銷售趨勢、商品排行 |
| `viewer` | 查看者 | 銷售趨勢 |

### 權限檢查

在組件中使用 Pinia store 進行權限檢查：

```vue
<script setup>
import { computed } from 'vue'
import { useUserStore } from '@/stores/user'

const userStore = useUserStore()

// 檢查是否有權限
const hasPermission = computed(() => {
  return userStore.isManager // 或 isAdmin, isStaff
})
</script>
```

## 📊 圖表組件

### 1. 銷售趨勢圖

**組件**: `SalesTrendChart.vue`

**功能**: 
- 按日期統計銷售額和訂單數
- 支持選擇時間範圍（7天、30天、90天）
- 折線圖展示

**使用示例**:
```vue
<template>
  <SalesTrendChart 
    :auto-load="true"
    @data-loaded="onDataLoaded"
    @error="onError"
  />
</template>

<script setup>
const onDataLoaded = (data) => {
  console.log('數據加載成功:', data)
}

const onError = (error) => {
  console.error('加載失敗:', error)
}
</script>
```

### 2. 商品銷售排行

**組件**: `ProductRankingChart.vue`

**功能**:
- 統計商品銷售數量
- 支持選擇 Top N（5、10、20）
- 柱狀圖展示

### 3. 庫存狀態分佈

**組件**: `InventoryDistributionChart.vue`

**功能**:
- 統計正常、低庫存、缺貨商品數量
- 餅圖展示
- 顯示庫存摘要

### 4. 客戶消費分析

**組件**: `CustomerAnalysisChart.vue`

**功能**:
- 統計客戶消費金額
- 支持選擇 Top N（5、10、20）
- 水平柱狀圖展示

### 5. 供應商採購統計

**組件**: `SupplierStatsChart.vue`

**功能**:
- 統計供應商商品數量和成本
- 混合圖表（柱狀圖 + 折線圖）展示

## 🌐 API 接口

所有 API 接口封裝在 `src/api/dashboard.js` 中。

### 主要接口

```javascript
import { 
  getCharts,
  getPermissions,
  generateChart,
  getSalesTrend,
  getProductRanking,
  getInventoryDistribution
} from '@/api/dashboard'

// 獲取可用圖表列表
const charts = await getCharts()

// 查詢用戶權限
const permissions = await getPermissions('manager')

// 生成圖表
const chart = await generateChart({
  user_id: 'user123',
  user_role: 'manager',
  chart_type: 'sales_trend',
  start_date: '2026-01-01',
  end_date: '2026-01-31'
})

// 快捷接口
const salesTrend = await getSalesTrend({
  user_id: 'user123',
  user_role: 'manager',
  days: 30
})
```

## 🎨 樣式定製

### 全局樣式

全局樣式定義在 `src/style.css` 中，包含：
- 滾動條樣式
- 按鈕基礎樣式
- 輸入框基礎樣式

### 組件樣式

每個組件使用 Scoped CSS，樣式不會影響其他組件。

### 響應式設計

所有圖表組件都支持響應式設計，自動適配不同屏幕尺寸：

```css
@media (max-width: 768px) {
  .charts-grid {
    grid-template-columns: 1fr;
  }
}
```

## 🔧 配置說明

### Vite 配置

`vite.config.js` 主要配置：

```javascript
export default defineConfig({
  plugins: [vue()],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    }
  },
  server: {
    port: 3000,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true
      }
    }
  }
})
```

### API 代理

開發環境下，Vite 自動將 `/api` 請求代理到後端服務器（http://localhost:8000）。

## 🐛 常見問題

### 1. CORS 錯誤

**問題**: 瀏覽器控制台顯示 CORS 錯誤

**解決**: 確保後端服務器已啟動，並且 Vite 配置中已設置代理。

### 2. 權限不足

**問題**: 圖表顯示"權限不足"提示

**解決**: 檢查當前用戶角色是否具有訪問該圖表的權限。

### 3. 圖表不顯示

**問題**: 圖表加載但不顯示

**解決**: 
- 檢查數據格式是否正確
- 打開瀏覽器控制台查看錯誤信息
- 確認 Chart.js 版本兼容性

### 4. 依賴安裝失敗

**問題**: `npm install` 失敗

**解決**:
```bash
# 清除緩存
npm cache clean --force

# 使用淘寶鏡像
npm config set registry https://registry.npmmirror.com

# 重新安裝
npm install
```

## 📦 部署

### Docker 部署

```dockerfile
FROM node:16-alpine as builder

WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

### Nginx 配置

```nginx
server {
    listen 80;
    server_name your-domain.com;
    
    root /usr/share/nginx/html;
    index index.html;
    
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    location /api {
        proxy_pass http://backend:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## 🔄 更新日誌

### v1.0.0 (2026-01-21)

- ✅ 初始版本發布
- ✅ 集成 Chart.js 圖表庫
- ✅ 實現 5 種數據可視化圖表
- ✅ 實現基於角色的訪問控制
- ✅ 響應式設計
- ✅ API 接口封裝
- ✅ Pinia 狀態管理

## 📝 開發規範

### 組件命名

- 使用 PascalCase 命名組件文件
- 組件名稱應具有描述性

### 代碼風格

- 使用 Vue3 Composition API (`<script setup>`)
- 使用 TypeScript 類型註解（推薦）
- 遵循 ESLint 規則

### 提交規範

```
feat: 新功能
fix: 修復 bug
docs: 文檔更新
style: 代碼格式調整
refactor: 代碼重構
test: 測試相關
chore: 構建/工具鏈相關
```

## 🤝 貢獻

歡迎提交 Issue 和 Pull Request！

## 📄 許可證

MIT License

## 📞 聯繫方式

如有問題，請聯繫開發團隊。
