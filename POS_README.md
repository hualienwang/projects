# POS系统前台工作流

## 概述

这是一个基于LangGraph的POS（销售点）系统前台工作流，能够与后台进销存系统无缝连接，实现商品销售、库存管理、订单处理等核心功能。

## 主要功能

### 1. 扫码销售
- 支持通过条码或ISBN识别商品
- 实时检查商品库存
- 自动添加商品到购物车
- 显示商品详细信息（名称、作者、出版社、价格等）

### 2. 购物车管理
- 支持多个商品添加到购物车
- 自动计算商品小计
- 支持相同商品数量累加

### 3. 订单处理
- 自动生成订单编号
- 支持客户识别和会员等级管理
- 自动计算订单总价
- 支持会员折扣（金卡会员10%、钻石会员15%）
- 自动计算消费积分（1元=1积分）

### 4. 库存管理
- 销售时自动扣减库存
- 库存不足时提示警告

### 5. 小票生成
- 自动生成详细销售小票
- 小票上传到对象存储
- 提供小票下载链接

### 6. 邮件通知
- 支持发送小票邮件给客户
- 包含小票下载链接

## 工作流程

```
扫码销售流程：
扫码识别 → 检查库存 → 添加到购物车

结账流程：
订单汇总 → 创建订单 → 扣减库存 → 生成小票 → 发送邮件
```

## 技术栈

- **LangGraph**: 工作流编排框架
- **Python**: 主要开发语言
- **PostgreSQL**: 数据库
- **SQLAlchemy**: ORM框架
- **Pydantic**: 数据验证
- **对象存储**: S3兼容存储
- **邮件集成**: SMTP/IMAP

## 文件结构

```
src/graphs/
├── state_pos.py       # POS系统状态定义
├── node_pos.py        # POS系统节点实现
└── graph_pos.py       # POS系统图编排

scripts/
└── test_pos_standalone.py  # POS系统测试脚本
```

## 节点说明

### 1. scan_product_node
**功能**: 扫码识别商品  
**输入**: scanned_code, action  
**输出**: product_info, found

### 2. check_inventory_node
**功能**: 检查商品库存是否充足  
**输入**: product_info, quantity  
**输出**: inventory_available, current_stock, shortage

### 3. add_to_cart_node
**功能**: 添加商品到购物车  
**输入**: product_info, quantity, cart_items  
**输出**: cart_items, added

### 4. calculate_order_node
**功能**: 计算订单总价和会员折扣  
**输入**: cart_items, customer_id  
**输出**: order_summary, customer_info

### 5. create_order_node
**功能**: 创建订单并更新客户信息  
**输入**: order_summary, customer_id  
**输出**: order_id, order_no, success

### 6. deduct_inventory_node
**功能**: 扣减商品库存  
**输入**: cart_items  
**输出**: success, updated_products

### 7. generate_receipt_node
**功能**: 生成销售小票并上传到对象存储  
**输入**: order_summary, order_no, customer_info  
**输出**: receipt_url, receipt_content

### 8. send_email_node
**功能**: 发送小票邮件给客户  
**输入**: receipt_url, customer_email, order_no  
**输出**: email_sent, email_address

## 使用方法

### 1. 扫码添加商品

```python
from graphs.graph_pos import pos_graph

test_input = {
    "action": "scan",
    "scanned_code": "9789571468753"  # 商品ISBN或条码
}

results = []
for chunk in pos_graph.stream(test_input):
    print(chunk)
    results.append(chunk)
```

### 2. 结账

```python
test_input = {
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
    "customer_id": 1  # 可选，不填则为散客
}

results = []
for chunk in pos_graph.stream(test_input):
    print(chunk)
    results.append(chunk)
```

## 数据库表依赖

本工作流依赖以下数据库表：

- **products**: 商品信息表
- **inventory**: 库存表
- **customers**: 客户表
- **orders**: 订单表
- **order_items**: 订单明细表

## 集成服务

- **数据库集成**: PostgreSQL数据库操作
- **对象存储集成**: 小票文件存储
- **邮件集成**: 发送小票邮件

## 测试

运行测试脚本：

```bash
export PYTHONPATH=/workspace/projects/src
python scripts/test_pos_standalone.py
```

## 注意事项

1. **库存扣减**: 确保商品库存充足后再进行销售
2. **客户识别**: 结账时可以关联客户ID，享受会员折扣和积分
3. **邮件发送**: 需要正确配置邮件集成才能发送小票邮件
4. **小票存储**: 小票文件会自动上传到对象存储，并提供下载链接

## 后续优化建议

1. 添加商品搜索功能（支持按名称、作者、分类搜索）
2. 支持退货和换货流程
3. 添加优惠券管理功能
4. 支持多种支付方式（现金、刷卡、支付宝、微信等）
5. 添加销售报表功能
6. 支持批量导入商品

## 版本历史

- **v1.0.0** (2026-01-21): 初始版本，实现基本的扫码销售和结账功能
