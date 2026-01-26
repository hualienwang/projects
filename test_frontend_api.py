#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
测试前端 API 调用格式
模拟前端调用 API 的过程
"""

import requests
import json

BASE_URL = "http://localhost:5000"

# 模拟前端调用
def test_sales_trend():
    """测试销售趋势 API - 模拟前端调用"""
    print("=" * 60)
    print("测试: 销售趋势 API (模拟前端调用)")
    print("=" * 60)

    payload = {
        "user_id": "user123",
        "user_role": "admin",
        "chart_type": "sales_trend"
    }

    print(f"\n请求参数:")
    print(json.dumps(payload, indent=2, ensure_ascii=False))

    try:
        response = requests.post(
            f"{BASE_URL}/api/dashboard/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"\n响应状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n响应数据:")
            print(json.dumps(data, indent=2, ensure_ascii=False))

            # 检查关键字段
            print("\n" + "=" * 60)
            print("数据验证:")
            print("=" * 60)

            required_fields = ["success", "has_permission", "chart_config", "chart_data"]
            for field in required_fields:
                if field in data:
                    print(f"✓ {field}: 存在")
                else:
                    print(f"✗ {field}: 缺失")

            if "chart_config" in data:
                chart_config = data["chart_config"]
                required_config_fields = ["type", "data", "options"]
                print("\nchart_config 字段检查:")
                for field in required_config_fields:
                    if field in chart_config:
                        print(f"  ✓ {field}: 存在")
                    else:
                        print(f"  ✗ {field}: 缺失")

                if "data" in chart_config:
                    chart_data = chart_config["data"]
                    required_data_fields = ["labels", "datasets"]
                    print("\nchart_config.data 字段检查:")
                    for field in required_data_fields:
                        if field in chart_data:
                            print(f"  ✓ {field}: 存在")
                            if field == "datasets" and isinstance(chart_data[field], list):
                                print(f"    - datasets 数量: {len(chart_data[field])}")
                                if len(chart_data[field]) > 0:
                                    print(f"    - 第一个 dataset 的数据点数: {len(chart_data[field][0].get('data', []))}")
                        else:
                            print(f"  ✗ {field}: 缺失")
        else:
            print(f"\n错误: {response.text}")

    except Exception as e:
        print(f"\n请求失败: {e}")

def test_product_ranking():
    """测试商品销售排行 API"""
    print("\n\n" + "=" * 60)
    print("测试: 商品销售排行 API")
    print("=" * 60)

    payload = {
        "user_id": "user123",
        "user_role": "admin",
        "chart_type": "product_ranking"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/dashboard/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n响应数据 (仅显示 chart_config 的 type 和 data.labels):")
            print(f"  chart_type: {data.get('chart_config', {}).get('type')}")
            print(f"  labels: {data.get('chart_config', {}).get('data', {}).get('labels', [])}")
            print(f"  datasets 数量: {len(data.get('chart_config', {}).get('data', {}).get('datasets', []))}")
        else:
            print(f"错误: {response.text}")

    except Exception as e:
        print(f"请求失败: {e}")

def test_inventory_distribution():
    """测试库存状态分布 API"""
    print("\n\n" + "=" * 60)
    print("测试: 库存状态分布 API")
    print("=" * 60)

    payload = {
        "user_id": "user123",
        "user_role": "admin",
        "chart_type": "inventory_distribution"
    }

    try:
        response = requests.post(
            f"{BASE_URL}/api/dashboard/generate",
            json=payload,
            headers={"Content-Type": "application/json"}
        )

        print(f"响应状态码: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"\n响应数据:")
            print(f"  chart_type: {data.get('chart_config', {}).get('type')}")
            print(f"  has_permission: {data.get('has_permission')}")
            print(f"  success: {data.get('success')}")
        else:
            print(f"错误: {response.text}")

    except Exception as e:
        print(f"请求失败: {e}")

if __name__ == "__main__":
    test_sales_trend()
    test_product_ranking()
    test_inventory_distribution()

    print("\n\n" + "=" * 60)
    print("测试完成！")
    print("=" * 60)
