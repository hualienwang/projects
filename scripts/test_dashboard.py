"""
数据可视化系统测试脚本
测试工作流和API接口
"""
import asyncio
import sys
import os
from datetime import date, timedelta

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from coze_coding_utils.runtime_ctx.context import new_context, Context
from graphs.graph_dashboard import main_graph


def print_section(title: str):
    """打印分节标题"""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80)


def print_result(test_name: str, success: bool, message: str = ""):
    """打印测试结果"""
    status = "✓ PASS" if success else "✗ FAIL"
    print(f"\n{status}: {test_name}")
    if message:
        print(f"  {message}")


async def test_permission_check():
    """测试权限检查功能"""
    print_section("测试1: 权限检查")
    
    test_cases = [
        {
            "name": "管理员访问所有图表",
            "user_role": "admin",
            "chart_type": "supplier_stats",
            "expected_permission": True
        },
        {
            "name": "经理访问库存分布",
            "user_role": "manager",
            "chart_type": "inventory_distribution",
            "expected_permission": True
        },
        {
            "name": "员工访问销售趋势",
            "user_role": "staff",
            "chart_type": "sales_trend",
            "expected_permission": True
        },
        {
            "name": "查看者访问客户分析（应失败）",
            "user_role": "viewer",
            "chart_type": "customer_analysis",
            "expected_permission": False
        }
    ]
    
    for test_case in test_cases:
        ctx = new_context("test_permission")
        
        try:
            input_data = {
                "user_id": "test_user",
                "user_role": test_case["user_role"],
                "chart_type": test_case["chart_type"],
                "start_date": date.today() - timedelta(days=30),
                "end_date": date.today()
            }
            
            result = await main_graph.ainvoke(input_data, context=ctx)
            
            has_permission = result.get("has_permission", False)
            expected = test_case["expected_permission"]
            
            if has_permission == expected:
                print_result(test_case["name"], True, result.get("permission_message", ""))
            else:
                print_result(test_case["name"], False, 
                           f"预期权限: {expected}, 实际权限: {has_permission}")
                
        except Exception as e:
            print_result(test_case["name"], False, str(e))


async def test_sales_trend():
    """测试销售趋势图"""
    print_section("测试2: 销售趋势图")
    
    ctx = new_context("test_sales_trend")
    
    try:
        input_data = {
            "user_id": "test_user",
            "user_role": "manager",
            "chart_type": "sales_trend",
            "start_date": date.today() - timedelta(days=7),
            "end_date": date.today()
        }
        
        result = await main_graph.ainvoke(input_data, context=ctx)
        
        if result.get("has_permission") and result.get("chart_data"):
            print_result("销售趋势图生成", True)
            
            # 打印图表数据摘要
            chart_data = result["chart_data"]
            print(f"\n  图表类型: {result.get('chart_config', {}).get('type')}")
            print(f"  数据点数量: {len(chart_data.get('labels', []))}")
            print(f"  数据集数量: {len(chart_data.get('datasets', []))}")
            
            if chart_data.get('labels'):
                print(f"  日期范围: {chart_data['labels'][0]} ~ {chart_data['labels'][-1]}")
                
        else:
            print_result("销售趋势图生成", False, result.get("permission_message", "生成失败"))
            
    except Exception as e:
        print_result("销售趋势图生成", False, str(e))


async def test_product_ranking():
    """测试商品销售排行"""
    print_section("测试3: 商品销售排行")
    
    ctx = new_context("test_product_ranking")
    
    try:
        input_data = {
            "user_id": "test_user",
            "user_role": "staff",
            "chart_type": "product_ranking",
            "start_date": date.today() - timedelta(days=30),
            "end_date": date.today()
        }
        
        result = await main_graph.ainvoke(input_data, context=ctx)
        
        if result.get("has_permission") and result.get("chart_data"):
            print_result("商品销售排行生成", True)
            
            chart_data = result["chart_data"]
            print(f"\n  图表类型: {result.get('chart_config', {}).get('type')}")
            print(f"  商品数量: {len(chart_data.get('labels', []))}")
            
            if chart_data.get('labels'):
                print(f"  Top 3 商品:")
                for i, name in enumerate(chart_data['labels'][:3], 1):
                    dataset = chart_data['datasets'][0]
                    value = dataset['data'][i-1]
                    print(f"    {i}. {name}: {value} 件")
                    
        else:
            print_result("商品销售排行生成", False, result.get("permission_message", "生成失败"))
            
    except Exception as e:
        print_result("商品销售排行生成", False, str(e))


async def test_inventory_distribution():
    """测试库存状态分布"""
    print_section("测试4: 库存状态分布")
    
    ctx = new_context("test_inventory_distribution")
    
    try:
        input_data = {
            "user_id": "test_user",
            "user_role": "manager",
            "chart_type": "inventory_distribution"
        }
        
        result = await main_graph.ainvoke(input_data, context=ctx)
        
        if result.get("has_permission") and result.get("chart_data"):
            print_result("库存状态分布生成", True)
            
            chart_data = result["chart_data"]
            print(f"\n  图表类型: {result.get('chart_config', {}).get('type')}")
            print(f"  状态类别: {chart_data.get('labels', [])}")
            
            if chart_data.get('datasets'):
                dataset = chart_data['datasets'][0]
                print(f"  数据分布:")
                for label, value in zip(chart_data['labels'], dataset['data']):
                    print(f"    {label}: {value} 个商品")
                    
        else:
            print_result("库存状态分布生成", False, result.get("permission_message", "生成失败"))
            
    except Exception as e:
        print_result("库存状态分布生成", False, str(e))


