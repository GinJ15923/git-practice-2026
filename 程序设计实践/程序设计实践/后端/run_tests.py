#!/usr/bin/env python3
"""
测试运行器 - 运行所有测试

功能增强：
- 自动发现所有测试用例
- 支持命令行参数过滤测试
- 更详细的测试结果展示
- 环境变量支持
- 可选的测试覆盖率统计
"""

import unittest
import sys
import os
import time
import argparse
import logging
from typing import List, Optional, Tuple

# 配置基本日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('test_runner')

# 尝试导入测试覆盖率工具
try:
    import coverage
    COVERAGE_AVAILABLE = True
except ImportError:
    logger.info("coverage模块未安装，无法生成测试覆盖率报告")
    COVERAGE_AVAILABLE = False


def setup_test_environment() -> None:
    """设置测试环境，添加必要的路径到Python搜索路径"""
    # 添加项目根目录到Python路径
    project_root = os.path.dirname(os.path.abspath(__file__))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
        logger.info(f"已添加项目根目录到Python路径: {project_root}")
    
    # 确保测试目录在路径中
    tests_dir = os.path.join(project_root, 'tests')
    if tests_dir not in sys.path:
        sys.path.insert(0, tests_dir)
        logger.info(f"已添加测试目录到Python路径: {tests_dir}")


def run_tests(test_pattern: Optional[str] = None, fail_fast: bool = False, 
              with_coverage: bool = False) -> Tuple[unittest.TestResult, float]:
    """运行测试套件并返回测试结果和运行时间
    
    参数:
        test_pattern: 测试名称过滤模式
        fail_fast: 是否在第一个失败时停止测试
        with_coverage: 是否生成测试覆盖率报告
    
    返回:
        测试结果对象和运行时间
    """
    # 设置测试环境
    setup_test_environment()
    
    # 初始化测试覆盖率工具（如果可用）
    cov = None
    if with_coverage and COVERAGE_AVAILABLE:
        cov = coverage.Coverage(
            source=['app', 'api'],  # 要覆盖的源代码目录
            omit=['*__pycache__*', '*tests*', '*venv*', '*env*']  # 排除的目录
        )
        cov.start()
        logger.info("已开始测试覆盖率统计")
    
    print("=" * 60)
    print("开始运行测试套件")
    print(f"过滤模式: {'无' if not test_pattern else test_pattern}")
    print(f"快速失败: {fail_fast}")
    print(f"覆盖率统计: {with_coverage and COVERAGE_AVAILABLE}")
    print("=" * 60)
    
    start_time = time.time()
    
    # 创建测试加载器
    loader = unittest.TestLoader()
    
    # 如果有测试过滤模式，则使用自定义的测试查找函数
    if test_pattern:
        def pattern_match(test_name: str) -> bool:
            return test_pattern.lower() in test_name.lower()
        
        loader.testNamePatterns = [test_pattern]
        suite = unittest.TestSuite()
        
        # 从tests目录发现所有测试
        tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
        all_tests = loader.discover(tests_dir, pattern='test_*.py')
        
        # 应用过滤
        for test_case in all_tests:
            filtered_tests = []
            for test in test_case:
                if hasattr(test, '_tests'):
                    # 处理TestSuite
                    for sub_test in test:
                        if pattern_match(sub_test.id()):
                            filtered_tests.append(sub_test)
                elif pattern_match(test.id()):
                    # 处理单个TestCase
                    filtered_tests.append(test)
            
            if filtered_tests:
                sub_suite = unittest.TestSuite(filtered_tests)
                suite.addTest(sub_suite)
    else:
        # 从tests目录自动发现所有测试
        tests_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'tests')
        suite = loader.discover(tests_dir, pattern='test_*.py')
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2, failfast=fail_fast)
    result = runner.run(suite)
    
    # 停止覆盖率统计并生成报告（如果启用）
    if cov:
        cov.stop()
        cov.save()
        # 生成控制台覆盖率报告
        print("\n" + "=" * 60)
        print("测试覆盖率报告")
        print("=" * 60)
        cov.report(show_missing=True)
        
        # 可选：生成HTML覆盖率报告
        if os.environ.get('GENERATE_HTML_REPORT', 'false').lower() == 'true':
            cov.html_report(directory='coverage_html_report')
            logger.info("HTML覆盖率报告已生成在 coverage_html_report 目录")
    
    end_time = time.time()
    return result, end_time - start_time


def print_test_summary(result: unittest.TestResult, run_time: float) -> None:
    """打印测试结果摘要"""
    print("\n" + "=" * 60)
    print("测试总结")
    print("=" * 60)
    print(f"运行时间: {run_time:.2f}秒")
    print(f"测试用例数: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失败: {len(result.failures)}")
    print(f"错误: {len(result.errors)}")
    print(f"跳过: {len(result.skipped) if hasattr(result, 'skipped') else 0}")
    
    if result.failures:
        print("\n失败详情:")
        for i, (test, traceback) in enumerate(result.failures, 1):
            test_name = test.id().split('.')[-1]
            print(f"  {i}. ❌ {test_name}")
            # 提取简短的错误信息
            error_lines = traceback.splitlines()
            short_error = error_lines[-1] if error_lines else "Unknown error"
            print(f"      {short_error}")
    
    if result.errors:
        print("\n错误详情:")
        for i, (test, traceback) in enumerate(result.errors, 1):
            test_name = test.id().split('.')[-1]
            print(f"  {i}. ⚠️ {test_name}")
            # 提取简短的错误信息
            error_lines = traceback.splitlines()
            short_error = error_lines[-1] if error_lines else "Unknown error"
            print(f"      {short_error}")
    
    # 输出成功消息
    if result.wasSuccessful():
        print("\n✅ 所有测试通过！")
    else:
        print("\n❌ 测试失败！")


def main() -> None:
    """主函数，处理命令行参数并运行测试"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='运行项目测试')
    parser.add_argument('--pattern', '-p', help='测试名称过滤模式')
    parser.add_argument('--fail-fast', '-f', action='store_true', 
                        help='在第一个失败时停止测试')
    parser.add_argument('--coverage', '-c', action='store_true', 
                        help='生成测试覆盖率报告')
    parser.add_argument('--verbose', '-v', action='store_true', 
                        help='启用详细日志')
    
    args = parser.parse_args()
    
    # 如果启用详细日志，设置日志级别为DEBUG
    if args.verbose:
        logger.setLevel(logging.DEBUG)
    
    # 运行测试
    result, run_time = run_tests(
        test_pattern=args.pattern,
        fail_fast=args.fail_fast,
        with_coverage=args.coverage
    )
    
    # 打印测试摘要
    print_test_summary(result, run_time)
    
    # 退出码：0表示成功，1表示失败
    sys.exit(0 if result.wasSuccessful() else 1)

if __name__ == "__main__":
    main()