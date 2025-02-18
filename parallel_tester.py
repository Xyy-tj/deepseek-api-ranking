import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Optional
from dataclasses import dataclass
from tester import APITester
from providers import BaseProvider

@dataclass
class ParallelTestConfig:
    """并行测试配置"""
    max_workers: int = 3  # 最大并发数
    timeout: int = 300    # 单个测试超时时间（秒）

class ParallelAPITester:
    """并行API测试器"""
    
    def __init__(self, config: ParallelTestConfig = None):
        self.config = config or ParallelTestConfig()
        self._lock = threading.Lock()  # 用于线程安全的打印
    
    def test_providers(self, providers: List[BaseProvider], messages: List[dict]):
        """
        并行测试多个提供商
        
        Args:
            providers: 提供商实例列表
            messages: 测试消息列表
        
        Returns:
            list: 测试结果列表
        """
        results = []
        active_providers = [p for p in providers if p.is_available()]
        
        if not active_providers:
            print("没有可用的服务商")
            return results
        
        with ThreadPoolExecutor(max_workers=min(self.config.max_workers, len(active_providers))) as executor:
            # 提交所有测试任务
            future_to_provider = {
                executor.submit(self._test_single_provider, provider, messages): provider
                for provider in active_providers
            }
            
            # 收集结果
            for future in as_completed(future_to_provider):
                provider = future_to_provider[future]
                try:
                    result = future.result(timeout=self.config.timeout)
                    if result:
                        results.append(result)
                except Exception as e:
                    with self._lock:
                        print(f"\n服务商 {provider.name} 测试失败: {str(e)}")
        
        return sorted(results, key=lambda x: x.provider)  # 按提供商名称排序
    
    def _test_single_provider(self, provider: BaseProvider, messages: List[dict]):
        """
        测试单个提供商（在独立线程中运行）
        """
        with self._lock:
            print(f"\n准备测试服务商：{provider.name}")
        
        # 使用带缓冲的测试器
        tester = APITester(buffer_output=True)
        result = tester.test_provider(provider, messages)
        
        with self._lock:
            if result:
                print(f"\n完成测试服务商：{provider.name}")
            else:
                print(f"\n服务商 {provider.name} 测试失败")
        
        return result
