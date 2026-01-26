import os
import json
from datetime import datetime
from typing import List
from jinja2 import Template

from langchain_core.runnables import RunnableConfig
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.runtime import Runtime
from coze_coding_dev_sdk import LLMClient
from coze_coding_utils.runtime_ctx.context import Context
from cozeloop.decorator import observe

try:
    from coze_workload_identity import Client
    HAS_WORKLOAD_IDENTITY = True
except ImportError:
    HAS_WORKLOAD_IDENTITY = False

from graphs.state import (
    CheckInventoryInput, CheckInventoryOutput,
    AnalyzeAlertInput, AnalyzeAlertOutput,
    GenerateReportInput, GenerateReportOutput,
    SendEmailInput, SendEmailOutput,
    RecordAlertInput, RecordAlertOutput
)
from storage.database.inventory_manager import InventoryManager, StockAlertCreate
from storage.database.db import get_session


# ==================== 节点1: 检查库存 ====================
def check_inventory_node(
    state: CheckInventoryInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CheckInventoryOutput:
    """
    title: 检查库存
    desc: 从数据库查询所有商品库存，识别低库存和库存积压商品
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        inventory_mgr = InventoryManager()
        
        # 检查低库存
        low_stock_products = inventory_mgr.check_low_stock(db)
        
        # 检查库存积压
        overstock_products = []
        if state.check_overstock:
            overstock_products = inventory_mgr.check_overstock(db)
        
        alert_count = len(low_stock_products) + len(overstock_products)
        
        return CheckInventoryOutput(
            low_stock_products=low_stock_products,
            overstock_products=overstock_products,
            alert_count=alert_count
        )
    finally:
        db.close()


# ==================== 节点2: 分析预警（大语言模型节点）====================
def analyze_alert_node(
    state: AnalyzeAlertInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> AnalyzeAlertOutput:
    """
    title: 分析预警
    desc: 使用大语言模型分析库存预警情况，生成智能补货建议
    integrations: 大语言模型
    """
    ctx = runtime.context

    # 检查是否有 LLM API Key 配置
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    if not api_key:
        # 本地环境：生成模拟的补货建议
        recommendations = generate_mock_recommendations(state.low_stock_products, state.overstock_products)

        # 生成摘要
        alert_summary = {
            "low_stock_count": len(state.low_stock_products),
            "overstock_count": len(state.overstock_products),
            "total_alerts": len(state.low_stock_products) + len(state.overstock_products),
            "analysis_time": datetime.now().isoformat()
        }

        return AnalyzeAlertOutput(
            alert_summary=alert_summary,
            recommendations=recommendations
        )

    # 读取配置文件
    workspace_path = os.getenv("COZE_WORKSPACE_PATH")
    if not workspace_path:
        workspace_path = os.getcwd()
    cfg_file = os.path.join(workspace_path, config['metadata']['llm_cfg'])
    with open(cfg_file, 'r', encoding='utf-8') as fd:
        _cfg = json.load(fd)

    llm_config = _cfg.get("config", {})
    sp = _cfg.get("sp", "")
    up = _cfg.get("up", "")

    # 使用jinja2模板渲染提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        "low_stock_count": len(state.low_stock_products),
        "overstock_count": len(state.overstock_products),
        "low_stock_data": json.dumps(state.low_stock_products, ensure_ascii=False)
    })

    # 调用大语言模型
    llm_client = LLMClient(ctx=ctx)

    messages = [
        SystemMessage(content=sp),
        HumanMessage(content=user_prompt_content)
    ]

    response = llm_client.invoke(
        messages=messages,
        model=llm_config.get("model", "doubao-seed-1-8-251228"),
        temperature=llm_config.get("temperature", 0.3)
    )

    # 解析响应
    content = response.content
    recommendations = ""

    if isinstance(content, str):
        recommendations = content
    elif isinstance(content, list):
        # 处理列表格式响应
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                if isinstance(text, str):
                    text_parts.append(text)
        recommendations = " ".join(text_parts)
    else:
        # 其他情况，转换为字符串
        recommendations = str(content)

    # 生成摘要
    alert_summary = {
        "low_stock_count": len(state.low_stock_products),
        "overstock_count": len(state.overstock_products),
        "total_alerts": len(state.low_stock_products) + len(state.overstock_products),
        "analysis_time": datetime.now().isoformat()
    }

    return AnalyzeAlertOutput(
        alert_summary=alert_summary,
        recommendations=recommendations
    )


def generate_mock_recommendations(low_stock_products: List[dict], overstock_products: List[dict]) -> str:
    """生成模拟的补货建议"""
    lines = []

    if low_stock_products:
        lines.append("【智能补货建议】")
        lines.append("")

        # 按缺货数量排序
        sorted_products = sorted(low_stock_products, key=lambda x: x.get("shortage", 0), reverse=True)

        lines.append("1. 【紧急处理】")
        for product in sorted_products[:3]:  # 前3个最紧急的
            shortage = product.get("shortage", 0)
            if shortage > 10:
                lines.append(f"   - 商品名称：{product.get('name', 'N/A')}")
                lines.append(f"   - 补货数量：{product.get('reorder_quantity', 0)}")
                lines.append(f"   - 理由：当前库存{product.get('current_quantity', 0)}，低于最小阈值{product.get('min_threshold', 0)}，缺口{shortage}，属于紧急缺货，需立即补货")
                lines.append("")

        if len(sorted_products) > 3:
            lines.append("2. 【重要处理】")
            for product in sorted_products[3:]:
                shortage = product.get("shortage", 0)
                lines.append(f"   - 商品名称：{product.get('name', 'N/A')}")
                lines.append(f"   - 补货数量：{product.get('reorder_quantity', 0)}")
                lines.append(f"   - 理由：当前库存{product.get('current_quantity', 0)}，低于最小阈值{product.get('min_threshold', 0)}，缺口{shortage}，建议按推荐数量补货")
                lines.append("")

    if overstock_products:
        lines.append("3. 【库存积压处理建议】")
        lines.append("   本次检测到库存积压商品，建议采取以下措施：")
        lines.append("   - 开展促销活动，降低库存水平")
        lines.append("   - 联系供应商协商退换货")
        lines.append("   - 适当减少后续采购数量")
        lines.append("")

    if not low_stock_products and not overstock_products:
        lines.append("【智能补货建议】")
        lines.append("当前库存状态良好，无需立即补货。建议定期监控库存水平。")
        lines.append("")

    return "\n".join(lines)


# ==================== 节点3: 生成报告 ====================
def generate_report_node(
    state: GenerateReportInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GenerateReportOutput:
    """
    title: 生成预警报告
    desc: 整合库存预警数据和补货建议，生成详细的预警报告
    integrations:
    """
    ctx = runtime.context
    
    # 构建报告
    report_lines = []
    
    # 报告标题
    report_lines.append("=" * 80)
    report_lines.append("库存预警报告")
    report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # 摘要信息
    report_lines.append("【预警摘要】")
    if state.alert_summary:
        report_lines.append(f"- 低库存商品数量: {state.alert_summary.get('low_stock_count', 0)}")
        report_lines.append(f"- 库存积压商品数量: {state.alert_summary.get('overstock_count', 0)}")
        report_lines.append(f"- 预警总数: {state.alert_summary.get('total_alerts', 0)}")
    report_lines.append("")
    
    # 低库存商品详情
    if state.low_stock_products:
        report_lines.append("【低库存商品详情】")
        report_lines.append("-" * 80)
        for idx, product in enumerate(state.low_stock_products, 1):
            report_lines.append(f"\n{idx}. {product.get('name', 'N/A')}")
            report_lines.append(f"   ISBN: {product.get('isbn', 'N/A')}")
            report_lines.append(f"   作者: {product.get('author', 'N/A')}")
            report_lines.append(f"   价格: ¥{product.get('price', 0):.2f}")
            report_lines.append(f"   当前库存: {product.get('current_quantity', 0)}")
            report_lines.append(f"   最小阈值: {product.get('min_threshold', 0)}")
            report_lines.append(f"   缺货数量: {product.get('shortage', 0)}")
            report_lines.append(f"   建议补货: {product.get('reorder_quantity', 0)}")
        report_lines.append("")
    
    # 库存积压商品详情
    if state.overstock_products:
        report_lines.append("【库存积压商品详情】")
        report_lines.append("-" * 80)
        for idx, product in enumerate(state.overstock_products, 1):
            report_lines.append(f"\n{idx}. {product.get('name', 'N/A')}")
            report_lines.append(f"   ISBN: {product.get('isbn', 'N/A')}")
            report_lines.append(f"   作者: {product.get('author', 'N/A')}")
            report_lines.append(f"   价格: ¥{product.get('price', 0):.2f}")
            report_lines.append(f"   当前库存: {product.get('current_quantity', 0)}")
            report_lines.append(f"   最大阈值: {product.get('max_threshold', 0)}")
            report_lines.append(f"   积压数量: {product.get('overstock', 0)}")
        report_lines.append("")
    
    # 补货建议
    if state.recommendations:
        report_lines.append("【智能补货建议】")
        report_lines.append("-" * 80)
        report_lines.append(state.recommendations)
        report_lines.append("")
    
    report_lines.append("=" * 80)
    report_lines.append("报告结束")
    report_lines.append("=" * 80)
    
    alert_report = "\n".join(report_lines)
    
    return GenerateReportOutput(alert_report=alert_report)


# ==================== 节点4: 发送邮件 ====================
@observe
def send_email_node(
    state: SendEmailInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SendEmailOutput:
    """
    title: 发送邮件通知
    desc: 将库存预警报告通过邮件发送给相关人员
    integrations: 邮件
    """
    ctx = runtime.context

    # 检查是否有邮件配置
    if not HAS_WORKLOAD_IDENTITY:
        # 本地环境：模拟发送邮件
        return SendEmailOutput(
            email_sent=True,
            email_result={
                "status": "simulated",
                "recipients": state.email_recipients,
                "sent_time": datetime.now().isoformat(),
                "message": "本地环境模拟发送邮件成功"
            }
        )

    # 获取邮件配置
    try:
        client = Client()
        email_credential = client.get_integration_credential("integration-email-imap-smtp")
        email_config = json.loads(email_credential)
    except Exception as e:
        # 获取邮件配置失败，返回模拟结果
        return SendEmailOutput(
            email_sent=False,
            email_result={
                "status": "error",
                "error": f"无法获取邮件配置: {str(e)}",
                "simulated": True
            }
        )
    
    import smtplib
    import ssl
    from email.mime.text import MIMEText
    from email.header import Header
    from email.utils import formataddr, formatdate, make_msgid
    
    try:
        # 构建邮件内容（HTML格式）
        html_content = state.alert_report.replace("\n", "<br>")
        
        msg = MIMEText(html_content, "html", "utf-8")
        msg["From"] = formataddr(("库存预警系统", email_config["account"]))
        msg["To"] = ", ".join(state.email_recipients)
        msg["Subject"] = Header("库存预警报告 - " + datetime.now().strftime("%Y-%m-%d"), "utf-8")
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
                state.email_recipients,
                msg.as_string()
            )
            server.quit()
        
        return SendEmailOutput(
            email_sent=True,
            email_result={
                "status": "success",
                "recipients": state.email_recipients,
                "sent_time": datetime.now().isoformat()
            }
        )
    except Exception as e:
        return SendEmailOutput(
            email_sent=False,
            email_result={
                "status": "error",
                "error": str(e)
            }
        )


# ==================== 节点5: 记录预警 ====================
def record_alert_node(
    state: RecordAlertInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> RecordAlertOutput:
    """
    title: 记录预警
    desc: 将低库存预警记录到数据库，便于后续跟踪
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        inventory_mgr = InventoryManager()
        recorded_count = 0
        
        for product in state.low_stock_products:
            alert_in = StockAlertCreate(
                product_id=product.get("product_id"),
                alert_type="low_stock",
                current_quantity=product.get("current_quantity", 0),
                threshold_value=product.get("min_threshold", 0),
                suggested_reorder_quantity=product.get("reorder_quantity", 0)
            )
            inventory_mgr.create_stock_alert(db, alert_in)
            recorded_count += 1
        
        return RecordAlertOutput(recorded_count=recorded_count)
    except Exception as e:
        return RecordAlertOutput(recorded_count=0)
    finally:
        db.close()
