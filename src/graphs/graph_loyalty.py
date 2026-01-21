from langgraph.graph import StateGraph, END
from graphs.state_loyalty import (
    LoyaltyGlobalState,
    LoyaltyWorkflowInput,
    LoyaltyWorkflowOutput
)
from graphs.node_loyalty import (
    get_customer_info_node,
    calculate_points_node,
    check_member_level_node,
    update_member_level_node,
    generate_loyalty_report_node,
    send_loyalty_notification_node
)


# 条件判断函数：是否需要升级
def should_upgrade_level(state: LoyaltyGlobalState) -> str:
    """
    title: 判断是否需要升级
    desc: 根据会员等级变化决定是否执行升级流程
    """
    if state.level_upgraded:
        return "升级并通知"
    else:
        return "生成报告"


# 创建状态图
builder = StateGraph(
    LoyaltyGlobalState,
    input_schema=LoyaltyWorkflowInput,
    output_schema=LoyaltyWorkflowOutput
)

# 添加节点
builder.add_node("get_customer_info", get_customer_info_node)
builder.add_node("calculate_points", calculate_points_node)
builder.add_node("check_level", check_member_level_node)
builder.add_node("update_level", update_member_level_node)
builder.add_node("generate_report", generate_loyalty_report_node)
builder.add_node("send_notification", send_loyalty_notification_node)

# 设置入口点
builder.set_entry_point("get_customer_info")

# 添加边
builder.add_edge("get_customer_info", "calculate_points")
builder.add_edge("calculate_points", "check_level")

# 条件分支：判断是否需要升级
builder.add_conditional_edges(
    source="check_level",
    path=should_upgrade_level,
    path_map={
        "升级并通知": "update_level",
        "生成报告": "generate_report"
    }
)

# 升级流程
builder.add_edge("update_level", "generate_report")
builder.add_edge("generate_report", "send_notification")
builder.add_edge("send_notification", END)

# 编译图
main_graph = builder.compile()
