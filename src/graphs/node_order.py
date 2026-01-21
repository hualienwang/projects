import os
import json
from datetime import datetime
from typing import List

from sqlalchemy.orm import Session
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_dev_sdk.database import get_session
from coze_coding_utils.runtime_ctx.context import Context
from cozeloop.decorator import observe
from coze_workload_identity import Client

from graphs.state_order import (
    ValidateOrderInput, ValidateOrderOutput,
    CheckOrderInventoryInput, CheckOrderInventoryOutput,
    CreateOrderInput, CreateOrderOutput,
    DeductInventoryInput, DeductInventoryOutput,
    GenerateShippingOrderInput, GenerateShippingOrderOutput,
    NotifyCustomerInput, NotifyCustomerOutput
)
from storage.database.shared.model import Product, Inventory, Customer, Order, OrderItem
from storage.database.product_manager import ProductManager
from storage.database.inventory_manager import InventoryManager
import uuid


# ==================== 节点1: 验证订单 ====================
def validate_order_node(
    state: ValidateOrderInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ValidateOrderOutput:
    """
    title: 验证订单
    desc: 验证客户信息和商品信息是否有效
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 验证客户
        customer = db.query(Customer).filter(Customer.id == state.customer_id).first()
        if not customer:
            return ValidateOrderOutput(
                is_valid=False,
                validated_items=[],
                total_amount=0.0,
                message=f"客户ID {state.customer_id} 不存在"
            )
        
        # 验证商品并计算总价
        validated_items = []
        total_amount = 0.0
        
        for item in state.items:
            product = db.query(Product).filter(
                Product.id == item.get("product_id"),
                Product.is_active == True
            ).first()
            
            if not product:
                return ValidateOrderOutput(
                    is_valid=False,
                    validated_items=[],
                    total_amount=0.0,
                    message=f"商品ID {item.get('product_id')} 不存在或已下架"
                )
            
            quantity = item.get("quantity", 1)
            if quantity <= 0:
                return ValidateOrderOutput(
                    is_valid=False,
                    validated_items=[],
                    total_amount=0.0,
                    message=f"商品 {product.name} 的数量必须大于0"
                )
            
            item_total = float(product.price) * quantity
            total_amount += item_total
            
            validated_items.append({
                "product_id": product.id,
                "name": product.name,
                "quantity": quantity,
                "unit_price": float(product.price),
                "subtotal": item_total
            })
        
        return ValidateOrderOutput(
            is_valid=True,
            validated_items=validated_items,
            items=validated_items,
            total_amount=total_amount,
            message="订单验证成功"
        )
    finally:
        db.close()


# ==================== 节点2: 检查库存 ====================
def check_order_inventory_node(
    state: CheckOrderInventoryInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CheckOrderInventoryOutput:
    """
    title: 检查库存
    desc: 检查订单商品库存是否充足
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        inventory_mgr = InventoryManager()
        all_sufficient = True
        check_details = []
        
        for item in state.items:
            inventory = inventory_mgr.get_inventory_by_product_id(db, item.get("product_id"))
            
            if not inventory:
                all_sufficient = False
                check_details.append({
                    "product_id": item.get("product_id"),
                    "available": 0,
                    "requested": item.get("quantity"),
                    "sufficient": False,
                    "message": "商品库存记录不存在"
                })
                continue
            
            requested_qty = item.get("quantity", 1)
            available_qty = inventory.quantity
            is_sufficient = available_qty >= requested_qty
            
            if not is_sufficient:
                all_sufficient = False
            
            check_details.append({
                "product_id": item.get("product_id"),
                "available": available_qty,
                "requested": requested_qty,
                "sufficient": is_sufficient,
                "shortage": max(0, requested_qty - available_qty) if not is_sufficient else 0
            })
        
        # 判断库存状态
        if all_sufficient:
            inventory_status = "sufficient"
            message = "所有商品库存充足"
        else:
            inventory_status = "insufficient"
            message = "部分商品库存不足"
        
        return CheckOrderInventoryOutput(
            inventory_status=inventory_status,
            inventory_check_result={
                "details": check_details,
                "all_sufficient": all_sufficient
            },
            items=state.items,
            message=message
        )
    finally:
        db.close()


# ==================== 节点3: 创建订单 ====================
def create_order_node(
    state: CreateOrderInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CreateOrderOutput:
    """
    title: 创建订单
    desc: 在数据库中创建订单和订单明细
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 生成订单号
        order_no = f"ORD{datetime.now().strftime('%Y%m%d%H%M%S')}{str(uuid.uuid4())[:8]}"
        
        # 创建订单
        order = Order(
            order_no=order_no,
            customer_id=state.customer_id,
            total_amount=state.total_amount,
            status="pending"
        )
        db.add(order)
        db.flush()  # 获取 order.id
        
        # 创建订单明细
        for item in state.items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.get("product_id"),
                quantity=item.get("quantity"),
                unit_price=item.get("unit_price"),
                subtotal=item.get("subtotal")
            )
            db.add(order_item)
        
        db.commit()
        db.refresh(order)
        
        return CreateOrderOutput(
            order_no=order_no,
            order_id=order.id,
            order_created=True,
            message="订单创建成功",
            status="success"
        )
    except Exception as e:
        db.rollback()
        return CreateOrderOutput(
            order_no="",
            order_id=0,
            order_created=False,
            message=f"订单创建失败: {str(e)}"
        )
    finally:
        db.close()


# ==================== 节点4: 扣减库存 ====================
def deduct_inventory_node(
    state: DeductInventoryInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> DeductInventoryOutput:
    """
    title: 扣减库存
    desc: 根据订单商品数量扣减对应库存
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        inventory_mgr = InventoryManager()
        updated_items = []
        
        for item in state.items:
            try:
                # 扣减库存（负数表示减）
                inventory = inventory_mgr.adjust_inventory_quantity(
                    db,
                    item.get("product_id"),
                    -item.get("quantity")
                )
                
                updated_items.append({
                    "product_id": item.get("product_id"),
                    "old_quantity": inventory.quantity + item.get("quantity"),
                    "new_quantity": inventory.quantity
                })
            except Exception as e:
                return DeductInventoryOutput(
                    inventory_updated=False,
                    updated_items=[],
                    message=f"扣减库存失败: {str(e)}"
                )
        
        db.commit()
        
        return DeductInventoryOutput(
            inventory_updated=True,
            updated_items=updated_items,
            message="库存扣减成功"
        )
    except Exception as e:
        db.rollback()
        return DeductInventoryOutput(
            inventory_updated=False,
            updated_items=[],
            message=f"库存扣减失败: {str(e)}"
        )
    finally:
        db.close()


# ==================== 节点5: 生成发货单 ====================
def generate_shipping_order_node(
    state: GenerateShippingOrderInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GenerateShippingOrderOutput:
    """
    title: 生成发货单
    desc: 根据订单信息生成发货单
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 获取客户信息
        customer = db.query(Customer).filter(Customer.id == state.customer_id).first()
        
        # 生成发货单
        shipping_order = {
            "shipping_no": f"SHIP{state.order_no[3:]}",
            "order_no": state.order_no,
            "customer_name": customer.name if customer else "未知",
            "customer_phone": customer.phone if customer else "",
            "items": state.items,
            "shipping_date": datetime.now().isoformat(),
            "status": "pending"
        }
        
        return GenerateShippingOrderOutput(shipping_order=shipping_order)
    finally:
        db.close()


# ==================== 节点6: 通知客户 ====================
@observe
def notify_customer_node(
    state: NotifyCustomerInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> NotifyCustomerOutput:
    """
    title: 通知客户
    desc: 通过邮件通知客户订单处理结果
    integrations: 邮件
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 获取客户信息
        customer = db.query(Customer).filter(Customer.id == state.customer_id).first()
        
        if not customer or not bool(customer.email):
            return NotifyCustomerOutput(
                notified=False,
                message="客户邮箱不存在，无法发送通知"
            )
        
        # 获取邮件配置
        client_obj = Client()
        email_credential = client_obj.get_integration_credential("integration-email-imap-smtp")
        email_config = json.loads(email_credential)
        
        import smtplib
        import ssl
        from email.mime.text import MIMEText
        from email.header import Header
        from email.utils import formataddr, formatdate, make_msgid
        
        # 构建邮件内容
        if state.status == "success":
            subject = f"订单确认 - {state.order_no}"
            content = f"""
尊敬的 {customer.name}：

您的订单 {state.order_no} 已成功创建，我们将尽快为您发货。

订单详情：
- 订单号：{state.order_no}
- 订单状态：待发货
- 下单时间：{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

感谢您的购买！

瓊林圖書事業有限公司
"""
        else:
            subject = f"订单处理通知 - {state.order_no}"
            content = f"""
尊敬的 {customer.name}：

您的订单 {state.order_no} 处理过程中遇到问题，我们将尽快与您联系。

订单状态：{state.status}

瓊林圖書事業有限公司
"""
        
        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = formataddr(("订单系统", email_config["account"]))
        msg["To"] = customer.email
        msg["Subject"] = Header(subject, "utf-8")
        msg["Date"] = formatdate(localtime=True)
        msg["Message-ID"] = make_msgid()
        
        # 发送邮件
        ctx_ssl = ssl.create_default_context()
        ctx_ssl.minimum_version = ssl.TLSVersion.TLSv1_2
        
        with smtplib.SMTP_SSL(
            email_config["smtp_server"],
            email_config["smtp_port"],
            context=ctx_ssl,
            timeout=30
        ) as server:
            server.ehlo()
            server.login(email_config["account"], email_config["auth_code"])
            server.sendmail(
                email_config["account"],
                [customer.email],
                msg.as_string()
            )
            server.quit()
        
        return NotifyCustomerOutput(
            notified=True,
            message=f"已发送邮件通知到 {customer.email}"
        )
    except Exception as e:
        return NotifyCustomerOutput(
            notified=False,
            message=f"发送通知失败: {str(e)}"
        )
    finally:
        db.close()
