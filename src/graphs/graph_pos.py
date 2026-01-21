from langgraph.graph import StateGraph, END
from langchain_core.runnables import RunnableConfig
from langgraph.runtime import Runtime
from coze_coding_utils.runtime_ctx.context import Context

from graphs.state_pos import (
    POSGlobalState,
    POSGraphInput,
    POSGraphOutput
)
from graphs.node_pos import (
    scan_product_node,
    check_inventory_node,
    add_to_cart_node,
    calculate_order_node,
    create_order_node,
    deduct_inventory_node,
    generate_receipt_node,
    send_email_node
)


# ==================== 条件判断函数 ====================
def check_action_route(state: POSGlobalState) -> str:
    """
    title: 操作路由判断
    desc: 根据操作类型决定后续流程
    """
    action = state.action.lower() if state.action else ""
    
    if action == "scan":
        return "扫码识别"
    elif action == "checkout":
        return "结账处理"
    else:
        return "结束"


# ==================== 主图编排 ====================

# 创建状态图，指定工作流的入参和出参
builder = StateGraph(POSGlobalState, input_schema=POSGraphInput, output_schema=POSGraphOutput)

# 添加节点
builder.add_node("scan_product", scan_product_node)
builder.add_node("check_inventory", check_inventory_node)
builder.add_node("add_to_cart", add_to_cart_node)
builder.add_node("calculate_order", calculate_order_node)
builder.add_node("create_order", create_order_node)
builder.add_node("deduct_inventory", deduct_inventory_node)
builder.add_node("generate_receipt", generate_receipt_node)
builder.add_node("send_email", send_email_node)

# 设置入口点
builder.set_entry_point("scan_product")

# 添加条件分支：从扫码节点开始路由
builder.add_conditional_edges(
    source="scan_product",
    path=check_action_route,
    path_map={
        "扫码识别": "check_inventory",
        "结账处理": "calculate_order",
        "结束": END
    }
)

# 扫码流程：扫码识别 -> 检查库存 -> 添加到购物车
builder.add_edge("check_inventory", "add_to_cart")
builder.add_edge("add_to_cart", END)

# 结账流程：订单汇总 -> 创建订单 -> 扣减库存 -> 生成小票 -> 发送邮件
builder.add_edge("calculate_order", "create_order")
builder.add_edge("create_order", "deduct_inventory")
builder.add_edge("deduct_inventory", "generate_receipt")
builder.add_edge("generate_receipt", "send_email")
builder.add_edge("send_email", END)

# 编译图
pos_graph = builder.compile()
