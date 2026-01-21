from langgraph.graph import StateGraph, END
from graphs.state_sales import (
    SalesAnalysisGlobalState,
    SalesAnalysisInput,
    SalesAnalysisOutput
)
from graphs.node_sales import (
    collect_sales_data_node,
    analyze_sales_trend_node,
    ai_analyze_sales_node,
    generate_sales_report_node,
    send_sales_report_node
)


# 创建状态图
builder = StateGraph(
    SalesAnalysisGlobalState,
    input_schema=SalesAnalysisInput,
    output_schema=SalesAnalysisOutput
)

# 添加节点
builder.add_node("collect_sales_data", collect_sales_data_node)
builder.add_node("analyze_sales_trend", analyze_sales_trend_node)
builder.add_node("ai_analyze", ai_analyze_sales_node, metadata={"type": "agent", "llm_cfg": "config/sales_analysis_cfg.json"})
builder.add_node("generate_report", generate_sales_report_node)
builder.add_node("send_report", send_sales_report_node)

# 设置入口点
builder.set_entry_point("collect_sales_data")

# 添加边（线性流程）
builder.add_edge("collect_sales_data", "analyze_sales_trend")
builder.add_edge("analyze_sales_trend", "ai_analyze")
builder.add_edge("ai_analyze", "generate_report")
builder.add_edge("generate_report", "send_report")
builder.add_edge("send_report", END)

# 编译图
main_graph = builder.compile()
