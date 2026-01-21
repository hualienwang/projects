# 数据可视化系统使用指南

## 概述

数据可视化系统提供了基于 LangGraph 工作流的数据分析能力，支持多种图表类型和基于角色的访问控制（RBAC）。系统集成了 Chart.js 生成交互式图表，通过 RESTful API 供前端调用。

## 功能特性

### 1. 支持的图表类型

| 图表类型 | 描述 | 图表形式 |
|---------|------|---------|
| `sales_trend` | 销售趋势 - 按日期统计销售额和订单数 | 折线图 |
| `product_ranking` | 商品销售排行 - 统计商品销售数量 | 柱状图 |
| `inventory_distribution` | 库存状态分布 - 正常/低库存/缺货 | 饼图 |
| `customer_analysis` | 客户消费分析 - 统计客户消费金额 | 水平柱状图 |
| `supplier_stats` | 供应商采购统计 - 统计供应商商品数量和成本 | 混合图表 |

### 2. 权限管理

系统实现了基于角色的访问控制（RBAC），支持以下角色：

| 角色 | 权限 | 可访问图表 |
|------|------|-----------|
| `admin` | 系统管理员，所有权限 | 所有图表 |
| `manager` | 经理，查看报表 | sales_trend, product_ranking, inventory_distribution, customer_analysis |
| `staff` | 员工，查看基本报表 | sales_trend, product_ranking |
| `viewer` | 查看者，只读 | sales_trend |

## API 接口文档

### 基础信息

- **Base URL**: `http://localhost:8000`
- **API 前缀**: `/api/dashboard`
- **数据格式**: JSON

### 接口列表

#### 1. 获取可用图表列表

**接口**: `GET /api/dashboard/charts`

**描述**: 获取所有支持的图表类型及其描述

**响应示例**:
```json
{
  "success": true,
  "available_charts": {
    "sales_trend": "销售趋势 - 按日期统计销售额和订单数",
    "product_ranking": "商品销售排行 - 统计商品销售数量",
    "inventory_distribution": "库存状态分布 - 正常/低库存/缺货",
    "customer_analysis": "客户消费分析 - 统计客户消费金额",
    "supplier_stats": "供应商采购统计 - 统计供应商商品数量和成本"
  }
}
```

---

#### 2. 查询用户权限

**接口**: `GET /api/dashboard/permissions/{user_role}`

**描述**: 查询指定角色对所有图表的访问权限

**路径参数**:
- `user_role`: 用户角色 (admin/manager/staff/viewer)

**响应示例**:
```json
{
  "success": true,
  "user_role": "manager",
  "permissions": {
    "sales_trend": true,
    "product_ranking": true,
    "inventory_distribution": true,
    "customer_analysis": true,
    "supplier_stats": false
  }
}
```

---

#### 3. 生成数据可视化图表

**接口**: `POST /api/dashboard/generate`

**描述**: 生成指定类型的数据可视化图表

**请求体**:
```json
{
  "user_id": "user123",
  "user_role": "manager",
  "chart_type": "sales_trend",
  "start_date": "2024-01-01",
  "end_date": "2024-01-31"
}
```

**参数说明**:
- `user_id` (必填): 用户ID
- `user_role` (必填): 用户角色
- `chart_type` (必填): 图表类型
- `start_date` (可选): 开始日期，默认为30天前
- `end_date` (可选): 结束日期，默认为今天

**响应示例**:
```json
{
  "success": true,
  "has_permission": true,
  "chart_data": {
    "labels": ["2024-01-01", "2024-01-02", "2024-01-03"],
    "datasets": [
      {
        "label": "销售额 (元)",
        "data": [1000, 1500, 1200],
        "borderColor": "rgb(75, 192, 192)",
        "backgroundColor": "rgba(75, 192, 192, 0.2)",
        "tension": 0.1,
        "fill": true
      }
    ]
  },
  "chart_config": {
    "type": "line",
    "data": { /* ... */ },
    "options": {
      "responsive": true,
      "plugins": {
        "title": {
          "display": true,
          "text": "销售趋势 (2024-01-01 ~ 2024-01-31)"
        }
      }
    }
  },
  "message": "图表生成成功"
}
```

**错误响应**:
```json
{
  "detail": "权限不足: viewer 角色无权访问 inventory_distribution 图表"
}
```

---

#### 4. 获取图表类型列表

**接口**: `GET /api/dashboard/chart-types`

**描述**: 获取支持的图表类型列表

