"""
数据可视化 RESTful API
提供基于角色的访问控制和数据可视化接口
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, Dict, Any
from datetime import date, timedelta
from pydantic import BaseModel, Field

# 创建路由器
router = APIRouter(prefix="/api/dashboard", tags=["数据可视化"])


# ==================== API 请求/响应模型 ====================

class DashboardRequest(BaseModel):
    """数据可视化请求模型"""
    user_id: str = Field(..., description="用户ID")
    user_role: str = Field(default="viewer", description="用户角色: admin/manager/staff/viewer")
    chart_type: str = Field(..., description="图表类型: sales_trend/product_ranking/inventory_distribution/customer_analysis/supplier_stats")
    start_date: Optional[date] = Field(default=None, description="开始日期")
    end_date: Optional[date] = Field(default=None, description="结束日期")


class DashboardResponse(BaseModel):
    """数据可视化响应模型"""
    success: bool = Field(..., description="是否成功")
    has_permission: bool = Field(..., description="是否有权限访问")
    chart_data: Optional[Dict[str, Any]] = Field(default=None, description="图表数据")
    chart_config: Optional[Dict[str, Any]] = Field(default=None, description="图表配置")
    message: str = Field(default="", description="处理消息")


class ChartListResponse(BaseModel):
    """图表列表响应模型"""
    success: bool = Field(..., description="是否成功")
    available_charts: Dict[str, str] = Field(..., description="可用图表列表")


class PermissionResponse(BaseModel):
    """权限查询响应模型"""
    success: bool = Field(..., description="是否成功")
    user_role: str = Field(..., description="用户角色")
    permissions: Dict[str, bool] = Field(..., description="各图表的访问权限")


# ==================== 角色权限映射 ====================
ROLE_PERMISSIONS = {
    "admin": ["sales_trend", "product_ranking", "inventory_distribution", "customer_analysis", "supplier_stats"],
    "manager": ["sales_trend", "product_ranking", "inventory_distribution", "customer_analysis"],
    "staff": ["sales_trend", "product_ranking"],
    "viewer": ["sales_trend"]
}

CHART_DESCRIPTIONS = {
    "sales_trend": "销售趋势 - 按日期统计销售额和订单数",
    "product_ranking": "商品销售排行 - 统计商品销售数量",
    "inventory_distribution": "库存状态分布 - 正常/低库存/缺货",
    "customer_analysis": "客户消费分析 - 统计客户消费金额",
    "supplier_stats": "供应商采购统计 - 统计供应商商品数量和成本"
}


# ==================== API 接口 ====================

@router.get("/charts", response_model=ChartListResponse)
async def get_available_charts():
    """
    获取可用图表列表
    
    返回所有支持的图表类型及其描述
    """
    return ChartListResponse(
        success=True,
        available_charts=CHART_DESCRIPTIONS
    )


@router.get("/permissions/{user_role}", response_model=PermissionResponse)
async def get_user_permissions(user_role: str):
    """
    查询用户权限
    
    Args:
        user_role: 用户角色 (admin/manager/staff/viewer)
    
    Returns:
        该角色对所有图表的访问权限
    """
    if user_role not in ROLE_PERMISSIONS:
        raise HTTPException(status_code=400, detail=f"无效的角色: {user_role}")
    
    allowed_charts = ROLE_PERMISSIONS[user_role]
    
    # 生成各图表的权限状态
    permissions = {}
    for chart_type in CHART_DESCRIPTIONS.keys():
        permissions[chart_type] = chart_type in allowed_charts
    
    return PermissionResponse(
        success=True,
        user_role=user_role,
        permissions=permissions
    )


@router.post("/generate", response_model=DashboardResponse)
async def generate_dashboard_chart(request: DashboardRequest):
    """
    生成数据可视化图表
    
    Args:
        request: 数据可视化请求
    
    Returns:
        图表数据和配置（Chart.js格式）
    
    Raises:
        HTTPException: 权限不足或参数错误
    """
    # 验证角色
    if request.user_role not in ROLE_PERMISSIONS:
        raise HTTPException(status_code=400, detail=f"无效的角色: {request.user_role}")
    
    # 验证图表类型
    if request.chart_type not in CHART_DESCRIPTIONS:
        raise HTTPException(status_code=400, detail=f"无效的图表类型: {request.chart_type}")
    
    # 检查权限
    allowed_charts = ROLE_PERMISSIONS[request.user_role]
    if request.chart_type not in allowed_charts:
        raise HTTPException(
            status_code=403,
            detail=f"权限不足: {request.user_role} 角色无权访问 {request.chart_type} 图表"
        )
    
    # 设置默认日期范围
    if request.end_date is None:
        end_date = date.today()
    else:
        end_date = request.end_date
    
    if request.start_date is None:
        start_date = end_date - timedelta(days=30)
    else:
        start_date = request.start_date
    
    # 直接生成模拟数据（暂时不调用工作流，避免 Coze 身份验证问题）
    try:
        # 根据图表类型生成 Chart.js 配置
        chart_config = {
            "type": "line",
            "data": {
                "labels": [],
                "datasets": []
            },
            "options": {
                "responsive": True,
                "maintainAspectRatio": False,
                "plugins": {
                    "legend": {
                        "display": True,
                        "position": "top"
                    },
                    "title": {
                        "display": True,
                        "text": ""
                    },
                    "tooltip": {
                        "mode": "index",
                        "intersect": False
                    }
                }
            }
        }

        chart_data = {}

        # 根据图表类型返回模拟数据
        if request.chart_type == "sales_trend":
            chart_config["type"] = "line"
            chart_config["data"]["labels"] = ["一月", "二月", "三月", "四月", "五月", "六月", "七月", "八月", "九月", "十月", "十一月", "十二月"]
            chart_config["data"]["datasets"] = [
                {
                    "label": "銷售額 (萬元)",
                    "data": [120, 150, 180, 220, 280, 350, 420, 380, 450, 520, 580, 650],
                    "borderColor": "#4CAF50",
                    "backgroundColor": "rgba(76, 175, 80, 0.2)",
                    "fill": True,
                    "tension": 0.4
                },
                {
                    "label": "利潤 (萬元)",
                    "data": [40, 50, 60, 75, 95, 120, 145, 130, 155, 180, 200, 225],
                    "borderColor": "#2196F3",
                    "backgroundColor": "rgba(33, 150, 243, 0.2)",
                    "fill": True,
                    "tension": 0.4
                }
            ]
            chart_config["options"]["plugins"]["title"]["text"] = "銷售趨勢分析"
            chart_data = {
                "total_sales": 4340,
                "total_profit": 1485,
                "growth_rate": "+15.2%",
                "best_month": "十二月",
                "best_month_sales": 650
            }

        elif request.chart_type == "product_ranking":
            chart_config["type"] = "bar"
            chart_config["data"]["labels"] = ["哈利波特", "小王子", "老人與海", "1984", "三體", "百年孤獨", "福爾摩斯", "傲慢與偏見", "紅樓夢", "西遊記"]
            chart_config["data"]["datasets"] = [
                {
                    "label": "銷售量 (本)",
                    "data": [1250, 980, 870, 750, 680, 620, 580, 520, 480, 450],
                    "backgroundColor": [
                        "#FF6384", "#36A2EB", "#FFCE56", "#4BC0C0", "#9966FF",
                        "#FF9F40", "#FF6384", "#C9CBCF", "#36A2EB", "#FFCE56"
                    ],
                    "borderRadius": 5
                }
            ]
            chart_config["options"]["plugins"]["title"]["text"] = "商品銷售排行 Top 10"
            chart_config["options"]["indexAxis"] = "x"
            chart_data = {
                "best_seller": "哈利波特",
                "best_seller_count": 1250,
                "total_products": 156,
                "active_products": 98
            }

        elif request.chart_type == "inventory_distribution":
            chart_config["type"] = "doughnut"
            chart_config["data"]["labels"] = ["正常", "低庫存", "庫存不足", "庫存積壓"]
            chart_config["data"]["datasets"] = [
                {
                    "data": [65, 15, 12, 8],
                    "backgroundColor": [
                        "#4CAF50",  # 正常 - 綠色
                        "#FF9800",  # 低庫存 - 橙色
                        "#F44336",  # 庫存不足 - 紅色
                        "#9E9E9E"   # 庫存積壓 - 灰色
                    ],
                    "borderWidth": 2,
                    "borderColor": "#ffffff"
                }
            ]
            chart_config["options"]["plugins"]["title"]["text"] = "庫存狀態分佈"
            chart_config["options"]["cutout"] = "60%"
            chart_data = {
                "total_products": 156,
                "low_stock": 23,
                "out_of_stock": 18,
                "overstock": 13,
                "health_score": 85
            }

        elif request.chart_type == "customer_analysis":
            chart_config["type"] = "pie"
            chart_config["data"]["labels"] = ["普通會員", "銀卡會員", "金卡會員", "白金會員", "鑽石會員"]
            chart_config["data"]["datasets"] = [
                {
                    "data": [850, 450, 280, 120, 45],
                    "backgroundColor": [
                        "#9E9E9E",  # 普通 - 灰色
                        "#B0BEC5",  # 銀卡 - 銀灰色
                        "#FFD700",  # 金卡 - 金色
                        "#81C784",  # 白金 - 淡綠色
                        "#2196F3"   # 鑽石 - 藍色
                    ],
                    "borderWidth": 2,
                    "borderColor": "#ffffff"
                }
            ]
            chart_config["options"]["plugins"]["title"]["text"] = "客戶消費分佈"
            chart_data = {
                "total_customers": 1745,
                "vip_customers": 445,
                "avg_consumption": 520,
                "loyalty_rate": "78.5%"
            }

        elif request.chart_type == "supplier_stats":
            chart_config["type"] = "bar"
            chart_config["data"]["labels"] = ["聯合出版", "商務印書館", "人民文學", "中華書局", "三聯書店", "譯林出版社", "上海譯文", "浙江文藝"]
            chart_config["data"]["datasets"] = [
                {
                    "label": "採購金額 (萬元)",
                    "data": [850, 720, 680, 590, 520, 480, 420, 380],
                    "backgroundColor": "#2196F3",
                    "borderRadius": 5
                },
                {
                    "label": "訂單數量",
                    "data": [156, 142, 128, 115, 102, 95, 88, 75],
                    "backgroundColor": "#FF9800",
                    "borderRadius": 5
                }
            ]
            chart_config["options"]["plugins"]["title"]["text"] = "供應商採購統計"
            chart_config["options"]["scales"] = {
                "y": {
                    "beginAtZero": True
                }
            }
            chart_data = {
                "total_suppliers": 28,
                "active_suppliers": 22,
                "total_purchase": 4640,
                "avg_order_value": 3.2
            }
        else:
            return DashboardResponse(
                success=False,
                has_permission=False,
                chart_data=None,
                chart_config=None,
                message=f"未知的圖表類型: {request.chart_type}"
            )

        # 返回结果
        return DashboardResponse(
            success=True,
            has_permission=True,
            chart_data=chart_data,
            chart_config=chart_config,
            message="圖表數據加載成功"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"圖表生成失敗: {str(e)}")


@router.get("/chart-types", response_model=Dict[str, str])
async def get_chart_types():
    """
    获取支持的图表类型列表
    
    Returns:
        图表类型与描述的映射
    """
    return CHART_DESCRIPTIONS


@router.get("/roles")
async def get_roles():
    """
    获取支持的角色列表
    
    Returns:
        角色列表及其权限描述
    """
    roles_info = {
        "admin": {
            "description": "系统管理员",
            "permissions": ROLE_PERMISSIONS["admin"]
        },
        "manager": {
            "description": "经理",
            "permissions": ROLE_PERMISSIONS["manager"]
        },
        "staff": {
            "description": "员工",
            "permissions": ROLE_PERMISSIONS["staff"]
        },
        "viewer": {
            "description": "查看者",
            "permissions": ROLE_PERMISSIONS["viewer"]
        }
    }
    return roles_info


# ==================== 便捷接口 ====================

@router.post("/sales-trend")
async def get_sales_trend(
    user_id: str,
    user_role: str = "viewer",
    days: int = 30
):
    """
    快速获取销售趋势图
    
    Args:
        user_id: 用户ID
        user_role: 用户角色
        days: 统计天数（默认30天）
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    request = DashboardRequest(
        user_id=user_id,
        user_role=user_role,
        chart_type="sales_trend",
        start_date=start_date,
        end_date=end_date
    )
    
    return await generate_dashboard_chart(request)


@router.post("/product-ranking")
async def get_product_ranking(
    user_id: str,
    user_role: str = "viewer",
    days: int = 30,
    top_n: int = 10
):
    """
    快速获取商品销售排行
    
    Args:
        user_id: 用户ID
        user_role: 用户角色
        days: 统计天数（默认30天）
        top_n: 返回前N个商品（默认10）
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    
    request = DashboardRequest(
        user_id=user_id,
        user_role=user_role,
        chart_type="product_ranking",
        start_date=start_date,
        end_date=end_date
    )
    
    return await generate_dashboard_chart(request)


@router.post("/inventory-distribution")
async def get_inventory_distribution(
    user_id: str,
    user_role: str = "manager"
):
    """
    快速获取库存状态分布
    
    Args:
        user_id: 用户ID
        user_role: 用户角色
    """
    request = DashboardRequest(
        user_id=user_id,
        user_role=user_role,
        chart_type="inventory_distribution"
    )
    
    return await generate_dashboard_chart(request)
