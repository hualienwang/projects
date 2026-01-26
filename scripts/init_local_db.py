#!/usr/bin/env python3
"""
本地數據庫初始化腳本
創建數據庫表並插入測試數據
"""

import os
import sys
from datetime import datetime

# 添加 src 目錄到 Python 路徑
workspace_path = os.getenv("COZE_WORKSPACE_PATH", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
src_dir = os.path.join(workspace_path, 'src')
if src_dir not in sys.path:
    sys.path.insert(0, src_dir)

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# 導入數據庫模型
from storage.database.shared.model import (
    Base, Product, Inventory, Customer, Order, OrderItem
)

def init_database():
    """初始化本地數據庫"""

    # 獲取數據庫 URL
    from storage.database.db import get_db_url
    db_url = get_db_url()

    print(f"📦 使用數據庫: {db_url}")

    # 創建引擎
    engine = create_engine(db_url, echo=True)

    # 創建所有表
    print("\n🔨 創建數據庫表...")
    try:
        # 嘗試創建所有表
        Base.metadata.create_all(bind=engine, checkfirst=True)
        print("✅ 數據庫表創建成功！")
    except Exception as e:
        error_msg = str(e)
        if "already exists" in error_msg:
            print("⚠️  部分表已存在，嘗試逐個創建缺失的表...")
            # 逐個創建表，避免事務回滾問題
            for table in Base.metadata.sorted_tables:
                try:
                    table.create(engine, checkfirst=True)
                    print(f"  ✅ 創建表: {table.name}")
                except Exception as table_error:
                    if "already exists" not in str(table_error):
                        print(f"  ❌ 創建表 {table.name} 失敗: {table_error}")
        else:
            raise

    # 創建會話
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        # 檢查是否已有數據
        existing_customers = session.query(Customer).count()
        if existing_customers > 0:
            print(f"\n⚠️  數據庫已包含 {existing_customers} 條客戶記錄，跳過初始化數據")
            return

        print("\n📝 插入測試數據...")

        # 1. 創建客戶數據
        customers = [
            Customer(
                id=1,
                name="張三",
                email="zhangsan@example.com",
                phone="0912345678",
                points=0
            ),
            Customer(
                id=2,
                name="李四",
                email="lisi@example.com",
                phone="0923456789",
                points=150
            ),
            Customer(
                id=3,
                name="王五",
                email="wangwu@example.com",
                phone="0934567890",
                points=500
            )
        ]
        session.add_all(customers)
        session.flush()
        print(f"✅ 創建了 {len(customers)} 個客戶")

        # 2. 創建商品數據
        products = [
            Product(
                id=1,
                isbn="9789571234567",
                name="Python 程式設計入門",
                author="張大偉",
                publisher="松崗圖書",
                price=350.0,
                category="程式設計"
            ),
            Product(
                id=2,
                isbn="9789572345678",
                name="JavaScript 高級程式設計",
                author="李小明",
                publisher="博碩文化",
                price=460.0,
                category="程式設計"
            ),
            Product(
                id=3,
                isbn="9789573456789",
                name="資料結構與演算法",
                author="王大同",
                publisher="歐萊禮",
                price=520.0,
                category="電腦科學"
            ),
            Product(
                id=4,
                isbn="9789574567890",
                name="人工智慧基礎",
                author="陳小華",
                publisher="深藍圖書",
                price=480.0,
                category="人工智慧"
            ),
            Product(
                id=5,
                isbn="9789575678901",
                name="機器學習實戰",
                author="林大強",
                publisher="智冠科技",
                price=550.0,
                category="人工智慧"
            )
        ]
        session.add_all(products)
        session.flush()
        print(f"✅ 創建了 {len(products)} 個商品")

        # 3. 創建庫存數據
        inventories = [
            Inventory(product_id=1, quantity=50, min_stock_threshold=10),
            Inventory(product_id=2, quantity=30, min_stock_threshold=5),
            Inventory(product_id=3, quantity=20, min_stock_threshold=5),
            Inventory(product_id=4, quantity=40, min_stock_threshold=8),
            Inventory(product_id=5, quantity=25, min_stock_threshold=8)
        ]
        session.add_all(inventories)
        session.flush()
        print(f"✅ 創建了 {len(inventories)} 條庫存記錄")

        # 提交更改
        session.commit()
        print("\n🎉 數據庫初始化完成！")

        # 顯示統計信息
        print("\n📊 數據庫統計：")
        print(f"  - 客戶數量: {session.query(Customer).count()}")
        print(f"  - 商品數量: {session.query(Product).count()}")
        print(f"  - 庫存記錄: {session.query(Inventory).count()}")

    except Exception as e:
        print(f"\n❌ 初始化失敗: {e}")
        session.rollback()
        raise
    finally:
        session.close()

if __name__ == "__main__":
    print("=" * 60)
    print("🚀 本地數據庫初始化腳本")
    print("=" * 60)

    try:
        init_database()
        print("\n✅ 所有操作完成！")
    except Exception as e:
        print(f"\n❌ 發生錯誤: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
