"""查看库存数据"""
import sys
import os

os.chdir(os.getenv("COZE_WORKSPACE_PATH"))

from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import Product, Inventory


def check_inventory():
    """查看库存数据"""
    db = get_session()
    
    try:
        inventories = db.query(Inventory).join(Product).all()
        
        print(f"\n📦 库存列表:")
        print("=" * 80)
        
        for inv in inventories:
            print(f"\n商品: {inv.product.name}")
            print(f"ISBN: {inv.product.isbn}")
            print(f"当前库存: {inv.quantity}")
            print(f"最小阈值: {inv.min_stock_threshold}")
            print(f"最大阈值: {inv.max_stock_threshold}")
        
        print("\n" + "=" * 80)
        
    except Exception as e:
        print(f"❌ 查询失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    check_inventory()
