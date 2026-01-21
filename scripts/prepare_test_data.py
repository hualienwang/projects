"""准备测试数据的脚本"""
import sys
import os

# 设置工作目录
os.chdir(os.getenv("COZE_WORKSPACE_PATH"))

from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import Product, Inventory, Supplier
from storage.database.product_manager import ProductManager, ProductCreate
from storage.database.inventory_manager import InventoryManager, InventoryCreate


def prepare_test_data():
    """准备测试数据"""
    db = get_session()
    
    try:
        product_mgr = ProductManager()
        inventory_mgr = InventoryManager()
        
        # 1. 创建供应商
        supplier = Supplier(
            name="三民書局",
            contact_person="張經理",
            phone="02-23456789",
            email="zhang@sanmin.com.tw",
            address="台北市大安區和平東路二段339號"
        )
        db.add(supplier)
        db.commit()
        db.refresh(supplier)
        supplier_id = supplier.id
        
        print(f"✓ 创建供应商: {supplier.name} (ID: {supplier_id})")
        
        # 2. 创建商品和库存
        test_products = [
            {
                "isbn": "9789571468753",
                "name": "Python 程式設計：從入門到精通",
                "author": "王小明",
                "publisher": "碁峰資訊",
                "category": "程式設計",
                "price": 580.00,
                "cost": 420.00,
                "supplier_id": supplier_id,
                "quantity": 5,  # 低于默认阈值10，会触发预警
                "min_threshold": 10,
                "reorder_quantity": 30
            },
            {
                "isbn": "9789864345982",
                "name": "資料庫系統概論",
                "author": "李大華",
                "publisher": "東華書局",
                "category": "資料庫",
                "price": 650.00,
                "cost": 480.00,
                "supplier_id": supplier_id,
                "quantity": 3,  # 低于默认阈值10，会触发预警
                "min_threshold": 10,
                "reorder_quantity": 25
            },
            {
                "isbn": "9789573284561",
                "name": "演算法導論（第三版）",
                "author": "Thomas H. Cormen",
                "publisher": "歐萊禮",
                "category": "演算法",
                "price": 1200.00,
                "cost": 900.00,
                "supplier_id": supplier_id,
                "quantity": 2,  # 低于默认阈值10，会触发预警
                "min_threshold": 10,
                "reorder_quantity": 20
            },
            {
                "isbn": "9789861234567",
                "name": "人工智慧：現代方法",
                "author": "Stuart Russell",
                "publisher": "儒林圖書",
                "category": "人工智慧",
                "price": 980.00,
                "cost": 720.00,
                "supplier_id": supplier_id,
                "quantity": 8,  # 低于默认阈值10，会触发预警
                "min_threshold": 10,
                "reorder_quantity": 15
            },
            {
                "isbn": "9789577890123",
                "name": "深度學習",
                "author": "Ian Goodfellow",
                "publisher": "歐萊禮",
                "category": "人工智慧",
                "price": 1500.00,
                "cost": 1100.00,
                "supplier_id": supplier_id,
                "quantity": 50,  # 正常库存
                "min_threshold": 10,
                "max_threshold": 100,
                "reorder_quantity": 30
            }
        ]
        
        for product_data in test_products:
            # 提取库存数据
            quantity = product_data.pop("quantity")
            min_threshold = product_data.pop("min_threshold")
            max_threshold = product_data.pop("max_threshold", None)
            reorder_quantity = product_data.pop("reorder_quantity", 50)
            
            # 创建商品
            product_in = ProductCreate(**product_data)
            product = product_mgr.create_product(db, product_in)
            
            # 创建库存
            inventory_in = InventoryCreate(
                product_id=product.id,
                quantity=quantity,
                min_stock_threshold=min_threshold,
                max_stock_threshold=max_threshold,
                reorder_quantity=reorder_quantity
            )
            inventory_mgr.create_inventory(db, inventory_in)
            
            print(f"✓ 创建商品: {product.name} (库存: {quantity}/{min_threshold})")
        
        print("\n✓ 测试数据准备完成！")
        print(f"  - 供应商: 1 个")
        print(f"  - 商品: {len(test_products)} 个")
        print(f"  - 低库存商品: 4 个")
        print(f"  - 正常库存商品: 1 个")
        
    except Exception as e:
        print(f"✗ 准备测试数据失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    prepare_test_data()