**响应示例**:
```json
{
  "sales_trend": "销售趋势 - 按日期统计销售额和订单数",
  "product_ranking": "商品销售排行 - 统计商品销售数量",
  "inventory_distribution": "库存状态分布 - 正常/低库存/缺货",
  "customer_analysis": "客户消费分析 - 统计客户消费金额",
  "supplier_stats": "供应商采购统计 - 统计供应商商品数量和成本"
}
```

---

#### 5. 获取角色列表

**接口**: `GET /api/dashboard/roles`

**描述**: 获取支持的角色列表及其权限描述

**响应示例**:
```json
{
  "admin": {
    "description": "系统管理员",
    "permissions": ["sales_trend", "product_ranking", "inventory_distribution", "customer_analysis", "supplier_stats"]
  },
  "manager": {
    "description": "经理",
    "permissions": ["sales_trend", "product_ranking", "inventory_distribution", "customer_analysis"]
  },
  "staff": {
    "description": "员工",
    "permissions": ["sales_trend", "product_ranking"]
  },
  "viewer": {
    "description": "查看者",
    "permissions": ["sales_trend"]
  }
}
```

---

### 便捷接口

#### 快速获取销售趋势图

**接口**: `POST /api/dashboard/sales-trend`

**参数**:
- `user_id`: 用户ID
- `user_role`: 用户角色（默认: viewer）
- `days`: 统计天数（默认: 30）

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/dashboard/sales-trend?user_id=user123&user_role=manager&days=7"
```

---

#### 快速获取商品销售排行

**接口**: `POST /api/dashboard/product-ranking`

**参数**:
- `user_id`: 用户ID
- `user_role`: 用户角色（默认: viewer）
- `days`: 统计天数（默认: 30）
- `top_n`: 返回前N个商品（默认: 10）

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/dashboard/product-ranking?user_id=user123&user_role=manager&days=7&top_n=5"
```

---

#### 快速获取库存状态分布

**接口**: `POST /api/dashboard/inventory-distribution`

**参数**:
- `user_id`: 用户ID
- `user_role`: 用户角色（默认: manager）

**请求示例**:
```bash
curl -X POST "http://localhost:8000/api/dashboard/inventory-distribution?user_id=user123&user_role=admin"
```

---

## Chart.js 前端集成指南

### 1. 安装依赖

```html
<!-- 通过 CDN 引入 Chart.js -->
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

或使用 npm:

```bash
npm install chart.js
```

### 2. 基本使用示例

```html
<!DOCTYPE html>
<html>
<head>
    <title>数据可视化示例</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
</head>
<body>
    <div style="width: 800px;">
        <canvas id="myChart"></canvas>
    </div>

    <script>
        // 调用API获取图表数据
        async function loadChart() {
            const response = await fetch('http://localhost:8000/api/dashboard/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: 'user123',
                    user_role: 'manager',
                    chart_type: 'sales_trend',
                    start_date: '2024-01-01',
                    end_date: '2024-01-31'
                })
            });

            const result = await response.json();

            if (result.success && result.has_permission) {
                // 创建图表
                const ctx = document.getElementById('myChart').getContext('2d');
                new Chart(ctx, result.chart_config);
            } else {
                console.error('图表生成失败:', result.message);
            }
        }

        // 页面加载时调用
        loadChart();
    </script>
</body>
</html>
```

### 3. React 集成示例

```jsx
import React, { useEffect, useRef } from 'react';
import Chart from 'chart.js/auto';

function SalesTrendChart({ userRole, startDate, endDate }) {
    const chartRef = useRef(null);
    const chartInstance = useRef(null);

    useEffect(() => {
        async function fetchChartData() {
            const response = await fetch('http://localhost:8000/api/dashboard/generate', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    user_id: 'user123',
                    user_role: userRole,
                    chart_type: 'sales_trend',
                    start_date: startDate,
                    end_date: endDate
                })
            });

            const result = await response.json();

            if (result.success && result.has_permission) {
                const ctx = chartRef.current.getContext('2d');
                
                // 销毁旧图表
                if (chartInstance.current) {
                    chartInstance.current.destroy();
                }

                // 创建新图表
                chartInstance.current = new Chart(ctx, result.chart_config);
            }
        }

        fetchChartData();

        // 清理函数
        return () => {
            if (chartInstance.current) {
                chartInstance.current.destroy();
            }
        };
    }, [userRole, startDate, endDate]);

    return <canvas ref={chartRef}></canvas>;
}

