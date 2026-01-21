"""
POS系统使用示例

本文件展示了如何使用POS系统工作流进行扫码销售和结账操作。
"""

import os
import sys

# 设置Python路径
workspace_path = os.getenv("COZE_WORKSPACE_PATH", "/workspace/projects")
app_dir = os.path.join(workspace_path, 'src')
if app_dir not in sys.path:
    sys.path.insert(0, app_dir)

from graphs.graph_pos import pos_graph


def example_scan_product():
    """
    示例1：扫码添加商品
    
    场景：店员扫描商品条码，系统识别商品并添加到购物车
    """
    print("=" * 80)
    print("示例1：扫码添加商品")
    print("=" * 80)
    
    # 输入：扫描商品条码
    input_data = {
        "action": "scan",
        "scanned_code": "9789571468753"  # Python 程式設計：從入門到精通
    }
    
    print(f"\n📱 扫描条码: {input_data['scanned_code']}")
    print("\n执行工作流...\n")
    
    # 执行工作流
    results = []
    for chunk in pos_graph.stream(input_data):
        print(f"节点: {chunk}")
        results.append(chunk)
    
    # 显示结果
    print("\n" + "=" * 80)
    print("执行结果:")
    print("=" * 80)
    
    # 提取购物车信息
    cart_items = []
    for result in results:
        if "add_to_cart" in result:
            cart_items = result["add_to_cart"]["cart_items"]
    
    if cart_items:
        print(f"\n✅ 商品已添加到购物车！")
        for item in cart_items:
            print(f"   - {item['name']}")
            print(f"     单价: ¥{item['unit_price']:.2f}")
            print(f"     数量: {item['quantity']}")
            print(f"     小计: ¥{item['subtotal']:.2f}")
    else:
        print("\n❌ 未找到商品或添加失败")
    
    return cart_items


def example_checkout(cart_items):
    """
    示例2：结账
    
    场景：客户完成购物，进行结账操作
    """
    print("\n\n" + "=" * 80)
    print("示例2：结账")
    print("=" * 80)
    
    # 输入：结账信息
    input_data = {
        "action": "checkout",
        "cart_items": cart_items,
        "customer_id": 1  # 关联客户ID（可选）
    }
    
    print(f"\n💰 开始结账...")
    print(f"   商品数量: {len(input_data['cart_items'])}")
    print(f"   客户ID: {input_data['customer_id']}")
    print("\n执行工作流...\n")
    
    # 执行工作流
    results = []
    for chunk in pos_graph.stream(input_data):
        print(f"节点: {chunk}")
        results.append(chunk)
    
    # 显示结果
    print("\n" + "=" * 80)
    print("结账结果:")
    print("=" * 80)
    
    # 提取订单信息
    order_summary = None
    order_no = None
    receipt_url = None
    
    for result in results:
        if "calculate_order" in result:
            order_summary = result["calculate_order"]["order_summary"]
            customer_info = result["calculate_order"]["customer_info"]
        if "create_order" in result:
            order_no = result["create_order"]["order_no"]
        if "generate_receipt" in result:
            receipt_url = result["generate_receipt"]["receipt_url"]
    
    # 显示订单摘要
    if order_summary:
        print(f"\n📋 订单号: {order_no}")
        print(f"🛍️ 商品明细:")
        for item in order_summary["items"]:
            print(f"   - {item['name']} x {item['quantity']} = ¥{item['subtotal']:.2f}")
        
        print(f"\n💰 金额明细:")
        print(f"   总金额: ¥{order_summary['total_amount']:.2f}")
        
        if order_summary['discount'] > 0:
            print(f"   折扣: -¥{order_summary['discount']:.2f} ({order_summary['discount_reason']})")
        
        print(f"   实付金额: ¥{order_summary['final_amount']:.2f}")
        print(f"   获得积分: {order_summary['points_earned']}")
        
        # 显示客户信息
        if customer_info:
            print(f"\n👤 客户信息:")
            print(f"   姓名: {customer_info['name']}")
            print(f"   等级: {customer_info['level']}")
            print(f"   现有积分: {customer_info['points']}")
    
    # 显示小票信息
    if receipt_url:
        print(f"\n🧾 小票已生成")
        print(f"   下载链接: {receipt_url}")
    
    return order_no


def example_multiple_items():
    """
    示例3：多件商品销售
    
    场景：客户购买多件不同商品
    """
    print("\n\n" + "=" * 80)
    print("示例3：多件商品销售")
    print("=" * 80)
    
    # 输入：多件商品结账
    input_data = {
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
            },
            {
                "product_id": 2,
                "name": "資料庫系統概論",
                "author": "李大華",
                "isbn": "9789864345982",
                "quantity": 2,
                "unit_price": 650.0,
                "subtotal": 1300.0
            }
        ],
        "customer_id": 2  # 銀卡會員
    }
    
    print(f"\n📦 购买商品:")
    for item in input_data["cart_items"]:
        print(f"   - {item['name']} x {item['quantity']}")
    
    print(f"\n👤 客户: 客户ID {input_data['customer_id']} (銀卡會員)")
    print("\n执行工作流...\n")
    
    # 执行工作流
    results = []
    for chunk in pos_graph.stream(input_data):
        print(f"节点: {chunk}")
        results.append(chunk)
    
    # 显示结果
    print("\n" + "=" * 80)
    print("结账结果:")
    print("=" * 80)
    
    for result in results:
        if "calculate_order" in result:
            order_summary = result["calculate_order"]["order_summary"]
            customer_info = result["calculate_order"]["customer_info"]
            
            print(f"\n📋 订单信息:")
            print(f"   商品总数: {order_summary['item_count']}")
            print(f"   总金额: ¥{order_summary['total_amount']:.2f}")
            
            if order_summary['discount'] > 0:
                print(f"   会员折扣: -¥{order_summary['discount']:.2f}")
                print(f"   折扣原因: {order_summary['discount_reason']}")
            
            print(f"   实付金额: ¥{order_summary['final_amount']:.2f}")
            print(f"   获得积分: {order_summary['points_earned']}")
            
            if customer_info:
                print(f"\n👤 客户等级: {customer_info['level']}")
    
    return results


def main():
    """运行所有示例"""
    print("\n")
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 20 + "POS系统使用示例" + " " * 36 + "║")
    print("╚" + "=" * 78 + "╝")
    
    try:
        # 示例1：扫码添加商品
        cart_items = example_scan_product()
        
        # 示例2：结账
        if cart_items:
            example_checkout(cart_items)
        
        # 示例3：多件商品销售
        example_multiple_items()
        
        print("\n\n" + "=" * 80)
        print("✅ 所有示例执行完成！")
        print("=" * 80)
        
    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
