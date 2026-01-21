from langgraph.graph import StateGraph, END
from graphs.state_procurement import (
    ProcurementGlobalState,
    ProcurementInput,
    ProcurementOutput
)
from graphs.node_procurement import (
    identify_procurement_needs_node,
    generate_procurement_plan_node,
    recommend_suppliers_node,
    generate_procurement_order_node,
    send_procurement_order_node
)


# 创建状态图
builder = StateGraph(
    ProcurementGlobalState,
    input_schema=ProcurementInput,
    output_schema=ProcurementOutput
)

# 添加节点
builder.add_node("identify_needs", identify_procurement_needs_node)
builder.add_node("generate_plan", generate_procurement_plan_node)
builder.add_node("recommend_suppliers", recommend_suppliers_node)
builder.add_node("generate_order", generate_procurement_order_node)
builder.add_node("send_order", send_procurement_order_node)

# 设置入口点
builder.set_entry_point("identify_needs")

# 添加边（线性流程）
builder.add_edge("identify_needs", "generate_plan")
builder.add_edge("generate_plan", "recommend_suppliers")
builder.add_edge("recommend_suppliers", "generate_order")
builder.add_edge("generate_order", "send_order")
builder.add_edge("send_order", END)

# 编译图
main_graph = builder.compile()
