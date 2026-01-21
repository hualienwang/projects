from typing import Dict, Any, List, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc
from decimal import Decimal

from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from storage.database.db import get_session
from storage.database.shared.model import (
    Order, OrderItem, Product, Inventory, Customer, Supplier
)

from graphs.state_dashboard import (
    PermissionCheckInput, PermissionCheckOutput,
    SalesTrendInput, SalesTrendOutput,
    ProductRankingInput, ProductRankingOutput,
    InventoryDistributionInput, InventoryDistributionOutput,
    CustomerAnalysisInput, CustomerAnalysisOutput,
    SupplierStatsInput, SupplierStatsOutput,
    ChartConfigGenerationInput, ChartConfigGenerationOutput
)


# ==================== 权限配置 ====================
# 角色权限配置
ROLE_PERMISSIONS = {
    "admin": ["sales_trend", "product_ranking", "inventory_distribution", "customer_analysis", "supplier_stats"],
    "manager": ["sales_trend", "product_ranking", "inventory_distribution", "customer_analysis"],
    "staff": ["sales_trend", "product_ranking"],
    "viewer": ["sales_trend"]
}


def permission_check_node(
    state: PermissionCheckInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> PermissionCheckOutput:
    """
    title: 权限检查
    desc: 检查用户是否有权限访问请求的图表类型
    integrations: 无
    """
    ctx = runtime.context
    
    user_role = state.user_role.lower()
    chart_type = state.chart_type
    
    # 检查角色是否有权限访问该图表
    allowed_charts = ROLE_PERMISSIONS.get(user_role, [])
    
    if chart_type in allowed_charts:
        return PermissionCheckOutput(
            has_permission=True,
            permission_message=f"权限验证通过：{user_role} 角色可以访问 {chart_type} 图表"
        )
    else:
        return PermissionCheckOutput(
            has_permission=False,
            permission_message=f"权限不足：{user_role} 角色无权访问 {chart_type} 图表。允许的图表：{', '.join(allowed_charts)}"
        )


def sales_trend_node(
    state: SalesTrendInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SalesTrendOutput:
    """
    title: 销售趋势数据提取
    desc: 从数据库提取销售趋势数据（按日期统计订单金额）
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 设置默认日期范围（最近30天）
        if state.end_date is None:
            end_date = date.today()
        else:
            end_date = state.end_date
        
        if state.start_date is None:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = state.start_date
        
        # 查询每日销售数据
        query = db.query(
            func.date(Order.created_at).label('date'),
            func.sum(Order.total_amount).label('total_amount'),
            func.count(Order.id).label('order_count')
        ).filter(
            and_(
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date,
                Order.status.in_(['paid', 'shipped', 'completed'])
            )
        ).group_by(
            func.date(Order.created_at)
        ).order_by(
            func.date(Order.created_at)
        )
        
        results = query.all()
        
        # 准备数据
        dates = []
        amounts = []
        counts = []
        
        for row in results:
            dates.append(row.date.strftime('%Y-%m-%d'))
            amounts.append(float(row.total_amount) if row.total_amount else 0.0)
            counts.append(row.order_count)
        
        raw_data = {
            "dates": dates,
            "amounts": amounts,
            "counts": counts
        }
        
        # 生成Chart.js配置
        chart_data = {
            "labels": dates,
            "datasets": [
                {
                    "label": "销售额 (元)",
                    "data": amounts,
                    "borderColor": "rgb(75, 192, 192)",
                    "backgroundColor": "rgba(75, 192, 192, 0.2)",
                    "tension": 0.1,
                    "fill": True
                },
                {
                    "label": "订单数",
                    "data": counts,
                    "borderColor": "rgb(255, 99, 132)",
                    "backgroundColor": "rgba(255, 99, 132, 0.2)",
                    "tension": 0.1,
                    "fill": True,
                    "yAxisID": "y1"
                }
            ]
        }
        
        chart_config = {
            "type": "line",
            "data": chart_data,
            "options": {
                "responsive": True,
                "interaction": {
                    "mode": "index",
                    "intersect": False
                },
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"销售趋势 ({start_date} ~ {end_date})"
                    },
                    "tooltip": {
                        "enabled": True,
                        "mode": "index",
                        "intersect": False
                    }
                },
                "scales": {
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "title": {
                            "display": True,
                            "text": "销售额 (元)"
                        }
                    },
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "title": {
                            "display": True,
                            "text": "订单数"
                        },
                        "grid": {
                            "drawOnChartArea": False
                        }
                    }
                }
            }
        }
        
        return SalesTrendOutput(chart_data=chart_data, chart_config=chart_config)
        
    finally:
        db.close()


def product_ranking_node(
    state: ProductRankingInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> ProductRankingOutput:
    """
    title: 商品销售排行
    desc: 统计商品销售数量排行（Top N）
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 设置默认日期范围
        if state.end_date is None:
            end_date = date.today()
        else:
            end_date = state.end_date
        
        if state.start_date is None:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = state.start_date
        
        top_n = state.top_n
        
        # 查询商品销售排行
        query = db.query(
            Product.name.label('product_name'),
            func.sum(OrderItem.quantity).label('total_quantity'),
            func.sum(OrderItem.subtotal).label('total_amount')
        ).join(
            OrderItem, Product.id == OrderItem.product_id
        ).join(
            Order, OrderItem.order_id == Order.id
        ).filter(
            and_(
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date,
                Order.status.in_(['paid', 'shipped', 'completed'])
            )
        ).group_by(
            Product.id,
            Product.name
        ).order_by(
            desc('total_quantity')
        ).limit(top_n)
        
        results = query.all()
        
        # 准备数据
        product_names = []
        quantities = []
        amounts = []
        
        for row in results:
            product_names.append(row.product_name)
            quantities.append(row.total_quantity)
            amounts.append(float(row.total_amount) if row.total_amount else 0.0)
        
        # 生成Chart.js配置（柱状图）
        chart_data = {
            "labels": product_names,
            "datasets": [
                {
                    "label": "销售数量",
                    "data": quantities,
                    "backgroundColor": "rgba(54, 162, 235, 0.8)",
                    "borderColor": "rgba(54, 162, 235, 1)",
                    "borderWidth": 1
                }
            ]
        }
        
        chart_config = {
            "type": "bar",
            "data": chart_data,
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"商品销售排行 Top {top_n} ({start_date} ~ {end_date})"
                    },
                    "tooltip": {
                        "enabled": True
                    }
                },
                "scales": {
                    "y": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": "销售数量"
                        }
                    }
                }
            }
        }
        
        return ProductRankingOutput(chart_data=chart_data, chart_config=chart_config)
        
    finally:
        db.close()


