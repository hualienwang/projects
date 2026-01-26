#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Dashboard API 测试脚本
测试所有 Dashboard 相关的 API 端点
"""

import requests
import json
import sys
from typing import Dict, Any

# API 基础 URL
BASE_URL = "http://localhost:5000"

# ANSI 颜色代码
class Colors:
    CYAN = '\033[96m'
    YELLOW = '\033[93m'
    GREEN = '\033[92m'
    RED = '\033[91m'
    WHITE = '\033[97m'
    RESET = '\033[0m'

def print_header(text: str):
    """打印标题"""
    print(f"\n{Colors.CYAN}{'='*50}{Colors.RESET}")
    print(f"{Colors.CYAN}{text}{Colors.RESET}")
    print(f"{Colors.CYAN}{'='*50}{Colors.RESET}\n")

def print_success(message: str):
    """打印成功消息"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    """打印错误消息"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message: str):
    """打印信息消息"""
    print(f"{Colors.WHITE}{message}{Colors.RESET}")

def print_warning(message: str):
    """打印警告消息"""
    print(f"{Colors.YELLOW}⚠ {message}{Colors.RESET}")

def test_health() -> bool:
    """测试后端服务健康检查"""
    print_warning("正在测试后端服务连接...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print_success("后端服务连接成功")
            return True
        else:
            print_error(f"后端服务响应异常，状态码: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"错误: 无法连接到后端服务 - {e}")
        print_warning(f"请确保后端服务正在运行: {BASE_URL}")
        return False

def test_api(url: str, method: str = "GET", data: Dict[str, Any] = None) -> bool:
    """通用 API 测试函数"""
    try:
        if method == "GET":
            response = requests.get(url)
        elif method == "POST":
            response = requests.post(url, json=data)
        else:
            print_error(f"不支持的 HTTP 方法: {method}")
            return False

        print_info(f"状态码: {response.status_code}")

        # 尝试解析 JSON 响应
        try:
            json_data = response.json()
            print_info("响应内容:")
            print(json.dumps(json_data, ensure_ascii=False, indent=2))
        except:
            print_info("响应内容:")
            print(response.text)

        if response.status_code == 200:
            print_success("测试通过")
            return True
        else:
            print_error(f"测试失败，状态码: {response.status_code}")
            return False

    except Exception as e:
        print_error(f"测试失败: {e}")
        return False

def main():
    """主测试函数"""
    print_header("Dashboard API 测试工具")

    # 测试后端服务连接
    if not test_health():
        sys.exit(1)

    # 测试 1: 获取可用图表列表
    print_header("测试 1: 获取可用图表列表")
    test_api(f"{BASE_URL}/api/dashboard/charts")

    # 测试 2: 获取图表类型
    print_header("测试 2: 获取图表类型")
    test_api(f"{BASE_URL}/api/dashboard/chart-types")

    # 测试 3: 获取角色列表
    print_header("测试 3: 获取角色列表")
    test_api(f"{BASE_URL}/api/dashboard/roles")

    # 测试 4: 查询用户权限 (admin)
    print_header("测试 4: 查询用户权限 (admin)")
    test_api(f"{BASE_URL}/api/dashboard/permissions/admin")

    # 测试 5: 生成销售趋势图
    print_header("测试 5: 生成销售趋势图")
    test_api(
        f"{BASE_URL}/api/dashboard/generate",
        method="POST",
        data={"chart_type": "sales_trend", "user_role": "admin", "user_id": "test_user_001"}
    )

    # 测试 6: 生成商品销售排行
    print_header("测试 6: 生成商品销售排行")
    test_api(
        f"{BASE_URL}/api/dashboard/generate",
        method="POST",
        data={"chart_type": "product_ranking", "user_role": "admin", "user_id": "test_user_001"}
    )

    # 测试 7: 生成库存状态分布
    print_header("测试 7: 生成库存状态分布")
    test_api(
        f"{BASE_URL}/api/dashboard/generate",
        method="POST",
        data={"chart_type": "inventory_distribution", "user_role": "admin", "user_id": "test_user_001"}
    )

    # 测试 8: 生成客户消费分析
    print_header("测试 8: 生成客户消费分析")
    test_api(
        f"{BASE_URL}/api/dashboard/generate",
        method="POST",
        data={"chart_type": "customer_analysis", "user_role": "admin", "user_id": "test_user_001"}
    )

    # 测试 9: 生成供应商统计
    print_header("测试 9: 生成供应商统计")
    test_api(
        f"{BASE_URL}/api/dashboard/generate",
        method="POST",
        data={"chart_type": "supplier_stats", "user_role": "admin", "user_id": "test_user_001"}
    )

    print_header("所有测试完成")
    print_success("测试脚本执行完毕")

if __name__ == "__main__":
    main()