export default SalesTrendChart;
```

### 4. Vue 集成示例

```vue
<template>
  <div>
    <canvas ref="chartRef"></canvas>
  </div>
</template>

<script>
import Chart from 'chart.js/auto';

export default {
  name: 'DashboardChart',
  props: {
    userRole: {
      type: String,
      default: 'viewer'
    },
    chartType: {
      type: String,
      default: 'sales_trend'
    }
  },
  data() {
    return {
      chartInstance: null
    };
  },
  mounted() {
    this.loadChart();
  },
  methods: {
    async loadChart() {
      const response = await fetch('http://localhost:8000/api/dashboard/generate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: 'user123',
          user_role: this.userRole,
          chart_type: this.chartType
        })
      });

      const result = await response.json();

      if (result.success && result.has_permission) {
        const ctx = this.$refs.chartRef.getContext('2d');
        this.chartInstance = new Chart(ctx, result.chart_config);
      }
    }
  },
  beforeUnmount() {
    if (this.chartInstance) {
      this.chartInstance.destroy();
    }
  }
};
</script>
```

### 5. 图表交互功能

#### 5.1 添加点击事件

```javascript
const chart = new Chart(ctx, result.chart_config);

// 点击图表元素时触发
chart.onClick = (event, elements) => {
    if (elements.length > 0) {
        const element = elements[0];
        const datasetIndex = element.datasetIndex;
        const index = element.index;
        
        const label = chart.data.labels[index];
        const value = chart.data.datasets[datasetIndex].data[index];
        
        console.log(`点击了: ${label}, 值: ${value}`);
    }
};
```

#### 5.2 添加工具提示自定义

```javascript
chart.options.plugins.tooltip = {
    callbacks: {
        label: function(context) {
            let label = context.dataset.label || '';
            if (label) {
                label += ': ';
            }
            label += context.parsed.y + ' 元';
            return label;
        }
    }
};
```

#### 5.3 响应式调整

```javascript
// 监听窗口大小变化
window.addEventListener('resize', () => {
    if (chartInstance) {
        chartInstance.resize();
    }
});
```

## 工作流架构

### 数据流

```
用户请求 → API层 → 权限检查节点 → 路由分发 → 数据提取节点 → 返回图表配置
                ↓
         (验证角色权限)
                ↓
    根据图表类型选择节点:
    - sales_trend_node
    - product_ranking_node
    - inventory_distribution_node
    - customer_analysis_node
    - supplier_stats_node
```

### 权限检查逻辑

```python
ROLE_PERMISSIONS = {
    "admin": ["sales_trend", "product_ranking", "inventory_distribution", "customer_analysis", "supplier_stats"],
    "manager": ["sales_trend", "product_ranking", "inventory_distribution", "customer_analysis"],
    "staff": ["sales_trend", "product_ranking"],
    "viewer": ["sales_trend"]
}
```

## 故障排查

### 常见错误

#### 1. 权限不足

**错误信息**: `权限不足: viewer 角色无权访问 inventory_distribution 图表`

**解决方案**: 检查用户角色是否有权限访问该图表类型，或提升用户角色权限。

#### 2. 无效的图表类型

**错误信息**: `无效的图表类型: unknown_chart`

**解决方案**: 检查 `chart_type` 参数是否为支持的类型之一。

#### 3. 数据库连接错误

**错误信息**: `图表生成失败: database connection error`

**解决方案**: 检查数据库连接配置和连接状态。

#### 4. 日期范围错误

**错误信息**: `日期范围无效`

**解决方案**: 确保 `start_date` <= `end_date`，并且日期格式正确（YYYY-MM-DD）。

## 性能优化建议

1. **缓存图表数据**: 对于不常变化的数据，可以在前端缓存图表数据，减少API调用
2. **分页加载**: 对于大量数据，实现分页加载或虚拟滚动
3. **按需加载**: 只在图表可见时加载数据（懒加载）
4. **数据聚合**: 后端支持数据聚合（按天/周/月），减少数据传输量
5. **使用Web Worker**: 在Web Worker中处理大量数据，避免阻塞主线程

## 测试脚本

参见 `scripts/test_dashboard.py` 进行完整的API测试。

## 更新日志

### v1.0.0 (2024-01-01)
- 初始版本发布
- 支持5种图表类型
- 实现基于角色的访问控制
- 提供RESTful API接口
- 集成Chart.js前端支持
