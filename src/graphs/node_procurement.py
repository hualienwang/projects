import os
import json
from datetime import datetime
from typing import List
import uuid

from sqlalchemy.orm import Session
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_dev_sdk.database import get_session
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state_procurement import (
    IdentifyProcurementNeedsInput, IdentifyProcurementNeedsOutput,
    GenerateProcurementPlanInput, GenerateProcurementPlanOutput,
    RecommendSuppliersInput, RecommendSuppliersOutput,
    GenerateProcurementOrderInput, GenerateProcurementOrderOutput,
    SendProcurementOrderInput, SendProcurementOrderOutput
)
from storage.database.shared.model import Product, Inventory, Supplier


# ==================== 节点1: 识别采购需求 ====================
def identify_procurement_needs_node(
    state: IdentifyProcurementNeedsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> IdentifyProcurementNeedsOutput:
    """
    title: 识别采购需求
    desc: 检查库存不足商品，识别采购需求
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        low_stock_products = []
        
        if state.check_all_low_stock:
            # 检查所有低库存商品
            inventories = db.query(Inventory).join(Product).filter(
                Inventory.quantity < Inventory.min_stock_threshold
            ).all()
            
            for inv in inventories:
                low_stock_products.append({
                    "product_id": inv.product_id,
                    "name": inv.product.name,
                    "isbn": inv.product.isbn,
                    "current_quantity": inv.quantity,
                    "min_threshold": inv.min_stock_threshold,
                    "reorder_quantity": inv.reorder_quantity,
                    "shortage": inv.min_stock_threshold - inv.quantity,
                    "cost": float(inv.product.cost) if inv.product.cost else 0
                })
        elif state.product_ids:
            # 检查指定商品
            for product_id in state.product_ids:
                inv = db.query(Inventory).filter(Inventory.product_id == product_id).first()
                if inv and int(inv.quantity) < int(inv.min_stock_threshold):
                    product = db.query(Product).filter(Product.id == product_id).first()
                    low_stock_products.append({
                        "product_id": inv.product_id,
                        "name": product.name if product else "N/A",
                        "isbn": product.isbn if product else "N/A",
                        "current_quantity": inv.quantity,
                        "min_threshold": inv.min_stock_threshold,
                        "reorder_quantity": inv.reorder_quantity,
                        "shortage": inv.min_stock_threshold - inv.quantity,
                        "cost": float(inv.product.cost) if inv.product and inv.product.cost else 0
                    })
        
        return IdentifyProcurementNeedsOutput(low_stock_products=low_stock_products)
    finally:
        db.close()


# ==================== 节点2: 生成采购计划 ====================
def generate_procurement_plan_node(
    state: GenerateProcurementPlanInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GenerateProcurementPlanOutput:
    """
    title: 生成采购计划
    desc: 根据库存预警生成详细的采购计划
    integrations:
    """
    ctx = runtime.context
    
    procurement_plan = []
    total_cost = 0.0
    
    for product in state.low_stock_products:
        # 采购数量 = 建议补货量 + 安全库存（20%）
        order_quantity = int(product["reorder_quantity"] * 1.2)
        item_cost = order_quantity * product["cost"]
        total_cost += item_cost
        
        procurement_plan.append({
            "product_id": product["product_id"],
            "name": product["name"],
            "isbn": product["isbn"],
            "order_quantity": order_quantity,
            "unit_cost": product["cost"],
            "item_cost": item_cost,
            "priority": "高" if product["shortage"] > 5 else "中"
        })
    
    # 按优先级排序
    procurement_plan.sort(key=lambda x: x["priority"], reverse=True)
    
    return GenerateProcurementPlanOutput(
        procurement_plan=procurement_plan,
        total_cost=total_cost
    )


# ==================== 节点3: 推荐供应商 ====================
def recommend_suppliers_node(
    state: RecommendSuppliersInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> RecommendSuppliersOutput:
    """
    title: 推荐供应商
    desc: 为采购计划推荐最优供应商
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 获取所有供应商
        suppliers = db.query(Supplier).filter(Supplier.is_active == True).all()
        
        supplier_recommendations = {}
        
        for supplier in suppliers:
            supplier_info = {
                "supplier_id": supplier.id,
                "name": supplier.name,
                "contact_person": supplier.contact_person,
                "phone": supplier.phone,
                "email": supplier.email,
                "address": supplier.address
            }
            supplier_recommendations[f"supplier_{supplier.id}"] = supplier_info
        
        # 如果有供应商，选择第一个作为默认供应商
        if suppliers:
            primary_supplier = suppliers[0]
            supplier_recommendations["primary"] = {
                "supplier_id": primary_supplier.id,
                "name": primary_supplier.name,
                "contact_person": primary_supplier.contact_person,
                "phone": primary_supplier.phone,
                "email": primary_supplier.email
            }
        
        return RecommendSuppliersOutput(
            supplier_recommendations=supplier_recommendations
        )
    finally:
        db.close()


# ==================== 节点4: 生成采购单 ====================
def generate_procurement_order_node(
    state: GenerateProcurementOrderInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GenerateProcurementOrderOutput:
    """
    title: 生成采购单
    desc: 生成正式的采购单
    integrations:
    """
    ctx = runtime.context
    
    # 生成采购单号
    order_no = f"PO{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8]}"
    
    primary_supplier = state.supplier_recommendations.get("primary", {})
    
    procurement_order = {
        "order_no": order_no,
        "supplier": primary_supplier,
        "items": state.procurement_plan,
        "total_cost": state.procurement_plan[0]["item_cost"] if state.procurement_plan else 0,
        "order_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "status": "pending",
        "estimated_delivery": "7-14天"
    }
    
    # 计算总成本
    total_cost = sum(item["item_cost"] for item in state.procurement_plan)
    procurement_order["total_cost"] = total_cost
    
    return GenerateProcurementOrderOutput(
        procurement_order=procurement_order
    )


# ==================== 节点5: 发送采购单 ====================
def send_procurement_order_node(
    state: SendProcurementOrderInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SendProcurementOrderOutput:
    """
    title: 发送采购单
    desc: 将采购单发送给供应商（模拟）
    integrations:
    """
    ctx = runtime.context
    
    # 模拟发送采购单
    order = state.procurement_order
    supplier = order.get("supplier", {})
    
    # 生成采购单内容
    order_content = f"""
采购单号: {order['order_no']}
供应商: {supplier.get('name', 'N/A')}
联系人: {supplier.get('contact_person', 'N/A')}
电话: {supplier.get('phone', 'N/A')}
邮箱: {supplier.get('email', 'N/A')}

采购商品:
"""
    
    for item in order.get("items", []):
        order_content += f"""
- 商品名称: {item['name']}
  ISBN: {item['isbn']}
  采购数量: {item['order_quantity']}
  单价: ¥{item['unit_cost']:.2f}
  小计: ¥{item['item_cost']:.2f}
  优先级: {item['priority']}
"""
    
    order_content += f"""
总成本: ¥{order['total_cost']:,.2f}
下单时间: {order['order_date']}
预计交货: {order['estimated_delivery']}
"""
    
    print("\n📋 采购单详情:")
    print("=" * 80)
    print(order_content)
    print("=" * 80)
    
    return SendProcurementOrderOutput(
        order_sent=True,
        message=f"采购单 {order['order_no']} 已准备发送给 {supplier.get('name', 'N/A')}"
    )
