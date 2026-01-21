"""准备客户测试数据的脚本"""
import sys
import os

os.chdir(os.getenv("COZE_WORKSPACE_PATH"))

from coze_coding_dev_sdk.database import get_session
from storage.database.shared.model import Customer


def prepare_customer_data():
    """准备客户测试数据"""
    db = get_session()

    try:
        test_customers = [
            {
                "name": "張三",
                "phone": "0912-345-678",
                "email": "zhangsan@example.com",
                "level": "金卡會員",
                "points": 1500,
                "total_purchase": 12500.00
            },
            {
                "name": "李四",
                "phone": "0923-456-789",
                "email": "lisi@example.com",
                "level": "銀卡會員",
                "points": 800,
                "total_purchase": 8500.00
            },
            {
                "name": "王五",
                "phone": "0934-567-890",
                "email": "wangwu@example.com",
                "level": "普通會員",
                "points": 200,
                "total_purchase": 2800.00
            }
        ]

        for customer_data in test_customers:
            customer = Customer(**customer_data)
            db.add(customer)
            db.commit()
            db.refresh(customer)
            print(f"✓ 创建客户: {customer.name} ({customer.level})")

        print("\n✓ 客户测试数据准备完成！")
        print(f"  - 客户数量: {len(test_customers)} 个")

    except Exception as e:
        print(f"✗ 准备客户数据失败: {e}")
        import traceback
        traceback.print_exc()
    finally:
        db.close()


if __name__ == "__main__":
    prepare_customer_data()
