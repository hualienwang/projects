from typing import Literal, Optional, List
from pydantic import BaseModel, Field


# ==================== 全局状态 ====================
class LoyaltyGlobalState(BaseModel):
    """客户忠诚度管理工作流的全局状态"""
    customer_id: int = Field(default=0, description="客户ID")
    order_amount: float = Field(default=0.0, description="本次订单金额")
    customer_info: dict = Field(default={}, description="客户信息")
    purchase_history: List[dict] = Field(default=[], description="购买历史")
    current_points: int = Field(default=0, description="当前积分")
    new_points: int = Field(default=0, description="新增积分")
    total_points: int = Field(default=0, description="总积分")
    current_level: str = Field(default="", description="当前会员等级")
    new_level: str = Field(default="", description="新会员等级")
    level_upgraded: bool = Field(default=False, description="是否升级")
    notification_type: str = Field(default="", description="通知类型（level_up/birthday/promotion）")
    loyalty_report: str = Field(default="", description="忠诚度报告")
    notification_sent: bool = Field(default=False, description="通知是否发送")


# ==================== 工作流输入输出 ====================
class LoyaltyWorkflowInput(BaseModel):
    """客户忠诚度管理工作流输入"""
    customer_id: int = Field(..., description="客户ID")
    order_amount: float = Field(default=0.0, description="本次订单金额（可选，用于计算积分）")
    check_all_customers: bool = Field(default=False, description="是否检查所有客户")


class LoyaltyWorkflowOutput(BaseModel):
    """客户忠诚度管理工作流输出"""
    customer_id: int = Field(..., description="客户ID")
    customer_name: str = Field(..., description="客户姓名")
    current_level: str = Field(..., description="当前会员等级")
    total_points: int = Field(..., description="总积分")
    level_upgraded: bool = Field(..., description="是否升级")
    message: str = Field(..., description="处理消息")


# ==================== 节点输入输出 ====================

# 节点1: 获取客户信息
class GetCustomerInfoInput(BaseModel):
    """获取客户信息节点输入"""
    customer_id: int = Field(..., description="客户ID")


class GetCustomerInfoOutput(BaseModel):
    """获取客户信息节点输出"""
    customer_info: dict = Field(..., description="客户信息")
    purchase_history: List[dict] = Field(default=[], description="购买历史")
    current_level: str = Field(default="", description="当前会员等级")


# 节点2: 计算积分
class CalculatePointsInput(BaseModel):
    """计算积分节点输入"""
    customer_id: int = Field(..., description="客户ID")
    order_amount: float = Field(default=0.0, description="本次订单金额")


class CalculatePointsOutput(BaseModel):
    """计算积分节点输出"""
    current_points: int = Field(..., description="当前积分")
    new_points: int = Field(default=0, description="新增积分")
    total_points: int = Field(..., description="总积分")
    total_purchase: float = Field(default=0.0, description="累计消费金额")


# 节点3: 判断会员等级
class CheckMemberLevelInput(BaseModel):
    """判断会员等级节点输入"""
    total_points: int = Field(..., description="总积分")
    current_level: str = Field(..., description="当前会员等级")


class CheckMemberLevelOutput(BaseModel):
    """判断会员等级节点输出"""
    current_level: str = Field(..., description="当前会员等级")
    new_level: str = Field(..., description="新会员等级")
    level_upgraded: bool = Field(..., description="是否升级")


# 节点4: 更新会员等级
class UpdateMemberLevelInput(BaseModel):
    """更新会员等级节点输入"""
    customer_id: int = Field(..., description="客户ID")
    new_level: str = Field(..., description="新会员等级")
    total_points: int = Field(..., description="总积分")
    notification_type: str = Field(default="level_up", description="通知类型")


class UpdateMemberLevelOutput(BaseModel):
    """更新会员等级节点输出"""
    updated: bool = Field(..., description="是否更新成功")
    message: str = Field(default="", description="更新消息")
    notification_type: str = Field(default="level_up", description="通知类型")


# 节点5: 生成忠诚度报告
class GenerateLoyaltyReportInput(BaseModel):
    """生成忠诚度报告节点输入"""
    customer_info: dict = Field(..., description="客户信息")
    purchase_history: List[dict] = Field(default=[], description="购买历史")
    total_points: int = Field(..., description="总积分")
    current_level: str = Field(..., description="当前会员等级")
    level_upgraded: bool = Field(default=False, description="是否升级")


class GenerateLoyaltyReportOutput(BaseModel):
    """生成忠诚度报告节点输出"""
    loyalty_report: str = Field(..., description="忠诚度报告")


# 节点6: 发送通知
class SendLoyaltyNotificationInput(BaseModel):
    """发送通知节点输入"""
    customer_id: int = Field(..., description="客户ID")
    notification_type: str = Field(default="", description="通知类型: level_up/birthday/promotion")
    report: str = Field(default="", description="报告内容")


class SendLoyaltyNotificationOutput(BaseModel):
    """发送通知节点输出"""
    notification_sent: bool = Field(..., description="通知是否发送")
    message: str = Field(default="", description="通知消息")
