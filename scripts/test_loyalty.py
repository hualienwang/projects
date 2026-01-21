"""测试客户忠诚度管理工作流"""
import sys
import os

os.chdir(os.getenv("COZE_WORKSPACE_PATH"))

from graphs.graph_loyalty import main_graph as loyalty_graph


def test_loyalty_workflow():
    """测试客户忠诚度管理工作流"""
    print("=" * 80)
    print("测试客户忠诚度管理工作流")
    print("=" * 80)
    
    # 测试数据：王五（普通会员，200积分），消费3000元后应该升级到金卡会员
    test_input = {
        "customer_id": 3,  # 王五
        "order_amount": 3000.0
    }
    
    print("\n🎯 测试场景：客户消费后积分和会员等级更新")
    print(f"   客户ID: {test_input['customer_id']}")
    print(f"   本次消费: ¥{test_input['order_amount']:.2f}")
    print()
    
    try:
        print("🔄 执行工作流...\n")
        
        results = []
        for chunk in loyalty_graph.stream(test_input):
            print(f"节点输出: {list(chunk.keys())[0]}")
            results.append(chunk)
        
        # 获取最终结果
        final_result = {}
        for result in results:
            for node_name, node_output in result.items():
                final_result.update(node_output)
        
        print("\n✅ 工作流执行完成！")
        print("\n📊 执行结果:")
        print(f"   客户姓名: {final_result.get('name', 'N/A')}")
        print(f"   当前会员等级: {final_result.get('current_level', 'N/A')}")
        print(f"   总积分: {final_result.get('total_points', 0)}")
        print(f"   是否升级: {final_result.get('level_upgraded', False)}")
        
        if final_result.get('loyalty_report'):
            print("\n📄 忠诚度报告:")
            print("-" * 80)
            print(final_result['loyalty_report'])
            print("-" * 80)
        
        return final_result
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_loyalty_workflow()
