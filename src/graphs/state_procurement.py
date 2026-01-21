from typing import Literal, Optional, List
from pydantic import BaseModel, Field


# ==================== 全局状态 ====================
class ProcurementGlobalState(BaseModel):
    """供应商采购管理工作流的全局状态"""
    low_stock_products: List[dict] = Field(default=[], description="库存不足商品")
    procurement_plan: List[dict] = Field(default=[], description="采购计划")
    total_cost: float = Field(default=0.0, description="采购总成本")
    supplier_recommendations: dict = Field(default={}, description="供应商推荐")
    procurement_order: dict = Field(default={}, description="采购单")
    order_sent: bool = Field(default=False, description="采购单是否已发送")


# ==================== 工作流输入输出 ====================
class ProcurementInput(BaseModel):
    """供应商采购管理工作流输入"""
    check_all_low_stock: bool = Field(default=True, description="是否检查所有低库存商品")
    product_ids: Optional[List[int]] = Field(default=None, description="指定商品ID列表（可选）")


class ProcurementOutput(BaseModel):
    """供应商采购管理工作流输出"""
    total_products: int = Field(..., description="采购商品数量")
    total_cost: float = Field(..., description="采购总成本")
    procurement_order_no: str = Field(..., description="采购单号")
    order_sent: bool = Field(..., description="采购单是否发送")
    message: str = Field(..., description="处理消息")


# ==================== 节点输入输出 ====================

# 节点1: 识别采购需求
class IdentifyProcurementNeedsInput(BaseModel):
    """识别采购需求节点输入"""
    check_all_low_stock: bool = Field(..., description="是否检查所有低库存商品")
    product_ids: Optional[List[int]] = Field(None, description="指定商品ID列表")


class IdentifyProcurementNeedsOutput(BaseModel):
    """识别采购需求节点输出"""
    low_stock_products: List[dict] = Field(..., description="库存不足商品")


# 节点2: 生成采购计划
class GenerateProcurementPlanInput(BaseModel):
    """生成采购计划节点输入"""
    low_stock_products: List[dict] = Field(..., description="库存不足商品")


class GenerateProcurementPlanOutput(BaseModel):
    """生成采购计划节点输出"""
    procurement_plan: List[dict] = Field(..., description="采购计划")
    total_cost: float = Field(..., description="采购总成本")


# 节点3: 推荐供应商
class RecommendSuppliersInput(BaseModel):
    """推荐供应商节点输入"""
    procurement_plan: List[dict] = Field(..., description="采购计划")


class RecommendSuppliersOutput(BaseModel):
    """推荐供应商节点输出"""
    supplier_recommendations: dict = Field(..., description="供应商推荐")


# 节点4: 生成采购单
class GenerateProcurementOrderInput(BaseModel):
    """生成采购单节点输入"""
    procurement_plan: List[dict] = Field(..., description="采购计划")
    supplier_recommendations: dict = Field(..., description="供应商推荐")


class GenerateProcurementOrderOutput(BaseModel):
    """生成采购单节点输出"""
    procurement_order: dict = Field(..., description="采购单")


# 节点5: 发送采购单
class SendProcurementOrderInput(BaseModel):
    """发送采购单节点输入"""
    procurement_order: dict = Field(..., description="采购单")


class SendProcurementOrderOutput(BaseModel):
    """发送采购单节点输出"""
    order_sent: bool = Field(..., description="采购单是否发送")
    message: str = Field(default="", description="发送消息")