def inventory_distribution_node(
    state: InventoryDistributionInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> InventoryDistributionOutput:
    """
    title: 库存状态分布
    desc: 统计库存状态分布（正常、低库存、缺货）
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 查询库存状态分布
        results = db.query(
            Inventory.quantity,
            Inventory.min_stock_threshold
        ).all()
        
        # 统计库存状态
        normal = 0      # 正常库存
        low = 0         # 低库存预警
        out_of_stock = 0  # 缺货
        
        for row in results:
            quantity = row.quantity
            threshold = row.min_stock_threshold
            
            if quantity == 0:
                out_of_stock += 1
            elif quantity < threshold:
                low += 1
            else:
                normal += 1
        
        # 生成Chart.js配置（饼图）
        chart_data = {
            "labels": ["正常库存", "低库存预警", "缺货"],
            "datasets": [
                {
                    "data": [normal, low, out_of_stock],
                    "backgroundColor": [
                        "rgba(75, 192, 192, 0.8)",  # 绿色 - 正常
                        "rgba(255, 206, 86, 0.8)",  # 黄色 - 低库存
                        "rgba(255, 99, 132, 0.8)"   # 红色 - 缺货
                    ],
                    "borderColor": [
                        "rgba(75, 192, 192, 1)",
                        "rgba(255, 206, 86, 1)",
                        "rgba(255, 99, 132, 1)"
                    ],
                    "borderWidth": 1
                }
            ]
        }
        
        chart_config = {
            "type": "pie",
            "data": chart_data,
            "options": {
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "库存状态分布"
                    },
                    "tooltip": {
                        "enabled": True,
                        "callbacks": {
                            "label": "function(context) { return context.label + ': ' + context.raw + '个商品'; }"
                        }
                    },
                    "legend": {
                        "position": "bottom"
                    }
                }
            }
        }
        
        return InventoryDistributionOutput(chart_data=chart_data, chart_config=chart_config)
        
    finally:
        db.close()


def customer_analysis_node(
    state: CustomerAnalysisInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> CustomerAnalysisOutput:
    """
    title: 客户消费分析
    desc: 统计客户消费金额排行（Top N）
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 设置默认日期范围
        if state.end_date is None:
            end_date = date.today()
        else:
            end_date = state.end_date
        
        if state.start_date is None:
            start_date = end_date - timedelta(days=30)
        else:
            start_date = state.start_date
        
        top_n = state.top_n
        
        # 查询客户消费排行
        query = db.query(
            Customer.name.label('customer_name'),
            func.sum(Order.total_amount).label('total_amount'),
            func.count(Order.id).label('order_count')
        ).join(
            Order, Customer.id == Order.customer_id
        ).filter(
            and_(
                func.date(Order.created_at) >= start_date,
                func.date(Order.created_at) <= end_date,
                Order.status.in_(['paid', 'shipped', 'completed'])
            )
        ).group_by(
            Customer.id,
            Customer.name
        ).order_by(
            desc('total_amount')
        ).limit(top_n)
        
        results = query.all()
        
        # 准备数据
        customer_names = []
        amounts = []
        counts = []
        
        for row in results:
            customer_names.append(row.customer_name)
            amounts.append(float(row.total_amount) if row.total_amount else 0.0)
            counts.append(row.order_count)
        
        # 生成Chart.js配置（水平柱状图）
        chart_data = {
            "labels": customer_names,
            "datasets": [
                {
                    "label": "消费金额 (元)",
                    "data": amounts,
                    "backgroundColor": "rgba(153, 102, 255, 0.8)",
                    "borderColor": "rgba(153, 102, 255, 1)",
                    "borderWidth": 1
                }
            ]
        }
        
        chart_config = {
            "type": "bar",
            "data": chart_data,
            "options": {
                "indexAxis": "y",
                "responsive": True,
                "plugins": {
                    "title": {
                        "display": True,
                        "text": f"客户消费排行 Top {top_n} ({start_date} ~ {end_date})"
                    },
                    "tooltip": {
                        "enabled": True
                    }
                },
                "scales": {
                    "x": {
                        "beginAtZero": True,
                        "title": {
                            "display": True,
                            "text": "消费金额 (元)"
                        }
                    }
                }
            }
        }
        
        return CustomerAnalysisOutput(chart_data=chart_data, chart_config=chart_config)
        
    finally:
        db.close()


def supplier_stats_node(
    state: SupplierStatsInput,
    config: RunnableConfig,
    runtime: Runtime[Context]
) -> SupplierStatsOutput:
    """
    title: 供应商采购统计
    desc: 统计各供应商的商品数量和成本
    integrations: 数据库
    """
    ctx = runtime.context
    db = get_session()
    
    try:
        # 查询供应商统计（商品数量和总成本）
        query = db.query(
            Supplier.name.label('supplier_name'),
            func.count(Product.id).label('product_count'),
            func.sum(Product.cost).label('total_cost')
        ).join(
            Product, Supplier.id == Product.supplier_id
        ).filter(
            Supplier.is_active == True
        ).group_by(
            Supplier.id,
            Supplier.name
        ).order_by(
            desc('product_count')
        )
        
        results = query.all()
        
        # 准备数据
        supplier_names = []
        product_counts = []
        costs = []
        
        for row in results:
            supplier_names.append(row.supplier_name)
            product_counts.append(row.product_count)
            costs.append(float(row.total_cost) if row.total_cost else 0.0)
        
        # 生成Chart.js配置（混合图表）
        chart_data = {
            "labels": supplier_names,
            "datasets": [
                {
                    "label": "商品数量",
                    "data": product_counts,
                    "backgroundColor": "rgba(255, 159, 64, 0.8)",
                    "borderColor": "rgba(255, 159, 64, 1)",
                    "borderWidth": 1,
                    "yAxisID": "y"
                },
                {
                    "label": "总成本 (元)",
                    "data": costs,
                    "type": "line",
                    "borderColor": "rgb(201, 203, 207)",
                    "backgroundColor": "rgba(201, 203, 207, 0.2)",
                    "tension": 0.1,
                    "yAxisID": "y1"
                }
            ]
        }
        
        chart_config = {
            "type": "bar",
            "data": chart_data,
            "options": {
                "responsive": True,
                "interaction": {
                    "mode": "index",
                    "intersect": False
                },
                "plugins": {
                    "title": {
                        "display": True,
                        "text": "供应商采购统计"
                    },
                    "tooltip": {
                        "enabled": True,
                        "mode": "index",
                        "intersect": False
                    }
                },
                "scales": {
                    "y": {
                        "type": "linear",
                        "display": True,
                        "position": "left",
                        "title": {
                            "display": True,
                            "text": "商品数量"
                        },
                        "beginAtZero": True
                    },
                    "y1": {
                        "type": "linear",
                        "display": True,
                        "position": "right",
                        "title": {
                            "display": True,
                            "text": "总成本 (元)"
                        },
                        "grid": {
                            "drawOnChartArea": False
                        },
                        "beginAtZero": True
                    }
                }
            }
        }
        
        return SupplierStatsOutput(chart_data=chart_data, chart_config=chart_config)
        
    finally:
        db.close()
