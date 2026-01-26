import os
import json
from datetime import datetime, timedelta
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy import func
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

from graphs.state_sales import (
    CollectSalesDataInput, CollectSalesDataOutput,
    AnalyzeSalesTrendInput, AnalyzeSalesTrendOutput,
    AIAnalyzeSalesInput, AIAnalyzeSalesOutput,
    GenerateSalesReportInput, GenerateSalesReportOutput,
    SendSalesReportInput, SendSalesReportOutput
)
from storage.database.shared.model import Order, OrderItem, Product, Inventory
from storage.database.db import get_session
from jinja2 import Template


# ==================== 节点1: 收集销售数据 ====================
def collect_sales_data_node(
    state: CollectSalesDataInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CollectSalesDataOutput:
    """
    title: 收集销售数据
    desc: 从数据库收集指定时间范围内的销售数据
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 确定日期范围
        if state.start_date and state.end_date:
            start_date = datetime.strptime(state.start_date, "%Y-%m-%d")
            end_date = datetime.strptime(state.end_date, "%Y-%m-%d")
        else:
            # 默认根据报告类型设置日期范围
            today = datetime.now()
            if state.report_type == "daily":
                start_date = today.replace(hour=0, minute=0, second=0, microsecond=0)
                end_date = today.replace(hour=23, minute=59, second=59, microsecond=999999)
            elif state.report_type == "weekly":
                start_date = today - timedelta(days=7)
                end_date = today
            else:  # monthly
                start_date = today - timedelta(days=30)
                end_date = today
        
        date_range = f"{start_date.strftime('%Y-%m-%d')} 至 {end_date.strftime('%Y-%m-%d')}"
        
        # 查询订单数据
        orders = db.query(Order).filter(
            Order.created_at >= start_date,
            Order.created_at <= end_date,
            Order.status.in_(["completed", "paid"])
        ).all()
        
        # 汇总数据
        total_sales = 0.0
        sales_data = []
        
        for order in orders:
            total_sales += float(order.total_amount)
            
            # 查询订单商品
            items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            for item in items:
                product = db.query(Product).filter(Product.id == item.product_id).first()
                if product:
                    sales_data.append({
                        "order_no": order.order_no,
                        "order_date": order.created_at.strftime("%Y-%m-%d"),
                        "product_id": item.product_id,
                        "product_name": product.name,
                        "isbn": product.isbn,
                        "quantity": item.quantity,
                        "unit_price": float(item.unit_price),
                        "subtotal": float(item.subtotal)
                    })
        
        return CollectSalesDataOutput(
            sales_data=sales_data,
            total_sales=total_sales,
            total_orders=len(orders),
            date_range=date_range
        )
    finally:
        db.close()


# ==================== 节点2: 分析销售趋势 ====================
def analyze_sales_trend_node(
    state: AnalyzeSalesTrendInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> AnalyzeSalesTrendOutput:
    """
    title: 分析销售趋势
    desc: 分析销售数据，识别热销商品和库存不足商品
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 统计热销商品
        product_sales = {}
        for sale in state.sales_data:
            product_id = sale["product_id"]
            if product_id not in product_sales:
                product_sales[product_id] = {
                    "product_id": product_id,
                    "product_name": sale["product_name"],
                    "isbn": sale["isbn"],
                    "total_quantity": 0,
                    "total_amount": 0.0
                }
            product_sales[product_id]["total_quantity"] += sale["quantity"]
            product_sales[product_id]["total_amount"] += sale["subtotal"]
        
        # 排序获取热销商品
        top_products = sorted(product_sales.values(), key=lambda x: x["total_quantity"], reverse=True)[:5]
        
        # 检查库存不足商品
        low_stock_products = []
        for product_id in product_sales.keys():
            inventory = db.query(Inventory).filter(Inventory.product_id == product_id).first()
            if inventory and int(inventory.quantity) < int(inventory.min_stock_threshold):
                product_info = product_sales.get(product_id)
                low_stock_products.append({
                    "product_id": product_id,
                    "product_name": product_info["product_name"],
                    "current_quantity": inventory.quantity,
                    "min_threshold": inventory.min_stock_threshold,
                    "shortage": inventory.min_stock_threshold - inventory.quantity
                })
        
        # 销售趋势分析
        sales_by_date = {}
        for sale in state.sales_data:
            date = sale["order_date"]
            if date not in sales_by_date:
                sales_by_date[date] = 0.0
            sales_by_date[date] += sale["subtotal"]
        
        sales_trend = {
            "sales_by_date": sales_by_date,
            "total_products": len(product_sales),
            "avg_order_value": sum(s["subtotal"] for s in state.sales_data) / len(state.sales_data) if state.sales_data else 0
        }
        
        return AnalyzeSalesTrendOutput(
            sales_trend=sales_trend,
            top_products=top_products,
            low_stock_products=low_stock_products
        )
    finally:
        db.close()


# ==================== 节点3: AI分析（大语言模型节点）====================
def ai_analyze_sales_node(
    state: AIAnalyzeSalesInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> AIAnalyzeSalesOutput:
    """
    title: AI分析销售
    desc: 使用大语言模型分析销售数据，提供洞察和建议
    integrations: 大语言模型
    """
    ctx = runtime.context

    # 检查是否有 LLM API Key 配置
    api_key = os.getenv("COZE_WORKLOAD_IDENTITY_API_KEY")
    if not api_key:
        # 本地环境：生成模拟的销售分析
        analysis_result = generate_mock_sales_analysis(state.total_sales, state.total_orders, state.top_products)

        return AIAnalyzeSalesOutput(
            analysis_result=analysis_result,
            insights=[]
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

    # 准备数据
    top_products_summary = "\n".join([
        f"{i+1}. {p['product_name']} - 销量: {p['total_quantity']} - 金额: ¥{p['total_amount']:.2f}"
        for i, p in enumerate(state.top_products[:3], 1)
    ])

    # 使用jinja2模板渲染提示词
    up_tpl = Template(up)
    user_prompt_content = up_tpl.render({
        "total_sales": state.total_sales,
        "total_orders": state.total_orders,
        "top_products": top_products_summary
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
        temperature=llm_config.get("temperature", 0.5)
    )

    # 解析响应
    content = response.content
    if isinstance(content, str):
        analysis_result = content
    elif isinstance(content, list):
        text_parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                text = item.get("text", "")
                if isinstance(text, str):
                    text_parts.append(text)
        analysis_result = " ".join(text_parts)
    else:
        analysis_result = str(content)

    return AIAnalyzeSalesOutput(
        analysis_result=analysis_result,
        insights=[]
    )


def generate_mock_sales_analysis(total_sales: float, total_orders: int, top_products: List[dict]) -> str:
    """生成模拟的销售分析"""
    lines = []

    lines.append("【销售数据分析】")
    lines.append("")

    if total_orders == 0:
        lines.append("本期暂无销售数据，建议加强营销推广活动。")
        lines.append("")
        return "\n".join(lines)

    avg_order_value = total_sales / total_orders if total_orders > 0 else 0

    lines.append(f"1. 【整体表现】")
    lines.append(f"   - 本期总销售额为 ¥{total_sales:,.2f}，共完成 {total_orders} 笔订单")
    lines.append(f"   - 平均订单金额为 ¥{avg_order_value:,.2f}")
    lines.append("")

    lines.append("2. 【热门商品】")
    if top_products:
        for i, p in enumerate(top_products[:3], 1):
            lines.append(f"   Top{i}. {p['product_name']}")
            lines.append(f"        销量: {p['total_quantity']} 本")
            lines.append(f"        销售额: ¥{p['total_amount']:,.2f}")
    else:
        lines.append("   本期暂无销售记录")
    lines.append("")

    lines.append("3. 【建议】")
    lines.append("   - 继续保持热门商品的库存充足")
    lines.append("   - 对滞销商品考虑开展促销活动")
    lines.append("   - 优化客户体验，提高复购率")
    lines.append("")

    return "\n".join(lines)


# ==================== 节点4: 生成报告 ====================
def generate_sales_report_node(
    state: GenerateSalesReportInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> GenerateSalesReportOutput:
    """
    title: 生成销售报告
    desc: 整合销售数据和分析结果，生成详细的销售报告
    integrations:
    """
    ctx = runtime.context
    
    report_lines = []
    
    # 报告标题
    report_type_cn = {"daily": "日", "weekly": "周", "monthly": "月"}.get(state.report_type, state.report_type)
    report_lines.append("=" * 80)
    report_lines.append(f"销售数据分析报告 - {report_type_cn}报")
    report_lines.append(f"统计时间: {state.date_range}")
    report_lines.append(f"生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("=" * 80)
    report_lines.append("")
    
    # 核心指标
    report_lines.append("【核心指标】")
    report_lines.append(f"总销售额: ¥{state.total_sales:,.2f}")
    report_lines.append(f"总订单数: {state.total_orders}")
    report_lines.append(f"平均订单金额: ¥{state.total_sales/state.total_orders:,.2f}" if state.total_orders > 0 else "平均订单金额: ¥0.00")
    report_lines.append("")
    
    # 热销商品
    if state.top_products:
        report_lines.append("【热销商品排行】")
        report_lines.append("-" * 80)
        for i, product in enumerate(state.top_products[:5], 1):
            report_lines.append(f"{i}. {product['product_name']}")
            report_lines.append(f"   ISBN: {product['isbn']}")
            report_lines.append(f"   销量: {product['total_quantity']} 本")
            report_lines.append(f"   销售额: ¥{product['total_amount']:,.2f}")
        report_lines.append("")
    
    # 库存预警
    if state.low_stock_products:
        report_lines.append("【库存预警】")
        report_lines.append("-" * 80)
        for product in state.low_stock_products:
            report_lines.append(f"⚠️  {product['product_name']}")
            report_lines.append(f"   当前库存: {product['current_quantity']}")
            report_lines.append(f"   最小阈值: {product['min_threshold']}")
            report_lines.append(f"   缺货: {product['shortage']}")
        report_lines.append("")
    
    # AI分析
    if state.analysis_result:
        report_lines.append("【AI分析洞察】")
        report_lines.append("-" * 80)
        report_lines.append(state.analysis_result)
        report_lines.append("")
    
    report_lines.append("=" * 80)
    report_lines.append("报告结束")
    report_lines.append("=" * 80)
    
    report_content = "\n".join(report_lines)
    
    return GenerateSalesReportOutput(report_content=report_content)


# ==================== 节点5: 发送报告 ====================
@observe
def send_sales_report_node(
    state: SendSalesReportInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SendSalesReportOutput:
    """
    title: 发送销售报告
    desc: 将销售分析报告通过邮件发送给管理层
    integrations: 邮件
    """
    ctx = runtime.context

    # 检查是否有邮件配置
    if not HAS_WORKLOAD_IDENTITY:
        # 本地环境：模拟发送邮件
        return SendSalesReportOutput(
            report_sent=True,
            message=f"本地环境模拟发送销售报告：{state.report_type}报"
        )

    # 获取邮件配置
    try:
        client_obj = Client()
        email_credential = client_obj.get_integration_credential("integration-email-imap-smtp")
        email_config = json.loads(email_credential)
    except Exception as e:
        # 获取邮件配置失败，返回模拟结果
        return SendSalesReportOutput(
            report_sent=False,
            message=f"无法获取邮件配置: {str(e)}"
        )
    
    import smtplib
    import ssl
    from email.mime.text import MIMEText
    from email.header import Header
    from email.utils import formataddr, formatdate, make_msgid
    
    try:
        # 构建邮件内容
        report_type_cn = {"daily": "日", "weekly": "周", "monthly": "月"}.get(state.report_type, state.report_type)
        subject = f"销售数据分析报告 - {report_type_cn}报 - {datetime.now().strftime('%Y-%m-%d')}"
        
        html_content = state.report_content.replace("\n", "<br>")
        
        msg = MIMEText(html_content, "html", "utf-8")
        msg["From"] = formataddr(("数据分析系统", email_config["account"]))
        msg["To"] = ", ".join(state.email_recipients)
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
                state.email_recipients,
                msg.as_string()
            )
            server.quit()
        
        return SendSalesReportOutput(
            report_sent=True,
            message=f"已发送销售报告到 {len(state.email_recipients)} 位接收人"
        )
    except Exception as e:
        return SendSalesReportOutput(
            report_sent=False,
            message=f"发送报告失败: {str(e)}"
        )
