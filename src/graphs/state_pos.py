from typing import Optional, List
from pydantic import BaseModel, Field

# ==================== 全局状态 ====================
class POSGlobalState(BaseModel):
    """POS系统全局状态"""
    action: str = Field(default="", description="操作类型: scan/checkout")
    scanned_code: str = Field(default="", description="扫描的条码或ISBN")
    product_info: dict = Field(default={}, description="识别到的商品信息")
    cart_items: List[dict] = Field(default=[], description="购物车商品列表")
    inventory_check_result: dict = Field(default={}, description="库存检查结果")
    customer_info: dict = Field(default={}, description="客户信息")
    order_summary: dict = Field(default={}, description="订单汇总信息")
    payment_result: dict = Field(default={}, description="支付结果")
    receipt_url: str = Field(default="", description="小票文件URL")
    email_sent: bool = Field(default=False, description="邮件是否已发送")
    error_message: str = Field(default="", description="错误信息")

# ==================== 图输入输出 ====================
class POSGraphInput(BaseModel):
    """POS工作流输入"""
    action: str = Field(..., description="操作类型: scan/add/remove/checkout")
    scanned_code: str = Field(default="", description="扫描的条码或ISBN")
    product_id: Optional[int] = Field(default=None, description="商品ID")
    customer_id: Optional[int] = Field(default=None, description="客户ID")
    cart_items: Optional[List[dict]] = Field(default=[], description="购物车商品列表")

class POSGraphOutput(BaseModel):
    """POS工作流输出"""
    success: bool = Field(..., description="操作是否成功")
    result: dict = Field(..., description="操作结果")
    error_message: str = Field(default="", description="错误信息")

# ==================== 节点输入输出定义 ====================

# 1. 扫码识别节点
class ScanProductInput(BaseModel):
    """扫码识别节点输入"""
    scanned_code: Optional[str] = Field(default="", description="扫描的条码或ISBN")
    action: str = Field(..., description="操作类型")

class ScanProductOutput(BaseModel):
    """扫码识别节点输出"""
    product_info: dict = Field(..., description="识别到的商品信息")
    found: bool = Field(..., description="是否找到商品")

# 2. 库存检查节点
class CheckInventoryInput(BaseModel):
    """库存检查节点输入"""
    product_info: dict = Field(..., description="商品信息")
    quantity: int = Field(default=1, description="需要购买的数量")

class CheckInventoryOutput(BaseModel):
    """库存检查节点输出"""
    inventory_available: bool = Field(..., description="库存是否充足")
    current_stock: int = Field(..., description="当前库存数量")
    shortage: int = Field(default=0, description="缺少数量")

# 3. 添加购物车节点
class AddToCartInput(BaseModel):
    """添加购物车节点输入"""
    product_info: dict = Field(..., description="商品信息")
    quantity: int = Field(default=1, description="数量")
    cart_items: List[dict] = Field(default=[], description="当前购物车")

class AddToCartOutput(BaseModel):
    """添加购物车节点输出"""
    cart_items: List[dict] = Field(..., description="更新后的购物车")
    added: bool = Field(..., description="是否成功添加")

# 4. 订单汇总节点
class CalculateOrderInput(BaseModel):
    """订单汇总节点输入"""
    cart_items: List[dict] = Field(..., description="购物车商品列表")
    customer_id: Optional[int] = Field(default=None, description="客户ID")

class CalculateOrderOutput(BaseModel):
    """订单汇总节点输出"""
    order_summary: dict = Field(..., description="订单汇总信息")
    customer_info: dict = Field(default={}, description="客户信息")

# 5. 创建订单节点
class CreateOrderInput(BaseModel):
    """创建订单节点输入"""
    order_summary: dict = Field(..., description="订单汇总信息")
    customer_id: Optional[int] = Field(default=None, description="客户ID")

class CreateOrderOutput(BaseModel):
    """创建订单节点输出"""
    order_id: int = Field(..., description="订单ID")
    order_no: str = Field(..., description="订单编号")
    success: bool = Field(..., description="创建是否成功")

# 6. 扣减库存节点
class DeductInventoryInput(BaseModel):
    """扣减库存节点输入"""
    cart_items: List[dict] = Field(..., description="购物车商品列表")

class DeductInventoryOutput(BaseModel):
    """扣减库存节点输出"""
    success: bool = Field(..., description="扣减是否成功")
    updated_products: List[dict] = Field(default=[], description="更新的商品列表")

# 7. 生成小票节点
class GenerateReceiptInput(BaseModel):
    """生成小票节点输入"""
    order_summary: dict = Field(..., description="订单汇总信息")
    order_no: str = Field(..., description="订单编号")
    customer_info: dict = Field(default={}, description="客户信息")

class GenerateReceiptOutput(BaseModel):
    """生成小票节点输出"""
    receipt_url: str = Field(..., description="小票文件URL")
    receipt_content: str = Field(..., description="小票内容文本")

# 8. 发送邮件节点
class SendEmailInput(BaseModel):
    """发送邮件节点输入"""
    receipt_url: str = Field(..., description="小票文件URL")
    customer_email: str = Field(default="", description="客户邮箱")
    order_no: str = Field(..., description="订单编号")

class SendEmailOutput(BaseModel):
    """发送邮件节点输出"""
    email_sent: bool = Field(..., description="邮件是否发送成功")
    email_address: str = Field(..., description="收件人邮箱地址")

# 9. 操作判断节点
class ActionCheckInput(BaseModel):
    """操作判断节点输入"""
    action: str = Field(..., description="操作类型")
