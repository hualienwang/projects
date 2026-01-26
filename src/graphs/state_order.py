from typing import Literal, Optional, List
from pydantic import BaseModel, Field


# ==================== 全局状态 ====================
class OrderProcessingGlobalState(BaseModel):
    """订单处理工作流的全局状态"""
    order_no: str = Field(default="", description="订单编号")
    order_id: int = Field(default=0, description="订单ID")
    customer_id: int = Field(default=0, description="客户ID")
    items: List[dict] = Field(default=[], description="订单商品列表")
    total_amount: float = Field(default=0.0, description="订单总金额")
    inventory_check_result: dict = Field(default={}, description="库存检查结果")
    inventory_status: str = Field(default="", description="库存状态: sufficient/insufficient")
    order_created: bool = Field(default=False, description="订单是否创建成功")
    inventory_updated: bool = Field(default=False, description="库存是否更新成功")
    shipping_order: dict = Field(default={}, description="发货单信息")
    order_status: str = Field(default="pending", description="订单状态")
    status: str = Field(default="failed", description="处理状态: success/partial/failed")
    message: str = Field(default="", description="处理消息")


# ==================== 工作流输入输出 ====================
class OrderProcessingInput(BaseModel):
    """订单处理工作流输入"""
    customer_id: int = Field(default=0, description="客户ID")
    items: List[dict] = Field(default=[], description="商品列表，每个元素包含 product_id 和 quantity", examples=[{"product_id": 1, "quantity": 2}])


class OrderProcessingOutput(BaseModel):
    """订单处理工作流输出"""
    order_no: str = Field(..., description="订单编号")
    status: str = Field(..., description="处理状态: success/partial/failed")
    message: str = Field(..., description="处理结果消息")
    total_amount: float = Field(..., description="订单总金额")


# ==================== 节点输入输出 ====================

# 节点1: 验证订单
class ValidateOrderInput(BaseModel):
    """验证订单节点输入"""
    customer_id: int = Field(default=0, description="客户ID")
    items: List[dict] = Field(default=[], description="商品列表")


class ValidateOrderOutput(BaseModel):
    """验证订单节点输出"""
    is_valid: bool = Field(default=False, description="订单是否有效")
    validated_items: List[dict] = Field(default=[], description="验证后的商品列表")
    items: List[dict] = Field(default=[], description="商品列表（用于后续节点）")
    total_amount: float = Field(default=0.0, description="订单总金额")
    message: str = Field(default="", description="验证消息")


# 节点2: 检查库存
class CheckOrderInventoryInput(BaseModel):
    """检查库存节点输入"""
    items: List[dict] = Field(default=[], description="商品列表")


class CheckOrderInventoryOutput(BaseModel):
    """检查库存节点输出"""
    inventory_status: str = Field(default="insufficient", description="库存状态: sufficient/insufficient/partial")
    inventory_check_result: dict = Field(default={}, description="库存检查详情")
    items: List[dict] = Field(default=[], description="商品列表（透传）")
    message: str = Field(default="", description="检查消息")


# 节点3: 创建订单
class CreateOrderInput(BaseModel):
    """创建订单节点输入"""
    customer_id: int = Field(default=0, description="客户ID")
    items: List[dict] = Field(default=[], description="商品列表")
    total_amount: float = Field(default=0.0, description="订单总金额")


class CreateOrderOutput(BaseModel):
    """创建订单节点输出"""
    order_no: str = Field(default="", description="订单编号")
    order_id: int = Field(default=0, description="订单ID")
    order_created: bool = Field(default=False, description="订单是否创建成功")
    message: str = Field(default="", description="创建消息")
    status: str = Field(default="failed", description="订单状态")


# 节点4: 扣减库存
class DeductInventoryInput(BaseModel):
    """扣减库存节点输入"""
    items: List[dict] = Field(default=[], description="商品列表")


class DeductInventoryOutput(BaseModel):
    """扣减库存节点输出"""
    inventory_updated: bool = Field(default=False, description="库存是否更新成功")
    updated_items: List[dict] = Field(default=[], description="更新的商品列表")
    message: str = Field(default="", description="更新消息")


# 节点5: 生成发货单
class GenerateShippingOrderInput(BaseModel):
    """生成发货单节点输入"""
    order_no: str = Field(default="", description="订单编号")
    items: List[dict] = Field(default=[], description="商品列表")
    customer_id: int = Field(default=0, description="客户ID")


class GenerateShippingOrderOutput(BaseModel):
    """生成发货单节点输出"""
    shipping_order: dict = Field(default={}, description="发货单信息")


# 节点6: 通知客户
class NotifyCustomerInput(BaseModel):
    """通知客户节点输入"""
    order_no: str = Field(default="", description="订单编号")
    status: str = Field(default="pending", description="订单状态")
    customer_id: int = Field(default=0, description="客户ID")


class NotifyCustomerOutput(BaseModel):
    """通知客户节点输出"""
    notified: bool = Field(default=False, description="是否通知成功")
    message: str = Field(default="", description="通知消息")
    status: str = Field(default="failed", description="订单状态")
