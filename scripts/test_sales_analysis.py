"""测试销售数据分析工作流"""
import sys
import os

os.chdir(os.getenv("COZE_WORKSPACE_PATH"))

from graphs.graph_sales import main_graph as sales_graph


def test_sales_analysis_workflow():
    """测试销售数据分析工作流"""
    print("=" * 80)
    print("测试销售数据分析工作流")
    print("=" * 80)
    
    # 测试数据：生成日销售报告
    test_input = {
        "report_type": "daily",
        "email_recipients": ["manager@qionglin.com.tw"]
    }
    
    print("\n📊 测试场景：生成日销售分析报告")
    print(f"   报告类型: {test_input['report_type']}")
    print()
    
    try:
        print("🔄 执行工作流...\n")
        
        results = []
        for chunk in sales_graph.stream(test_input):
            print(f"节点输出: {list(chunk.keys())[0]}")
            results.append(chunk)
        
        # 获取最终结果
        final_result = {}
        for result in results:
            for node_name, node_output in result.items():
                final_result.update(node_output)
        
        print("\n✅ 工作流执行完成！")
        print("\n📊 执行结果:")
        print(f"   总销售额: ¥{final_result.get('total_sales', 0):,.2f}")
        print(f"   总订单数: {final_result.get('total_orders', 0)}")
        print(f"   日期范围: {final_result.get('date_range', 'N/A')}")
        
        if final_result.get('report_content'):
            print("\n📄 销售分析报告:")
            print("-" * 80)
            print(final_result['report_content'][:1000])  # 只显示前1000字符
            print("-" * 80)
        
        if final_result.get('top_products'):
            print("\n🏆 热销商品:")
            for i, p in enumerate(final_result['top_products'][:3], 1):
                print(f"   {i}. {p['product_name']} - 销量: {p['total_quantity']}")
        
        return final_result
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    test_sales_analysis_workflow()