async def test_customer_analysis():
    """测试客户消费分析"""
    print_section("测试5: 客户消费分析")
    
    ctx = new_context("test_customer_analysis")
    
    try:
        input_data = {
            "user_id": "test_user",
            "user_role": "manager",
            "chart_type": "customer_analysis",
            "start_date": date.today() - timedelta(days=30),
            "end_date": date.today()
        }
        
        result = await main_graph.ainvoke(input_data, context=ctx)
        
        if result.get("has_permission") and result.get("chart_data"):
            print_result("客户消费分析生成", True)
            
            chart_data = result["chart_data"]
            print(f"\n  图表类型: {result.get('chart_config', {}).get('type')}")
            print(f"  客户数量: {len(chart_data.get('labels', []))}")
            
            if chart_data.get('labels'):
                print(f"  Top 3 客户:")
                for i, name in enumerate(chart_data['labels'][:3], 1):
                    dataset = chart_data['datasets'][0]
                    value = dataset['data'][i-1]
                    print(f"    {i}. {name}: {value:.2f} 元")
                    
        else:
            print_result("客户消费分析生成", False, result.get("permission_message", "生成失败"))
            
    except Exception as e:
        print_result("客户消费分析生成", False, str(e))


async def test_supplier_stats():
    """测试供应商采购统计"""
    print_section("测试6: 供应商采购统计")
    
    ctx = new_context("test_supplier_stats")
    
    try:
        input_data = {
            "user_id": "test_user",
            "user_role": "admin",
            "chart_type": "supplier_stats"
        }
        
        result = await main_graph.ainvoke(input_data, context=ctx)
        
        if result.get("has_permission") and result.get("chart_data"):
            print_result("供应商采购统计生成", True)
            
            chart_data = result["chart_data"]
            print(f"\n  图表类型: {result.get('chart_config', {}).get('type')}")
            print(f"  供应商数量: {len(chart_data.get('labels', []))}")
            print(f"  数据集数量: {len(chart_data.get('datasets', []))}")
            
            if chart_data.get('labels'):
                print(f"  供应商列表:")
                for i, name in enumerate(chart_data['labels'], 1):
                    dataset = chart_data['datasets'][0]
                    value = dataset['data'][i-1]
                    print(f"    {i}. {name}: {value} 个商品")
                    
        else:
            print_result("供应商采购统计生成", False, result.get("permission_message", "生成失败"))
            
    except Exception as e:
        print_result("供应商采购统计生成", False, str(e))


async def test_chart_config_structure():
    """测试图表配置结构"""
    print_section("测试7: 图表配置结构验证")
    
    ctx = new_context("test_chart_config")
    
    try:
        input_data = {
            "user_id": "test_user",
            "user_role": "admin",
            "chart_type": "sales_trend",
            "start_date": date.today() - timedelta(days=7),
            "end_date": date.today()
        }
        
        result = await main_graph.ainvoke(input_data, context=ctx)
        
        if not result.get("has_permission"):
            print_result("图表配置结构验证", False, "权限不足")
            return
        
        chart_config = result.get("chart_config", {})
        
        # 验证必需字段
        required_fields = ["type", "data", "options"]
        missing_fields = [f for f in required_fields if f not in chart_config]
        
        if missing_fields:
            print_result("图表配置结构验证", False, f"缺少必需字段: {missing_fields}")
            return
        
        # 验证data字段
        if "labels" not in chart_config["data"] or "datasets" not in chart_config["data"]:
            print_result("图表配置结构验证", False, "chart_config.data 缺少 labels 或 datasets")
            return
        
        # 验证options字段
        if "responsive" not in chart_config["options"]:
            print_result("图表配置结构验证", False, "chart_config.options 缺少 responsive")
            return
        
        print_result("图表配置结构验证", True, "所有必需字段存在")
        
        # 打印配置摘要
        print(f"\n  图表类型: {chart_config['type']}")
        print(f"  标签数量: {len(chart_config['data']['labels'])}")
        print(f"  数据集数量: {len(chart_config['data']['datasets'])}")
        print(f"  响应式: {chart_config['options']['responsive']}")
        
    except Exception as e:
        print_result("图表配置结构验证", False, str(e))


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "🚀" * 40)
    print("  数据可视化系统测试套件")
    print("🚀" * 40)
    
    tests = [
        test_permission_check,
        test_sales_trend,
        test_product_ranking,
        test_inventory_distribution,
        test_customer_analysis,
        test_supplier_stats,
        test_chart_config_structure
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            await test()
            passed += 1
        except Exception as e:
            print_result(f"测试 {test.__name__}", False, f"测试执行异常: {str(e)}")
            failed += 1
    
    # 测试总结
    print_section("测试总结")
    print(f"\n  总测试数: {passed + failed}")
    print(f"  通过: {passed}")
    print(f"  失败: {failed}")
    print(f"  成功率: {passed / (passed + failed) * 100:.1f}%")
    
    if failed == 0:
        print("\n  🎉 所有测试通过！")
    else:
        print(f"\n  ⚠️  有 {failed} 个测试失败，请检查日志")
    
    print("\n" + "=" * 80 + "\n")


if __name__ == "__main__":
    asyncio.run(run_all_tests())
