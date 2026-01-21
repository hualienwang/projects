from typing import Literal, Optional, List
from pydantic import BaseModel, Field


# ==================== 全局状态 ====================
class SalesAnalysisGlobalState(BaseModel):
    """销售数据分析工作流的全局状态"""
    report_type: str = Field(default="daily", description="报告类型: daily/weekly/monthly")
    start_date: str = Field(default="", description="开始日期")
    end_date: str = Field(default="", description="结束日期")
    sales_data: List[dict] = Field(default=[], description="销售数据")
    total_sales: float = Field(default=0.0, description="总销售额")
    total_orders: int = Field(default=0, description="总订单数")
    top_products: List[dict] = Field(default=[], description="热销商品")
    low_stock_products: List[dict] = Field(default=[], description="库存不足商品")
    sales_trend: dict = Field(default={}, description="销售趋势")
    analysis_result: str = Field(default="", description="AI分析结果")
    report_sent: bool = Field(default=False, description="报告是否发送")


# ==================== 工作流输入输出 ====================
class SalesAnalysisInput(BaseModel):
    """销售数据分析工作流输入"""
    report_type: str = Field(default="daily", description="报告类型: daily/weekly/monthly")
    start_date: Optional[str] = Field(None, description="开始日期 (YYYY-MM-DD)")
    end_date: Optional[str] = Field(None, description="结束日期 (YYYY-MM-DD)")
    email_recipients: List[str] = Field(default=["manager@example.com"], description="邮件接收人")


class SalesAnalysisOutput(BaseModel):
    """销售数据分析工作流输出"""
    report_type: str = Field(..., description="报告类型")
    total_sales: float = Field(..., description="总销售额")
    total_orders: int = Field(..., description="总订单数")
    top_selling_product: str = Field(..., description="热销商品")
    report_sent: bool = Field(..., description="报告是否发送")
    message: str = Field(..., description="处理消息")


# ==================== 节点输入输出 ====================

# 节点1: 收集销售数据
class CollectSalesDataInput(BaseModel):
    """收集销售数据节点输入"""
    report_type: str = Field(..., description="报告类型")
    start_date: Optional[str] = Field(None, description="开始日期")
    end_date: Optional[str] = Field(None, description="结束日期")


class CollectSalesDataOutput(BaseModel):
    """收集销售数据节点输出"""
    sales_data: List[dict] = Field(..., description="销售数据")
    total_sales: float = Field(..., description="总销售额")
    total_orders: int = Field(..., description="总订单数")
    date_range: str = Field(..., description="日期范围")


# 节点2: 分析销售趋势
class AnalyzeSalesTrendInput(BaseModel):
    """分析销售趋势节点输入"""
    sales_data: List[dict] = Field(..., description="销售数据")


class AnalyzeSalesTrendOutput(BaseModel):
    """分析销售趋势节点输出"""
    sales_trend: dict = Field(..., description="销售趋势分析")
    top_products: List[dict] = Field(..., description="热销商品排行")
    low_stock_products: List[dict] = Field(default=[], description="库存不足商品")


# 节点3: AI分析（大语言模型节点）
class AIAnalyzeSalesInput(BaseModel):
    """AI分析销售节点输入"""
    sales_data: List[dict] = Field(..., description="销售数据")
    total_sales: float = Field(..., description="总销售额")
    total_orders: int = Field(..., description="总订单数")
    top_products: List[dict] = Field(..., description="热销商品")


class AIAnalyzeSalesOutput(BaseModel):
    """AI分析销售节点输出"""
    analysis_result: str = Field(..., description="AI分析结果")
    insights: List[str] = Field(default=[], description="洞察建议")


# 节点4: 生成报告
class GenerateSalesReportInput(BaseModel):
    """生成销售报告节点输入"""
    report_type: str = Field(..., description="报告类型")
    date_range: str = Field(..., description="日期范围")
    total_sales: float = Field(..., description="总销售额")
    total_orders: int = Field(..., description="总订单数")
    sales_trend: dict = Field(..., description="销售趋势")
    top_products: List[dict] = Field(..., description="热销商品")
    low_stock_products: List[dict] = Field(default=[], description="库存不足商品")
    analysis_result: str = Field(default="", description="AI分析结果")


class GenerateSalesReportOutput(BaseModel):
    """生成销售报告节点输出"""
    report_content: str = Field(..., description="报告内容")


# 节点5: 发送报告
class SendSalesReportInput(BaseModel):
    """发送销售报告节点输入"""
    email_recipients: List[str] = Field(..., description="邮件接收人")
    report_content: str = Field(..., description="报告内容")
    report_type: str = Field(..., description="报告类型")


class SendSalesReportOutput(BaseModel):
    """发送销售报告节点输出"""
    report_sent: bool = Field(..., description="报告是否发送")
    message: str = Field(default="", description="发送消息")
