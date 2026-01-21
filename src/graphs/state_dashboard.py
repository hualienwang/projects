from typing import Literal, Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime, date

# ==================== 数据可视化全局状态 ====================
class DashboardGlobalState(BaseModel):
    """数据可视化工作流全局状态"""
    # 用户信息
    user_id: str = Field(default="", description="用户ID")
    user_role: str = Field(default="viewer", description="用户角色: admin/manager/staff/viewer")
    
    # 权限检查结果
    has_permission: bool = Field(default=False, description="是否有权限访问")
    permission_message: str = Field(default="", description="权限检查消息")
    
    # 图表请求参数
    chart_type: str = Field(default="", description="图表类型: sales_trend/product_ranking/inventory_distribution/customer_analysis/supplier_stats")
    start_date: Optional[date] = Field(default=None, description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")
    
    # 数据提取结果
    chart_data: Dict[str, Any] = Field(default={}, description="图表数据")
    chart_config: Dict[str, Any] = Field(default={}, description="图表配置")
    
    # 错误信息
    error_message: str = Field(default="", description="错误信息")

# ==================== 工作流输入输出 ====================
class DashboardGraphInput(BaseModel):
    """数据可视化工作流输入"""
    user_id: str = Field(..., description="用户ID")
    user_role: str = Field(default="viewer", description="用户角色: admin/manager/staff/viewer")
    chart_type: str = Field(..., description="图表类型: sales_trend/product_ranking/inventory_distribution/customer_analysis/supplier_stats")
    start_date: Optional[date] = Field(default=None, description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")

class DashboardGraphOutput(BaseModel):
    """数据可视化工作流输出"""
    has_permission: bool = Field(..., description="是否有权限访问")
    chart_data: Dict[str, Any] = Field(..., description="图表数据（Chart.js格式）")
    chart_config: Dict[str, Any] = Field(..., description="图表配置")
    message: str = Field(default="", description="处理消息")

# ==================== 权限检查节点 ====================
class PermissionCheckInput(BaseModel):
    """权限检查节点输入"""
    user_id: str = Field(..., description="用户ID")
    user_role: str = Field(..., description="用户角色")
    chart_type: str = Field(..., description="请求的图表类型")

class PermissionCheckOutput(BaseModel):
    """权限检查节点输出"""
    has_permission: bool = Field(..., description="是否有权限")
    permission_message: str = Field(default="", description="权限检查消息")

# ==================== 销售趋势数据提取节点 ====================
class SalesTrendInput(BaseModel):
    """销售趋势数据提取输入"""
    start_date: Optional[date] = Field(default=None, description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")

class SalesTrendOutput(BaseModel):
    """销售趋势数据提取输出"""
    chart_data: Dict[str, Any] = Field(..., description="图表数据")
    chart_config: Dict[str, Any] = Field(..., description="图表配置")

# ==================== 商品销售排行节点 ====================
class ProductRankingInput(BaseModel):
    """商品销售排行输入"""
    start_date: Optional[date] = Field(default=None, description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")
    top_n: int = Field(default=10, description="返回前N个商品")

class ProductRankingOutput(BaseModel):
    """商品销售排行输出"""
    chart_data: Dict[str, Any] = Field(..., description="图表数据")
    chart_config: Dict[str, Any] = Field(..., description="图表配置")

# ==================== 库存状态分布节点 ====================
class InventoryDistributionInput(BaseModel):
    """库存状态分布输入"""
    # 可以添加过滤条件

class InventoryDistributionOutput(BaseModel):
    """库存状态分布输出"""
    chart_data: Dict[str, Any] = Field(..., description="图表数据")
    chart_config: Dict[str, Any] = Field(..., description="图表配置")

# ==================== 客户消费分析节点 ====================
class CustomerAnalysisInput(BaseModel):
    """客户消费分析输入"""
    start_date: Optional[date] = Field(default=None, description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")
    top_n: int = Field(default=10, description="返回前N个客户")

class CustomerAnalysisOutput(BaseModel):
    """客户消费分析输出"""
    chart_data: Dict[str, Any] = Field(..., description="图表数据")
    chart_config: Dict[str, Any] = Field(..., description="图表配置")

# ==================== 供应商采购统计节点 ====================
class SupplierStatsInput(BaseModel):
    """供应商采购统计输入"""
    start_date: Optional[date] = Field(default=None, description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")

class SupplierStatsOutput(BaseModel):
    """供应商采购统计输出"""
    chart_data: Dict[str, Any] = Field(..., description="图表数据")
    chart_config: Dict[str, Any] = Field(..., description="图表配置")

# ==================== 图表配置生成节点 ====================
class ChartConfigGenerationInput(BaseModel):
    """图表配置生成输入"""
    chart_type: str = Field(..., description="图表类型")
    raw_data: Dict[str, Any] = Field(..., description="原始数据")

class ChartConfigGenerationOutput(BaseModel):
    """图表配置生成输出"""
    chart_data: Dict[str, Any] = Field(..., description="Chart.js格式数据")
    chart_config: Dict[str, Any] = Field(..., description="Chart.js配置")

# ==================== 路由判断输入 ====================
class RouteDecisionInput(BaseModel):
    """路由判断输入"""
    chart_type: str = Field(..., description="图表类型")
