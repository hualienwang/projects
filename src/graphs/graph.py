from langgraph.graph import StateGraph, END
from graphs.state import (
    GlobalState,
    StockAlertWorkflowInput,
    StockAlertWorkflowOutput
)
from graphs.node import (
    check_inventory_node,
    analyze_alert_node,
    generate_report_node,
    send_email_node,
    record_alert_node
)


# 创建状态图，指定工作流的入参和出参
builder = StateGraph(
    GlobalState,
    input_schema=StockAlertWorkflowInput,
    output_schema=StockAlertWorkflowOutput
)

# 添加节点
builder.add_node("check_inventory", check_inventory_node)
builder.add_node("analyze_alert", analyze_alert_node, metadata={"type": "agent", "llm_cfg": "config/stock_alert_analysis_cfg.json"})
builder.add_node("generate_report", generate_report_node)
builder.add_node("send_email", send_email_node)
builder.add_node("record_alert", record_alert_node)

# 设置入口点
builder.set_entry_point("check_inventory")

# 添加边（线性流程）
builder.add_edge("check_inventory", "analyze_alert")
builder.add_edge("analyze_alert", "generate_report")
builder.add_edge("generate_report", "send_email")
builder.add_edge("send_email", "record_alert")
builder.add_edge("record_alert", END)

# 编译图
main_graph = builder.compile()
