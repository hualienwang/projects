from langgraph.graph import StateGraph, END
import os
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

# 導入訂單處理工作流
from graphs.graph_order import main_graph as order_processing_graph

# 通過環境變量選擇加載哪個工作流
# WORKFLOW_TYPE=order_processing 加載訂單處理工作流
# WORKFLOW_TYPE=stock_alert 加載庫存預警工作流
# 默認為 order_processing
# from pathlib import Path
# from dotenv import load_dotenv
# load_dotenv(Path(__file__).parent / ".env")

WORKFLOW_TYPE = os.getenv("WORKFLOW_TYPE", "order_processing")
# WORKFLOW_TYPE = os.getenv("WORKFLOW_TYPE", "stock_alert")
if WORKFLOW_TYPE == "stock_alert":
    # 使用庫存預警工作流
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
    print(f"✅ 已加載庫存預警工作流 (Stock Alert Workflow)")
else:
    # 使用訂單處理工作流（默認）
    main_graph = order_processing_graph
    print(f"✅ 已加載訂單處理工作流 (Order Processing Workflow)")
