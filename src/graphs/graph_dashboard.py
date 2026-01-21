from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state_dashboard import (
    DashboardGlobalState,
    DashboardGraphInput,
    DashboardGraphOutput
)

from graphs.node_dashboard import (
    permission_check_node,
    sales_trend_node,
    product_ranking_node,
    inventory_distribution_node,
    customer_analysis_node,
    supplier_stats_node
)


def check_permission_and_route(state: DashboardGlobalState) -> str:
    """
    title: 权限检查与路由
    desc: 检查权限后根据图表类型路由到相应的数据提取节点
    """
    # 先检查权限
    if not state.has_permission:
        return "无权限"
    
    # 根据图表类型返回对应的节点名称
    chart_type = state.chart_type
    
    if chart_type == "sales_trend":
        return "sales_trend"
    elif chart_type == "product_ranking":
        return "product_ranking"
    elif chart_type == "inventory_distribution":
        return "inventory_distribution"
    elif chart_type == "customer_analysis":
        return "customer_analysis"
    elif chart_type == "supplier_stats":
        return "supplier_stats"
    else:
        return "无权限"


# 创建状态图
builder = StateGraph(
    DashboardGlobalState,
    input_schema=DashboardGraphInput,
    output_schema=DashboardGraphOutput
)

# 添加节点
builder.add_node("permission_check", permission_check_node)
builder.add_node("sales_trend", sales_trend_node)
builder.add_node("product_ranking", product_ranking_node)
builder.add_node("inventory_distribution", inventory_distribution_node)
builder.add_node("customer_analysis", customer_analysis_node)
builder.add_node("supplier_stats", supplier_stats_node)

# 设置入口点
builder.set_entry_point("permission_check")

# 添加条件分支：权限检查后根据图表类型直接路由到对应的数据提取节点
builder.add_conditional_edges(
    source="permission_check",
    path=check_permission_and_route,
    path_map={
        "sales_trend": "sales_trend",
        "product_ranking": "product_ranking",
        "inventory_distribution": "inventory_distribution",
        "customer_analysis": "customer_analysis",
        "supplier_stats": "supplier_stats",
        "无权限": END
    }
)

# 所有图表节点执行完毕后结束
builder.add_edge("sales_trend", END)
builder.add_edge("product_ranking", END)
builder.add_edge("inventory_distribution", END)
builder.add_edge("customer_analysis", END)
builder.add_edge("supplier_stats", END)

# 编译图
main_graph = builder.compile()
