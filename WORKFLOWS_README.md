# 瓊林圖書進銷存系統 - 工作流使用指南

## 项目概述

本项目为瓊林圖書事業有限公司实现了完整的進銷存管理系統，包含6个核心业务自动化工作流。

## 工作流列表

### 1. 库存预警工作流 📦
**文件位置**: `src/graphs/graph.py`

**功能**:
- 自动检查所有商品库存
- 识别低库存商品
- 使用AI生成智能补货建议
- 生成详细的预警报告
- 发送邮件通知管理人员
- 记录预警历史

**测试命令**:
```bash
PYTHONPATH=/workspace/projects/src:/workspace/projects python scripts/test_stock_alert.py
```

**使用示例**:
```python
from graphs.graph import main_graph

result = main_graph.invoke({
    "email_recipients": ["manager@example.com"],
    "check_overstock": False
})
```

---

### 2. 客户订单处理工作流 🛒
**文件位置**: `src/graphs/graph_order.py`

**功能**:
- 验证客户和订单信息
- 检查商品库存是否充足
- 自动创建订单和订单明细
- 扣减库存数量
- 生成发货单
- 发送邮件通知客户
- 处理库存不足情况

**测试命令**:
```bash
PYTHONPATH=/workspace/projects/src:/workspace/projects python scripts/test_order_processing.py
```

**使用示例**:
```python
from graphs.graph_order import main_graph as order_graph

result = order_graph.invoke({
    "customer_id": 1,
    "items": [
        {"product_id": 1, "quantity": 2}
    ]
})
```

---

### 3. 客户忠诚度管理工作流 ⭐
**文件位置**: `src/graphs/graph_loyalty.py`

**功能**:
- 自动计算客户积分
- 根据积分判断会员等级
- 自动升级会员等级
- 生成忠诚度分析报告
- 发送升级通知邮件
- 展示会员权益

**测试命令**:
```bash
PYTHONPATH=/workspace/projects/src:/workspace/projects python scripts/test_loyalty.py
```

**使用示例**:
```python
from graphs.graph_loyalty import main_graph as loyalty_graph

result = loyalty_graph.invoke({
    "customer_id": 3,
    "order_amount": 3000.0
})
```

**会员等级规则**:
- 10000积分：鑽石會員（95折）
- 5000积分：白金會員（96折）
- 2000积分：金卡會員（97折）
- 500积分：銀卡會員（98折）
- 0-499积分：普通會員

---

### 4. 销售数据分析工作流 📊
**文件位置**: `src/graphs/graph_sales.py`

**功能**:
- 收集指定时间范围的销售数据
- 统计总销售额和订单数
- 识别热销商品排行
- 分析销售趋势
- 检查库存不足商品
- 使用AI提供业务洞察
- 生成可视化销售报告
- 发送报告给管理层

**测试命令**:
```bash
PYTHONPATH=/workspace/projects/src:/workspace/projects python scripts/test_sales_analysis.py
```

**使用示例**:
```python
from graphs.graph_sales import main_graph as sales_graph

result = sales_graph.invoke({
    "report_type": "daily",
    "start_date": "2026-01-01",
    "end_date": "2026-01-21",
    "email_recipients": ["manager@example.com"]
})
```

**报告类型**: `daily`（日报）、`weekly`（周报）、`monthly`（月报）

---

### 5. POS前台销售工作流 💳
**文件位置**: `src/graphs/graph_pos.py`

**功能**:
- 支持扫码识别商品（条码或ISBN）
- 实时检查商品库存
- 添加商品到购物车
- 订单汇总和会员折扣计算
- 创建销售订单
- 自动扣减库存
- 生成销售小票并上传到对象存储
- 发送小票邮件给客户

**测试命令**:
```bash
PYTHONPATH=/workspace/projects/src:/workspace/projects python scripts/test_pos_standalone.py
```

**使用示例**:
```python
from graphs.graph_pos import pos_graph

# 扫码添加商品
result = pos_graph.invoke({
    "action": "scan",
    "scanned_code": "9789571468753"
})

# 结账
result = pos_graph.invoke({
    "action": "checkout",
    "cart_items": [
        {
            "product_id": 1,
            "name": "Python 程式設計：從入門到精通",
            "author": "王小明",
            "isbn": "9789571468753",
            "quantity": 1,
            "unit_price": 580.0,
            "subtotal": 580.0
        }
    ],
    "customer_id": 1
})
```

