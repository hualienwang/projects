"""测试POS系统工作流（独立测试脚本）"""
import sys
import os

os.chdir(os.getenv("COZE_WORKSPACE_PATH"))

from graphs.graph_pos import pos_graph
from coze_coding_utils.runtime_ctx.context import Context, new_context
from langchain_core.runnables import RunnableConfig


def test_scan_product():
    """测试扫码添加商品功能"""
    print("=" * 80)
    print("测试POS系统 - 扫码添加商品")
    print("=" * 80)
    
    # 测试数据：扫描商品条码
    test_input = {
        "action": "scan",
        "scanned_code": "9789571468753"  # 假设这是一个有效的ISBN
    }
    
    print("\n📱 测试场景：扫描商品条码")
    print(f"   操作: {test_input['action']}")
    print(f"   条码: {test_input['scanned_code']}")
    print()
    
    try:
        print("🔄 执行工作流...\n")
        
        results = []
        for chunk in pos_graph.stream(test_input):
            print(f"节点输出: {chunk}")
            results.append(chunk)
            print()
        
        final_result = {}
        for result in results:
            final_result.update(result)
        
        print("\n✅ 工作流执行完成！")
        print(f"   最终结果: {final_result}")
        return final_result
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_checkout():
    """测试结账功能"""
    print("=" * 80)
    print("测试POS系统 - 结账")
    print("=" * 80)
    
    # 测试数据：结账
    test_input = {
        "action": "checkout",
        "cart_items": [
            {
                "product_id": 1,
                "name": "Python 程式設計：從入門到精通",
                "author": "王小明",
                "isbn": "9789571468753",
                "quantity": 1,
                "unit_price": 580.0,
                "subtotal": 580.0
            }
        ],
        "customer_id": 1
    }
    
    print("\n💰 测试场景：结账")
    print(f"   操作: {test_input['action']}")
    print(f"   购物车商品数: {len(test_input['cart_items'])}")
    print(f"   客户ID: {test_input['customer_id']}")
    print()
    
    try:
        print("🔄 执行工作流...\n")
        
        results = []
        for chunk in pos_graph.stream(test_input):
            print(f"节点输出: {chunk}")
            results.append(chunk)
            print()
        
        final_result = {}
        for result in results:
            final_result.update(result)
        
        print("\n✅ 工作流执行完成！")
        print(f"   最终结果: {final_result}")
        return final_result
    except Exception as e:
        print(f"❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return None


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print("POS系统工作流测试（独立）")
    print("=" * 80)
    
    # 测试扫码功能
    print("\n\n📦 测试 1: 扫码添加商品")
    result1 = test_scan_product()
    
    # 测试结账功能
    print("\n\n💰 测试 2: 结账")
    result2 = test_checkout()
    
    print("\n\n" + "=" * 80)
    print("所有测试完成！")
    print("=" * 80)
