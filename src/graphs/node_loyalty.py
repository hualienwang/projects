import os
import json
from datetime import datetime, date
from typing import List

from sqlalchemy.orm import Session
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_dev_sdk.database import get_session
from coze_coding_utils.runtime_ctx.context import Context
from cozeloop.decorator import observe
from coze_workload_identity import Client

from graphs.state_loyalty import (
    GetCustomerInfoInput, GetCustomerInfoOutput,
    CalculatePointsInput, CalculatePointsOutput,
    CheckMemberLevelInput, CheckMemberLevelOutput,
    UpdateMemberLevelInput, UpdateMemberLevelOutput,
    GenerateLoyaltyReportInput, GenerateLoyaltyReportOutput,
    SendLoyaltyNotificationInput, SendLoyaltyNotificationOutput
)
from storage.database.shared.model import Customer, Order, OrderItem


# ==================== 节点1: 获取客户信息 ====================
def get_customer_info_node(
    state: GetCustomerInfoInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GetCustomerInfoOutput:
    """
    title: 获取客户信息
    desc: 查询客户信息和购买历史
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 查询客户信息
        customer = db.query(Customer).filter(Customer.id == state.customer_id).first()
        
        if not customer:
            return GetCustomerInfoOutput(
                customer_info={},
                purchase_history=[]
            )
        
        # 查询购买历史
        orders = db.query(Order).filter(
            Order.customer_id == state.customer_id,
            Order.status.in_(["completed", "shipped"])
        ).order_by(Order.created_at.desc()).limit(10).all()
        
        purchase_history = []
        for order in orders:
            purchase_history.append({
                "order_no": order.order_no,
                "total_amount": float(order.total_amount),
                "order_date": order.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                "status": order.status
            })
        
        customer_info = {
            "id": customer.id,
            "name": customer.name,
            "phone": customer.phone,
            "email": customer.email,
            "level": customer.level,
            "points": customer.points,
            "total_purchase": float(customer.total_purchase),
            "last_purchase_date": customer.last_purchase_date.strftime("%Y-%m-%d") if bool(customer.last_purchase_date) else None
        }
        
        return GetCustomerInfoOutput(
            customer_info=customer_info,
            purchase_history=purchase_history,
            current_level=customer_info.get("level", "普通會員")
        )
    finally:
        db.close()


# ==================== 节点2: 计算积分 ====================
def calculate_points_node(
    state: CalculatePointsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CalculatePointsOutput:
    """
    title: 计算积分
    desc: 根据订单金额计算新增积分
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        customer = db.query(Customer).filter(Customer.id == state.customer_id).first()
        
        if not customer:
            return CalculatePointsOutput(
                current_points=0,
                new_points=0,
                total_points=0,
                total_purchase=0.0
            )
        
        current_points = customer.points
        total_purchase = float(customer.total_purchase)
        
        # 计算积分：每消费1元积1分
        new_points = int(state.order_amount) if state.order_amount > 0 else 0
        total_points = current_points + new_points
        
        return CalculatePointsOutput(
            current_points=current_points,
            new_points=new_points,
            total_points=total_points,
            total_purchase=total_purchase
        )
    finally:
        db.close()


# ==================== 节点3: 判断会员等级 ====================
def check_member_level_node(
    state: CheckMemberLevelInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CheckMemberLevelOutput:
    """
    title: 判断会员等级
    desc: 根据积分判断会员等级
    integrations:
    """
    ctx = runtime.context
    
    # 会员等级规则
    LEVEL_RULES = [
        (10000, "鑽石會員"),
        (5000, "白金會員"),
        (2000, "金卡會員"),
        (500, "銀卡會員"),
        (0, "普通會員")
    ]
    
    # 根据积分确定等级
    new_level = "普通會員"
    for threshold, level in LEVEL_RULES:
        if state.total_points >= threshold:
            new_level = level
            break
    
    # 判断是否升级
    level_upgraded = new_level != state.current_level
    
    return CheckMemberLevelOutput(
        current_level=state.current_level,
        new_level=new_level,
        level_upgraded=level_upgraded
    )


# ==================== 节点4: 更新会员等级 ====================
def update_member_level_node(
    state: UpdateMemberLevelInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> UpdateMemberLevelOutput:
    """
    title: 更新会员等级
    desc: 更新客户积分和会员等级
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        customer = db.query(Customer).filter(Customer.id == state.customer_id).first()
        
        if not customer:
            return UpdateMemberLevelOutput(
                updated=False,
                message="客户不存在"
            )
        
        # 更新积分和等级
        setattr(customer, "points", state.total_points)
        setattr(customer, "level", state.new_level)
        
        db.add(customer)
        try:
            db.commit()
            db.refresh(customer)
            return UpdateMemberLevelOutput(
                updated=True,
                message=f"会员等级已更新为 {state.new_level}，当前积分 {state.total_points}",
                notification_type=state.notification_type
            )
        except Exception as e:
            db.rollback()
            return UpdateMemberLevelOutput(
                updated=False,
                message=f"更新失败: {str(e)}"
            )
    finally:
        db.close()


# ==================== 节点5: 生成忠诚度报告 ====================
def generate_loyalty_report_node(
    state: GenerateLoyaltyReportInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GenerateLoyaltyReportOutput:
    """
    title: 生成忠诚度报告
    desc: 生成客户忠诚度分析报告
    integrations:
    """
    ctx = runtime.context
    
    report_lines = []
    
    # 报告标题
    report_lines.append("=" * 80)
    report_lines.append("客户忠诚度报告")
    report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # 客户信息
    report_lines.append("【客户信息】")
    report_lines.append(f"姓名: {state.customer_info.get('name', 'N/A')}")
    report_lines.append(f"电话: {state.customer_info.get('phone', 'N/A')}")
    report_lines.append(f"邮箱: {state.customer_info.get('email', 'N/A')}")
    report_lines.append(f"当前会员等级: {state.current_level}")
    report_lines.append(f"总积分: {state.total_points}")
    report_lines.append(f"累计消费: ¥{state.customer_info.get('total_purchase', 0):.2f}")
    report_lines.append(f"最后购买时间: {state.customer_info.get('last_purchase_date', 'N/A')}")
    report_lines.append("")
    
    # 会员升级
    if state.level_upgraded:
        report_lines.append("【🎉 恭喜升级！】")
        report_lines.append(f"您已成功升级为 {state.current_level}！")
        report_lines.append("升级权益:")
        if state.current_level == "鑽石會員":
            report_lines.append("- 享受95折优惠")
            report_lines.append("- 专属客服")
            report_lines.append("- 免费配送")
        elif state.current_level == "白金會員":
            report_lines.append("- 享受96折优惠")
            report_lines.append("- 优先配送")
        elif state.current_level == "金卡會員":
            report_lines.append("- 享受97折优惠")
        elif state.current_level == "銀卡會員":
            report_lines.append("- 享受98折优惠")
        report_lines.append("")
    
    # 购买历史
    if state.purchase_history:
        report_lines.append("【近期购买记录】")
        report_lines.append("-" * 80)
        for i, order in enumerate(state.purchase_history[:5], 1):
            report_lines.append(f"{i}. 订单号: {order['order_no']}")
            report_lines.append(f"   金额: ¥{order['total_amount']:.2f}")
            report_lines.append(f"   日期: {order['order_date']}")
            report_lines.append(f"   状态: {order['status']}")
        report_lines.append("")
    
    # 积分规则说明
    report_lines.append("【积分规则】")
    report_lines.append("- 每消费1元积1分")
    report_lines.append("- 500分：银卡会员（98折）")
    report_lines.append("- 2000分：金卡会员（97折）")
    report_lines.append("- 5000分：白金会员（96折）")
    report_lines.append("- 10000分：钻石会员（95折）")
    report_lines.append("")
    
    report_lines.append("=" * 80)
    report_lines.append("感谢您的支持！")
    report_lines.append("瓊林圖書事業有限公司")
    report_lines.append("=" * 80)
    
    loyalty_report = "\n".join(report_lines)
    
    return GenerateLoyaltyReportOutput(loyalty_report=loyalty_report)


# ==================== 节点6: 发送通知 ====================
@observe
def send_loyalty_notification_node(
    state: SendLoyaltyNotificationInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SendLoyaltyNotificationOutput:
    """
    title: 发送忠诚度通知
    desc: 发送会员等级升级或活动通知邮件
    integrations: 邮件
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        customer = db.query(Customer).filter(Customer.id == state.customer_id).first()
        
        if not customer or not bool(customer.email):
            return SendLoyaltyNotificationOutput(
                notification_sent=False,
                message="客户邮箱不存在"
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
        if state.notification_type == "level_up":
            subject = f"恭喜升级 - {customer.level}"
            content = state.report
        elif state.notification_type == "birthday":
            subject = "生日快乐！"
            content = f"""
尊敬的 {customer.name}：

生日快乐！祝您生日快乐，身体健康！

瓊林圖書事業有限公司
"""
        else:
            subject = "会员活动通知"
            content = state.report
        
        msg = MIMEText(content, "plain", "utf-8")
        msg["From"] = formataddr(("会员系统", email_config["account"]))
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
        
        return SendLoyaltyNotificationOutput(
            notification_sent=True,
            message=f"已发送{state.notification_type}通知到 {customer.email}"
        )
    except Exception as e:
        return SendLoyaltyNotificationOutput(
            notification_sent=False,
            message=f"发送通知失败: {str(e)}"
        )
    finally:
        db.close()