**操作类型**: `scan`（扫码）、`checkout`（结账）

**详细文档**: 查看 `POS_README.md` 了解更多使用说明

---

### 6. 供应商采购管理工作流 🚚
**文件位置**: `src/graphs/graph_procurement.py`

**功能**:
- 自动识别低库存商品
- 生成智能采购计划
- 推荐最优供应商
- 计算采购成本
- 生成正式采购单
- 发送采购单给供应商

**测试命令**:
```bash
PYTHONPATH=/workspace/projects/src:/workspace/projects python scripts/test_procurement.py
```

**使用示例**:
```python
from graphs.graph_procurement import main_graph as procurement_graph

result = procurement_graph.invoke({
    "check_all_low_stock": True
})
```

---

### 7. 数据可视化工作流 📈
**文件位置**: `src/graphs/graph_dashboard.py`

**功能**:
- 基于角色的访问控制（RBAC）
- 销售趋势分析（折线图）
- 商品销售排行（柱状图）
- 库存状态分布（饼图）
- 客户消费分析（水平柱状图）
- 供应商采购统计（混合图表）
- 生成Chart.js格式的图表配置
- 提供RESTful API接口供前端调用

**支持的图表类型**:
- `sales_trend`: 销售趋势 - 按日期统计销售额和订单数
- `product_ranking`: 商品销售排行 - 统计商品销售数量
- `inventory_distribution`: 库存状态分布 - 正常/低库存/缺货
- `customer_analysis`: 客户消费分析 - 统计客户消费金额
- `supplier_stats`: 供应商采购统计 - 统计供应商商品数量和成本

**权限角色**:
- `admin`: 系统管理员，所有权限
- `manager`: 经理，访问销售趋势、商品排行、库存分布、客户分析
- `staff`: 员工，访问销售趋势、商品排行
- `viewer`: 查看者，只读，访问销售趋势

**测试命令**:
```bash
PYTHONPATH=/workspace/projects/src:/workspace/projects python scripts/test_dashboard.py
```

**使用示例**:
```python
from graphs.graph_dashboard import main_graph as dashboard_graph

# 生成销售趋势图
result = dashboard_graph.invoke({
    "user_id": "user123",
    "user_role": "manager",
    "chart_type": "sales_trend",
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
})

# 生成商品销售排行
result = dashboard_graph.invoke({
    "user_id": "user123",
    "user_role": "staff",
    "chart_type": "product_ranking",
    "start_date": "2026-01-01",
    "end_date": "2026-01-31"
})
```

**RESTful API接口**:
```bash
# 获取可用图表列表
GET /api/dashboard/charts

# 查询用户权限
GET /api/dashboard/permissions/{user_role}

# 生成图表
POST /api/dashboard/generate
{
  "user_id": "user123",
  "user_role": "manager",
  "chart_type": "sales_trend",
  "start_date": "2026-01-01",
  "end_date": "2026-01-31"
}

# 快捷接口
POST /api/dashboard/sales-trend
POST /api/dashboard/product-ranking
POST /api/dashboard/inventory-distribution
```

**详细文档**: 查看 `DASHBOARD_README.md` 了解API详细说明和Chart.js集成指南

---

## 数据库表结构

### 核心表
- **products**: 商品信息表
- **inventory**: 库存表
- **suppliers**: 供应商表
- **customers**: 客户表
- **orders**: 订单表
- **order_items**: 订单明细表
- **stock_alerts**: 库存预警记录表

### Manager 接口
- **ProductManager**: 商品管理
- **InventoryManager**: 库存管理

---

## 配置文件

### LLM配置
- `config/stock_alert_analysis_cfg.json`: 库存分析AI配置
- `config/sales_analysis_cfg.json`: 销售分析AI配置

---

## 辅助脚本

### 数据准备
```bash
# 准备商品和库存数据
PYTHONPATH=/workspace/projects/src:/workspace/projects python scripts/prepare_test_data.py

# 准备客户数据
PYTHONPATH=/workspace/projects/src:/workspace/projects python scripts/prepare_customer_data.py
```

