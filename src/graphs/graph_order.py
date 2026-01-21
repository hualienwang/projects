from langgraph.graph import StateGraph, END
from graphs.state_order import (
    OrderProcessingGlobalState,
    OrderProcessingInput,
    OrderProcessingOutput
)
from graphs.node_order import (
    validate_order_node,
    check_order_inventory_node,
    create_order_node,
    deduct_inventory_node,
    generate_shipping_order_node,
    notify_customer_node
)


# 条件判断函数：库存是否充足
def should_create_order(state: OrderProcessingGlobalState) -> str:
    """
    title: 判断是否可以创建订单
    desc: 根据库存检查结果决定是否创建订单
    """
    if state.inventory_status == "sufficient":
        return "创建订单"
    else:
        return "通知失败"


# 创建状态图
builder = StateGraph(
    OrderProcessingGlobalState,
    input_schema=OrderProcessingInput,
    output_schema=OrderProcessingOutput
)

# 添加节点
builder.add_node("validate_order", validate_order_node)
builder.add_node("check_inventory", check_order_inventory_node)
builder.add_node("create_order", create_order_node)
builder.add_node("deduct_inventory", deduct_inventory_node)
builder.add_node("generate_shipping", generate_shipping_order_node)
builder.add_node("notify_success", notify_customer_node)
builder.add_node("notify_failure", notify_customer_node)

# 设置入口点
builder.set_entry_point("validate_order")

# 添加边（线性流程 + 条件分支）
builder.add_edge("validate_order", "check_inventory")

# 条件分支：库存检查
builder.add_conditional_edges(
    source="check_inventory",
    path=should_create_order,
    path_map={
        "创建订单": "create_order",
        "通知失败": "notify_failure"
    }
)

# 库存充足的处理流程
builder.add_edge("create_order", "deduct_inventory")
builder.add_edge("deduct_inventory", "generate_shipping")
builder.add_edge("generate_shipping", "notify_success")
builder.add_edge("notify_success", END)

# 库存不足的处理流程
builder.add_edge("notify_failure", END)

# 编译图
main_graph = builder.compile()
