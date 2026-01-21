import os
import json
from datetime import datetime
from typing import List
from decimal import Decimal

from sqlalchemy.orm import Session
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_dev_sdk.database import get_session
from coze_coding_dev_sdk.s3 import S3SyncStorage
from coze_coding_utils.runtime_ctx.context import Context
from cozeloop.decorator import observe
from coze_workload_identity import Client
from jinja2 import Template

from graphs.state_pos import (
    ScanProductInput, ScanProductOutput,
    CheckInventoryInput, CheckInventoryOutput,
    AddToCartInput, AddToCartOutput,
    CalculateOrderInput, CalculateOrderOutput,
    CreateOrderInput, CreateOrderOutput,
    DeductInventoryInput, DeductInventoryOutput,
    GenerateReceiptInput, GenerateReceiptOutput,
    SendEmailInput, SendEmailOutput,
    ActionCheckInput
)
from storage.database.shared.model import Product, Inventory, Customer, Order, OrderItem
from storage.database.product_manager import ProductManager
from storage.database.inventory_manager import InventoryManager
import uuid


# ==================== 节点1: 扫码识别商品 ====================
def scan_product_node(
    state: ScanProductInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ScanProductOutput:
    """
    title: 扫码识别商品
    desc: 根据条码或ISBN识别商品信息（如果是结账操作则跳过）
    integrations: 数据库
    """
    ctx = runtime.context
    
    # 如果是结账操作，直接返回空结果
    if state.action == "checkout":
        return ScanProductOutput(
            product_info={},
            found=False
        )
    
    db = get_session()
    
    try:
        # 查询商品：优先匹配条形码，然后是ISBN
        product = db.query(Product).filter(
            (Product.barcode == state.scanned_code) | (Product.isbn == state.scanned_code)
        ).first()
        
        if product and bool(product.is_active):
            product_info = {
                "id": product.id,
                "isbn": product.isbn,
                "name": product.name,
                "author": product.author,
                "publisher": product.publisher,
                "category": product.category,
                "price": float(product.price),
                "barcode": product.barcode
            }
            return ScanProductOutput(
                product_info=product_info,
                found=True
            )
        else:
            return ScanProductOutput(
                product_info={},
                found=False
            )
    finally:
        db.close()


# ==================== 节点2: 检查库存 ====================
def check_inventory_node(
    state: CheckInventoryInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CheckInventoryOutput:
    """
    title: 检查库存
    desc: 检查商品库存是否充足
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        product_id = state.product_info.get("id")
        quantity = state.quantity
        
        inventory = db.query(Inventory).filter(
            Inventory.product_id == product_id
        ).first()
        
        if not inventory:
            return CheckInventoryOutput(
                inventory_available=False,
                current_stock=0,
                shortage=quantity
            )
        
        current_stock = int(inventory.quantity)
        if current_stock >= quantity:
            return CheckInventoryOutput(
                inventory_available=True,
                current_stock=current_stock,
                shortage=0
            )
        else:
            shortage = quantity - current_stock
            return CheckInventoryOutput(
                inventory_available=False,
                current_stock=current_stock,
                shortage=shortage
            )
    finally:
        db.close()


# ==================== 节点3: 添加到购物车 ====================
def add_to_cart_node(
    state: AddToCartInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> AddToCartOutput:
    """
    title: 添加到购物车
    desc: 将商品添加到购物车
    integrations: 
    """
    ctx = runtime.context
    
    cart_items = state.cart_items.copy()
    product_id = state.product_info.get("id")
    quantity = state.quantity
    
    # 检查购物车中是否已有该商品
    found = False
    for item in cart_items:
        if item.get("product_id") == product_id:
            item["quantity"] += quantity
            item["subtotal"] = float(item["unit_price"]) * item["quantity"]
            found = True
            break
    
    if not found:
        cart_item = {
            "product_id": product_id,
            "name": state.product_info.get("name"),
            "author": state.product_info.get("author"),
            "isbn": state.product_info.get("isbn"),
            "quantity": quantity,
            "unit_price": state.product_info.get("price"),
            "subtotal": state.product_info.get("price") * quantity
        }
        cart_items.append(cart_item)
    
    return AddToCartOutput(
        cart_items=cart_items,
        added=True
    )


# ==================== 节点4: 订单汇总 ====================
def calculate_order_node(
    state: CalculateOrderInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CalculateOrderOutput:
    """
    title: 订单汇总
    desc: 计算订单总价、折扣、积分等信息
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 计算订单总价
        total_amount = sum(item.get("subtotal", 0) for item in state.cart_items)
        
        # 获取客户信息（如果有）
        customer_info = {}
        if state.customer_id:
            customer = db.query(Customer).filter(Customer.id == state.customer_id).first()
            if customer:
                customer_info = {
                    "id": customer.id,
                    "name": customer.name,
                    "phone": customer.phone,
                    "email": customer.email,
                    "level": customer.level,
                    "points": customer.points,
                    "total_purchase": float(customer.total_purchase)
                }
        
        # 计算积分（1元=1积分）
        points_earned = int(total_amount)
        
        # 计算会员折扣
        discount = 0.0
        discount_reason = ""
        
        if customer_info:
            level = customer_info.get("level", "普通会员")
            if level == "黄金会员":
                discount = total_amount * 0.1  # 10%折扣
                discount_reason = "黄金会员10%折扣"
            elif level == "钻石会员":
                discount = total_amount * 0.15  # 15%折扣
                discount_reason = "钻石会员15%折扣"
        
        final_amount = total_amount - discount
        
        order_summary = {
            "items": state.cart_items,
            "total_amount": total_amount,
            "discount": discount,
            "discount_reason": discount_reason,
            "final_amount": final_amount,
            "points_earned": points_earned,
            "item_count": len(state.cart_items)
        }
        
        return CalculateOrderOutput(
            order_summary=order_summary,
            customer_info=customer_info
        )
    finally:
        db.close()


# ==================== 节点5: 创建订单 ====================
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
        order_no = f"POS{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:6].upper()}"
        
        # 创建订单
        order = Order(
            order_no=order_no,
            customer_id=state.customer_id,
            total_amount=Decimal(str(state.order_summary.get("final_amount", 0))),
            status="completed",
            payment_method="cash"
        )
        
        db.add(order)
        db.flush()  # 获取订单ID
        
        # 创建订单明细
        for item in state.order_summary.get("items", []):
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.get("product_id"),
                quantity=item.get("quantity"),
                unit_price=Decimal(str(item.get("unit_price", 0))),
                subtotal=Decimal(str(item.get("subtotal", 0)))
            )
            db.add(order_item)
        
        # 更新客户累计消费和积分
        if state.customer_id:
            customer = db.query(Customer).filter(Customer.id == state.customer_id).first()
            if customer is not None:
                # 使用setattr更新属性
                current_purchase = float(customer.total_purchase) if bool(customer.total_purchase) else 0
                final_amount = state.order_summary.get("final_amount", 0)
                setattr(customer, "total_purchase", Decimal(str(current_purchase + final_amount)))
                
                current_points = int(customer.points) if bool(customer.points) else 0
                points_earned = state.order_summary.get("points_earned", 0)
                setattr(customer, "points", current_points + points_earned)
                
                setattr(customer, "last_purchase_date", datetime.now())
        
        db.commit()
        
        return CreateOrderOutput(
            order_id=order.id,
            order_no=order_no,
            success=True
        )
    except Exception as e:
        db.rollback()
        return CreateOrderOutput(
            order_id=0,
            order_no="",
            success=False
        )
    finally:
        db.close()


# ==================== 节点6: 扣减库存 ====================
def deduct_inventory_node(
    state: DeductInventoryInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> DeductInventoryOutput:
    """
    title: 扣减库存
    desc: 根据订单扣减商品库存
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        updated_products = []
        success = True
        
        for item in state.cart_items:
            product_id = item.get("product_id")
            quantity = item.get("quantity")
            
            if quantity is None:
                quantity = 1
            
            inventory = db.query(Inventory).filter(
                Inventory.product_id == product_id
            ).first()
            
            if inventory is not None:
                current_qty = int(inventory.quantity)
                new_quantity = current_qty - quantity
                if new_quantity < 0:
                    success = False
                    break
                
                setattr(inventory, "quantity", new_quantity)
                updated_products.append({
                    "product_id": product_id,
                    "old_quantity": current_qty,
                    "new_quantity": new_quantity
                })
            else:
                success = False
                break
        
        if success:
            db.commit()
            return DeductInventoryOutput(
                success=True,
                updated_products=updated_products
            )
        else:
            db.rollback()
            return DeductInventoryOutput(
                success=False,
                updated_products=[]
            )
    except Exception as e:
        db.rollback()
        return DeductInventoryOutput(
            success=False,
            updated_products=[]
        )
    finally:
        db.close()


# ==================== 节点7: 生成小票 ====================
def generate_receipt_node(
    state: GenerateReceiptInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GenerateReceiptOutput:
    """
    title: 生成小票
    desc: 生成销售小票并上传到对象存储
    integrations: 对象存储
    """
    ctx = runtime.context
    
    try:
        # 初始化对象存储
        storage = S3SyncStorage(
            endpoint_url=os.getenv("COZE_BUCKET_ENDPOINT_URL"),
            access_key="",
            secret_key="",
            bucket_name=os.getenv("COZE_BUCKET_NAME"),
            region="cn-beijing"
        )
        
        # 生成小票内容
        receipt_lines = [
            "=" * 50,
            "        瓊林圖書事業有限公司",
            "              销售小票",
            "=" * 50,
            f"订单号: {state.order_no}",
            f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            "-" * 50,
            "商品明细:",
        ]
        
        # 添加商品明细
        for item in state.order_summary.get("items", []):
            receipt_lines.append(f"{item.get('name')}")
            receipt_lines.append(f"  单价: {item.get('unit_price'):.2f}  数量: {item.get('quantity')}  小计: {item.get('subtotal'):.2f}")
        
        receipt_lines.append("-" * 50)
        receipt_lines.append(f"商品总数: {state.order_summary.get('item_count', 0)}")
        receipt_lines.append(f"总金额: {state.order_summary.get('total_amount', 0):.2f}")
        
        # 添加折扣信息
        discount = state.order_summary.get('discount', 0)
        if discount > 0:
            receipt_lines.append(f"折扣: -{discount:.2f} ({state.order_summary.get('discount_reason', '')})")
        
        receipt_lines.append("-" * 50)
        receipt_lines.append(f"实付金额: {state.order_summary.get('final_amount', 0):.2f}")
        receipt_lines.append(f"获得积分: {state.order_summary.get('points_earned', 0)}")
        
        # 添加客户信息
        if state.customer_info:
            receipt_lines.append("-" * 50)
            receipt_lines.append(f"客户: {state.customer_info.get('name', '散客')}")
            if state.customer_info.get('phone'):
                receipt_lines.append(f"电话: {state.customer_info.get('phone')}")
        
        receipt_lines.append("=" * 50)
        receipt_lines.append("      感谢您的光临，欢迎再次光临！")
        receipt_lines.append("=" * 50)
        
        receipt_content = "\n".join(receipt_lines)
        
        # 生成文件名
        receipt_filename = f"receipt_{state.order_no}.txt"
        
        # 上传到对象存储
        receipt_key = storage.upload_file(
            file_content=receipt_content.encode('utf-8'),
            file_name=receipt_filename,
            content_type='text/plain'
        )
        
        # 生成签名URL
        receipt_url = storage.generate_presigned_url(key=receipt_key, expire_time=3600)
        
        return GenerateReceiptOutput(
            receipt_url=receipt_url,
            receipt_content=receipt_content
        )
    except Exception as e:
        # 发生错误时返回文本内容
        return GenerateReceiptOutput(
            receipt_url="",
            receipt_content=f"生成小票失败: {str(e)}"
        )


# ==================== 节点8: 发送邮件 ====================
@observe
def send_email_node(
    state: SendEmailInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SendEmailOutput:
    """
    title: 发送邮件
    desc: 发送小票邮件给客户
    integrations: 邮件
    """
    ctx = runtime.context
    
    # 如果没有客户邮箱，跳过发送
    if not state.customer_email:
        return SendEmailOutput(
            email_sent=False,
            email_address=""
        )
    
    try:
        import smtplib
        import ssl
        from email.mime.text import MIMEText
        from email.header import Header
        from email.utils import formataddr, formatdate, make_msgid
        
        # 获取邮件配置
        client = Client()
        email_credential = client.get_integration_credential("integration-email-imap-smtp")
        email_config = json.loads(email_credential)
        
        # 准备邮件内容
        subject = f"瓊林圖書 - 订单小票 {state.order_no}"
        html_content = f"""
        <html>
        <head>
            <meta charset="UTF-8">
        </head>
        <body>
            <h2>瓊林圖書事業有限公司 - 销售小票</h2>
            <p>订单号: {state.order_no}</p>
            <p>时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            <hr>
            <p>您的销售小票已生成，请点击以下链接查看：</p>
            <p><a href="{state.receipt_url}">{state.receipt_url}</a></p>
            <hr>
            <p>感谢您的光临，欢迎再次光临！</p>
        </body>
        </html>
        """
        
        # 创建邮件对象
        msg = MIMEText(html_content, "html", "utf-8")
        msg["From"] = formataddr(("瓊林圖書", email_config["account"]))
        msg["To"] = state.customer_email
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
            server.sendmail(email_config["account"], [state.customer_email], msg.as_string())
            server.quit()
        
        return SendEmailOutput(
            email_sent=True,
            email_address=state.customer_email
        )
    except Exception as e:
        return SendEmailOutput(
            email_sent=False,
            email_address=state.customer_email
        )


# ==================== 条件节点: 操作判断 ====================
def action_check_node(state: ActionCheckInput) -> str:
    """
    title: 操作判断
    desc: 根据操作类型决定后续流程
    """
    action = state.action.lower()
    
    if action == "scan":
        return "扫码识别"
    elif action == "checkout":
        return "结账处理"
    else:
        return "其他操作"