### 数据查询
```bash
# 查看订单
PYTHONPATH=/workspace/projects/src:/workspace/projects python scripts/check_orders.py

# 查看库存
PYTHONPATH=/workspace/projects/src:/workspace/projects python scripts/check_inventory.py
```

---

## 测试数据

### 已创建的测试数据

**供应商**:
- 三民書局（ID: 1）

**商品**（5本）:
1. Python 程式設計：從入門到精通（ISBN: 9789571468753）
2. 資料庫系統概論（ISBN: 9789864345982）
3. 演算法導論（第三版）（ISBN: 9789573284561）
4. 人工智慧：現代方法（ISBN: 9789861234567）
5. 深度學習（ISBN: 9789577890123）

**客户**（3位）:
1. 張三 - 金卡會員（1500积分）
2. 李四 - 銀卡會員（800积分）
3. 王五 - 普通會員（200积分）

---

## 技术栈

- **工作流框架**: LangGraph
- **数据库**: PostgreSQL
- **ORM**: SQLAlchemy
- **数据验证**: Pydantic
- **大语言模型**: 豆包
- **邮件服务**: SMTP/IMAP

---

## 使用说明

### 切换工作流

修改 `src/main.py` 中的导入语句来切换不同的工作流：

```python
# 库存预警工作流
from graphs.graph import main_graph

# 订单处理工作流
from graphs.graph_order import main_graph

# 客户忠诚度工作流
from graphs.graph_loyalty import main_graph

# 销售分析工作流
from graphs.graph_sales import main_graph

# 采购管理工作流
from graphs.graph_procurement import main_graph
```

---

## 项目结构

```
src/
├── graphs/
│   ├── state.py              # 库存预警工作流状态
│   ├── node.py               # 库存预警工作流节点
│   ├── graph.py              # 库存预警工作流编排
│   ├── state_order.py        # 订单处理工作流状态
│   ├── node_order.py         # 订单处理工作流节点
│   ├── graph_order.py        # 订单处理工作流编排
│   ├── state_loyalty.py      # 客户忠诚度工作流状态
│   ├── node_loyalty.py       # 客户忠诚度工作流节点
│   ├── graph_loyalty.py      # 客户忠诚度工作流编排
│   ├── state_sales.py        # 销售分析工作流状态
│   ├── node_sales.py         # 销售分析工作流节点
│   ├── graph_sales.py        # 销售分析工作流编排
│   ├── state_procurement.py  # 采购管理工作流状态
│   ├── node_procurement.py   # 采购管理工作流节点
│   ├── graph_procurement.py  # 采购管理工作流编排
│   ├── state_pos.py          # POS系统工作流状态
│   ├── node_pos.py           # POS系统工作流节点
│   └── graph_pos.py          # POS系统工作流编排
├── storage/database/
│   ├── shared/model.py       # 数据库模型
│   ├── product_manager.py    # 商品管理
│   └── inventory_manager.py  # 库存管理

config/
├── stock_alert_analysis_cfg.json  # 库存分析配置
└── sales_analysis_cfg.json       # 销售分析配置

scripts/
├── prepare_test_data.py      # 准备测试数据
├── prepare_customer_data.py  # 准备客户数据
├── check_orders.py           # 查看订单
├── check_inventory.py        # 查看库存
├── test_stock_alert.py       # 测试库存预警
├── test_order_processing.py # 测试订单处理
├── test_loyalty.py          # 测试忠诚度管理
├── test_sales_analysis.py   # 测试销售分析
├── test_procurement.py      # 测试采购管理
├── test_pos_standalone.py   # 测试POS系统
└── pos_examples.py          # POS系统使用示例
```

---

## 注意事项

1. **邮件功能**: 需要配置SMTP服务才能正常发送邮件
2. **工作流切换**: 每次只能使用一个主图，需要修改 `src/main.py` 的导入
3. **测试数据**: 使用 `scripts/prepare_test_data.py` 生成测试数据
4. **数据库迁移**: 修改模型后需要运行 `coze-coding-ai db upgrade`

---

## 完成状态

✅ 库存预警工作流 - 完成
✅ 客户订单处理工作流 - 完成
✅ 客户忠诚度管理工作流 - 完成
✅ 销售数据分析工作流 - 完成
✅ 供应商采购管理工作流 - 完成
✅ POS前台销售工作流 - 完成

---

## 联系方式

如有问题，请联系技术支持。
