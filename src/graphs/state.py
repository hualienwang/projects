from typing import Literal, Optional, List
from pydantic import BaseModel, Field


# ==================== 全局状态 ====================
class GlobalState(BaseModel):
    """库存预警工作流的全局状态"""
    email_recipients: List[str] = Field(default=["manager@example.com"], description="邮件接收人列表")
    check_overstock: bool = Field(default=False, description="是否检查库存积压")
    low_stock_products: List[dict] = Field(default=[], description="低库存商品列表")
    overstock_products: List[dict] = Field(default=[], description="库存积压商品列表")
    alert_count: int = Field(default=0, description="预警总数")
    alert_report: str = Field(default="", description="预警报告内容")
    alert_summary: dict = Field(default={}, description="预警摘要信息")
    recommendations: str = Field(default="", description="补货建议")
    email_sent: bool = Field(default=False, description="邮件是否发送成功")
    email_result: dict = Field(default={}, description="邮件发送结果详情")
    recorded_count: int = Field(default=0, description="记录的预警数量")


# ==================== 工作流输入输出 ====================
class StockAlertWorkflowInput(BaseModel):
    """库存预警工作流输入"""
    email_recipients: List[str] = Field(default=["manager@example.com"], description="邮件接收人列表")
    check_overstock: bool = Field(default=False, description="是否检查库存积压")


class StockAlertWorkflowOutput(BaseModel):
    """库存预警工作流输出"""
    alert_count: int = Field(..., description="预警商品数量")
    alert_report: str = Field(..., description="预警报告内容")
    email_sent: bool = Field(..., description="邮件是否发送成功")


# ==================== 节点输入输出 ====================

# 节点1: 检查库存
class CheckInventoryInput(BaseModel):
    """检查库存节点输入"""
    check_overstock: bool = Field(default=False, description="是否检查库存积压")


class CheckInventoryOutput(BaseModel):
    """检查库存节点输出"""
    low_stock_products: List[dict] = Field(..., description="低库存商品列表")
    overstock_products: List[dict] = Field(default=[], description="库存积压商品列表")
    alert_count: int = Field(..., description="预警总数")


# 节点2: 分析预警
class AnalyzeAlertInput(BaseModel):
    """分析预警节点输入"""
    low_stock_products: List[dict] = Field(..., description="低库存商品列表")
    overstock_products: List[dict] = Field(default=[], description="库存积压商品列表")


class AnalyzeAlertOutput(BaseModel):
    """分析预警节点输出"""
    alert_summary: dict = Field(..., description="预警摘要信息")
    recommendations: str = Field(default="", description="补货建议")


# 节点3: 生成报告
class GenerateReportInput(BaseModel):
    """生成报告节点输入"""
    low_stock_products: List[dict] = Field(..., description="低库存商品列表")
    overstock_products: List[dict] = Field(default=[], description="库存积压商品列表")
    alert_summary: dict = Field(default={}, description="预警摘要")
    recommendations: str = Field(default="", description="补货建议")


class GenerateReportOutput(BaseModel):
    """生成报告节点输出"""
    alert_report: str = Field(..., description="预警报告内容")


# 节点4: 发送邮件
class SendEmailInput(BaseModel):
    """发送邮件节点输入"""
    email_recipients: List[str] = Field(..., description="邮件接收人列表")
    alert_report: str = Field(..., description="预警报告内容")


class SendEmailOutput(BaseModel):
    """发送邮件节点输出"""
    email_sent: bool = Field(..., description="邮件是否发送成功")
    email_result: dict = Field(default={}, description="邮件发送结果详情")


# 节点5: 记录预警
class RecordAlertInput(BaseModel):
    """记录预警节点输入"""
    low_stock_products: List[dict] = Field(..., description="低库存商品列表")


class RecordAlertOutput(BaseModel):
    """记录预警节点输出"""
    recorded_count: int = Field(..., description="记录的预警数量")
