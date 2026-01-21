"""测试订单处理工作流"""
import sys
import os

os.chdir(os.getenv("COZE_WORKSPACE_PATH"))

from langgraph.graph.state import CompiledStateGraph
from graphs.graph_order import main_graph as order_graph


def test_order_processing():
    """测试订单处理工作流"""
    print("=" * 80)
    print("测试订单处理工作流")
    print("=" * 80)
    
    # 测试数据：购买 1 本 Python 程式设计（库存 1，足够）
    test_input = {
        "customer_id": 1,  # 張三
        "items": [
            {
                "product_id": 1,
                "quantity": 1
            }
        ]
    }
    
    print("\n📦 测试场景：购买 1 本 'Python 程式設計：從入門到精通'")
    print(f"   客户ID: {test_input['customer_id']}")
    print(f"   商品: 商品ID {test_input['items'][0]['product_id']} x {test_input['items'][0]['quantity']}")
    print()
    
    try:
        # 使用 stream 模式获取详细输出
        print("🔄 执行工作流...\n")
        
        results = []
        for chunk in order_graph.stream(test_input):
            print(f"节点输出: {chunk}")
            results.append(chunk)
            print()
        
        # 获取最终结果
        final_result = {}
        for result in results:
            final_result.update(result)
        
        print("\n✅ 工作流执行完成！")
        print("\n📊 执行结果:")
        print(f"   订单编号: {final_result.get('order_no', 'N/A')}")
        print(f"   订单状态: {final_result.get('status', 'N/A')}")
        print(f"   订单金额: ¥{final_result.get('total_amount', 0):.2f}")
        print(f"   消息: {final_result.get('message', 'N/A')}")
        
        print("\n📋 详细信息:")
        if final_result.get('order_no'):
            print(f"   ✓ 订单已创建: {final_result['order_no']}")
        if final_result.get('inventory_updated'):
            print(f"   ✓ 库存已扣减")
        if final_result.get('order_created'):
            print(f"   ✓ 订单创建状态: {final_result['order_created']}")
        
        return final_result
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_order_processing()
