import datetime
import pytz
import time
import argparse
from typing import List, Optional, Tuple
from providers import AVAILABLE_PROVIDERS, BaseProvider
from parallel_tester import ParallelAPITester, ParallelTestConfig
from tester import APITester
from reporter import TestReporter

def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(description='API性能测试工具')
    
    # 测试模式
    parser.add_argument(
        '--mode', 
        choices=['multi', 'seq'], 
        default='seq',
        help='测试模式：multi(并行) 或 seq(串行)'
    )
    
    # 并行测试的参数
    parser.add_argument(
        '--workers',
        type=int,
        default=3,
        help='并行测试时的工作线程数（默认：3）'
    )
    
    parser.add_argument(
        '--timeout',
        type=int,
        default=300,
        help='单个测试的超时时间（秒）（默认：300）'
    )
    
    # 测试内容
    parser.add_argument(
        '--prompt',
        type=str,
        default="给我写一首七言绝句，赞叹祖国的大好河山",
        help='测试用的提示词'
    )
    
    return parser.parse_args()

def initialize_providers() -> List[BaseProvider]:
    """初始化所有提供商"""
    providers = []
    for provider_class in AVAILABLE_PROVIDERS:
        try:
            provider = provider_class()
            if not provider.is_available():
                print(f"\n跳过服务商 {provider.name}：API密钥未配置")
                continue
            providers.append(provider)
        except Exception as e:
            print(f"初始化服务商 {provider_class.__name__} 时发生错误：{e}")
    
    if not providers:
        raise ValueError("没有可用的服务商，测试终止")
    
    return providers

def run_sequential_test(
    providers: List[BaseProvider], 
    messages: List[dict]
) -> List:
    """运行串行测试"""
    print("\n开始串行测试...")
    results = []
    tester = APITester(buffer_output=True)
    
    for provider in sorted(providers, key=lambda x: x.name):
        try:
            result = tester.test_provider(provider, messages)
            if result:
                results.append(result)
        except Exception as e:
            print(f"测试服务商 {provider.name} 时发生错误：{e}")
    
    return results

def run_parallel_test(
    providers: List[BaseProvider], 
    messages: List[dict],
    workers: int,
    timeout: int
) -> List:
    """运行并行测试"""
    print("\n开始并行测试...")
    config = ParallelTestConfig(max_workers=workers, timeout=timeout)
    tester = ParallelAPITester(config)
    return tester.test_providers(providers, messages)

def main() -> Tuple[Optional[List], Optional[str]]:
    """主函数"""
    args = parse_args()
    
    # 准备测试消息
    messages = [
        {
            'role': 'user',
            'content': args.prompt
        }
    ]

    start_time = time.time()
    print(f"本次测试开始于中国时间：{datetime.datetime.now(pytz.timezone('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"测试模式：{'并行' if args.mode == 'parallel' else '串行'}")
    if args.mode == 'parallel':
        print(f"并行工作线程数：{args.workers}")
        print(f"单个测试超时时间：{args.timeout}秒")
    print(f"测试提示词：{args.prompt}")

    try:
        # 初始化提供商
        providers = initialize_providers()
        
        # 根据模式执行测试
        if args.mode == 'parallel':
            results = run_parallel_test(providers, messages, args.workers, args.timeout)
        else:
            results = run_sequential_test(providers, messages)
        
        # 生成测试报告
        reporter = TestReporter(results, messages[0]['content'])
        report_path = reporter.create_report()
        
        total_time = time.time() - start_time
        print(f"\n所有测试完成，总耗时：{total_time:.2f}秒")
        
        return results, report_path
        
    except Exception as e:
        print(f"测试过程中发生错误：{e}")
        return None, None

if __name__ == "__main__":
    main()