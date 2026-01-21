"""查看订单数据"""
import sys
import os

os.chdir(os.getenv("COZE_WORKSPACE_PATH"))

from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import Order, OrderItem, Inventory


def check_orders():
    """查看订单数据"""
    db = get_session()
    
    try:
        orders = db.query(Order).all()
        
        print(f"\n📋 订单列表 (共 {len(orders)} 个):")
        print("=" * 80)
        
        for order in orders:
            print(f"\n订单号: {order.order_no}")
            print(f"客户ID: {order.customer_id}")
            print(f"总金额: ¥{order.total_amount}")
            print(f"状态: {order.status}")
            print(f"创建时间: {order.created_at}")
            
            # 查询订单明细
            items = db.query(OrderItem).filter(OrderItem.order_id == order.id).all()
            print("\n商品明细:")
            for item in items:
                product = db.query(Inventory).filter(Inventory.product_id == item.product_id).first()
                print(f"  - 商品ID: {item.product_id}")
                print(f"    数量: {item.quantity}")
                print(f"    单价: ¥{item.unit_price}")
                print(f"    小计: ¥{item.subtotal}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_orders()
