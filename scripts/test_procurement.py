"""测试供应商采购管理工作流"""
import sys
import os

os.chdir(os.getenv("COZE_WORKSPACE_PATH"))

from graphs.graph_procurement import main_graph as procurement_graph


def test_procurement_workflow():
    """测试供应商采购管理工作流"""
    print("=" * 80)
    print("测试供应商采购管理工作流")
    print("=" * 80)
    
    # 测试数据：检查所有低库存商品并生成采购计划
    test_input = {
        "check_all_low_stock": True
    }
    
    print("\n🛒 测试场景：自动生成采购计划")
    print(f"   检查所有低库存商品: {test_input['check_all_low_stock']}")
    print()
    
    try:
        print("🔄 执行工作流...\n")
        
        results = []
        for chunk in procurement_graph.stream(test_input):
            print(f"节点输出: {list(chunk.keys())[0]}")
            results.append(chunk)
        
        # 获取最终结果
        final_result = {}
        for result in results:
            for node_name, node_output in result.items():
                final_result.update(node_output)
        
        print("\n✅ 工作流执行完成！")
        print("\n📊 执行结果:")
        
        if final_result.get('low_stock_products'):
            print(f"\n📦 低库存商品 ({len(final_result['low_stock_products'])}个):")
            for i, p in enumerate(final_result['low_stock_products'][:5], 1):
                print(f"   {i}. {p['name']} - 当前库存: {p['current_quantity']}/{p['min_threshold']}")
        
        if final_result.get('procurement_plan'):
            print(f"\n🛍️  采购计划 ({len(final_result['procurement_plan'])}个商品):")
            for i, p in enumerate(final_result['procurement_plan'][:5], 1):
                print(f"   {i}. {p['name']} - 采购数量: {p['order_quantity']} - 成本: ¥{p['item_cost']:,.2f} ({p['priority']}优先级)")
        
        if final_result.get('procurement_order'):
            order = final_result['procurement_order']
            print(f"\n📄 采购单:")
            print(f"   采购单号: {order['order_no']}")
            print(f"   供应商: {order['supplier'].get('name', 'N/A')}")
            print(f"   采购商品数: {len(order['items'])}")
            print(f"   总成本: ¥{order['total_cost']:,.2f}")
            print(f"   预计交货: {order['estimated_delivery']}")
        
        print(f"\n📤 发送状态: {'✅ 已发送' if final_result.get('order_sent') else '❌ 未发送'}")
        
        return final_result
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_procurement_workflow()
