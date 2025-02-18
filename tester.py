import time
from dataclasses import dataclass
from typing import Optional, Dict, Any

@dataclass
class TestResult:
    """Test result data class"""
    provider: str
    first_token_time: Optional[float]
    reasoning_tokens: int
    reasoning_time: float
    content_tokens: int
    content_time: float
    total_tokens: int
    total_time: float

class APITester:
    """API testing class for different providers"""
    
    def __init__(self, buffer_output=True):
        self.reset_metrics()
        self.buffer_output = buffer_output
        self._output_buffer = []
    
    def reset_metrics(self):
        """Reset all metrics for a new test"""
        self.prompt_tokens = 0
        self.completion_tokens = 0
        self.reasoning_tokens = 0
        self.content_tokens = 0
        self.total_tokens = 0
        
        self.reasoning_text = ""
        self.content_text = ""
        
        self.start_time = None
        self.first_token_time = None
        
        self.reasoning_start_time = None
        self.reasoning_end_time = None
        self.content_start_time = None
        self.content_end_time = None
        
        self.usage_content = ""
        self._output_buffer = []
    
    def _buffer_print(self, text, end='\n'):
        """Buffer or directly print text based on settings"""
        if self.buffer_output:
            self._output_buffer.append(text + (end if end else ""))
        else:
            print(text, end=end)
    
    def _flush_buffer(self):
        """Flush the output buffer to console"""
        if self.buffer_output and self._output_buffer:
            print(''.join(self._output_buffer), end='')
            self._output_buffer = []
    
    def test_provider(self, provider, messages) -> Optional[TestResult]:
        """
        Test a specific provider with given messages
        
        Args:
            provider: Provider instance
            messages: List of message dictionaries
        
        Returns:
            TestResult object if successful, None if failed
        """
        self._buffer_print(f"\n---------------------------")
        self._buffer_print(f"开始测试服务商：{provider.name}")
        self._buffer_print(f"---------------------------\n")
        
        try:
            self.reset_metrics()
            self.start_time = time.time()
            
            # Create streaming completion
            response = provider.create_completion(messages)
            
            # Process each chunk
            for chunk in response:
                self._process_usage(chunk)
                self._process_content(chunk)
            
            # Calculate final metrics
            total_time = time.time() - self.start_time
            reasoning_time = (self.reasoning_end_time - self.reasoning_start_time) if (self.reasoning_start_time and self.reasoning_end_time) else 0
            content_time = (self.content_end_time - self.content_start_time) if (self.content_start_time and self.content_end_time) else 0
            
            # Print results
            self._print_results(provider.name, total_time, reasoning_time, content_time)
            
            # Flush the buffer
            self._flush_buffer()
            
            # Return test results
            return TestResult(
                provider=provider.name,
                first_token_time=self.first_token_time,
                reasoning_tokens=self.reasoning_tokens,
                reasoning_time=reasoning_time,
                content_tokens=self.content_tokens,
                content_time=content_time,
                total_tokens=self.total_tokens,
                total_time=total_time
            )
            
        except Exception as e:
            self._buffer_print(f"服务商 {provider.name} 测试过程中发生错误：{e}")
            self._buffer_print("\n---------------------------\n")
            self._flush_buffer()
            return None
    
    def _process_usage(self, chunk):
        """Process usage information from chunk"""
        if chunk.usage:
            self.usage_content = chunk.usage
            
            # Update token counts
            if chunk.usage.completion_tokens_details is None:
                self.reasoning_tokens = 0
            else:
                self.reasoning_tokens = chunk.usage.completion_tokens_details.reasoning_tokens
            
            self.prompt_tokens = chunk.usage.prompt_tokens
            self.completion_tokens = chunk.usage.completion_tokens
            self.content_tokens = self.completion_tokens - self.reasoning_tokens
            self.total_tokens = chunk.usage.total_tokens
    
    def _process_content(self, chunk):
        """Process content from chunk"""
        if not chunk.choices:
            return
            
        delta = chunk.choices[0].delta
        reasoning_piece = getattr(delta, 'reasoning_content', "")
        content_piece = getattr(delta, 'content', "")
        
        # Record first token time
        if self.first_token_time is None and (reasoning_piece or content_piece):
            self.first_token_time = time.time() - self.start_time
        
        # Process reasoning content
        if reasoning_piece:
            if self.reasoning_start_time is None:
                self.reasoning_start_time = time.time()
            self.reasoning_text += reasoning_piece
            self.reasoning_end_time = time.time()
            self._buffer_print(reasoning_piece, end='')
        
        # Process main content
        elif content_piece:
            if self.content_start_time is None:
                self.content_start_time = time.time()
            self.content_text += content_piece
            self.content_end_time = time.time()
            self._buffer_print(content_piece, end='')
    
    def _print_results(self, provider_name: str, total_time: float, reasoning_time: float, content_time: float):
        """Print test results"""
        if self.usage_content:
            self._buffer_print("\n\n【Usage 信息】")
            self._buffer_print(str(self.usage_content))
        
        self._buffer_print(f"\n\n【{provider_name}】")
        
        if self.first_token_time is not None:
            self._buffer_print(f"首 token 响应时间：{self.first_token_time:.2f} 秒")
        else:
            self._buffer_print("未收到 token 响应。")
        
        if self.reasoning_tokens > 0:
            self._buffer_print(
                f"Reasoning 部分：{len(self.reasoning_text)} 字符，{self.reasoning_tokens} tokens, "
                f"用时：{reasoning_time:.2f} 秒, "
                f"生成速度：{self.reasoning_tokens / reasoning_time if reasoning_time > 0 else 0:.2f} tokens/s"
            )
            self._buffer_print(
                f"Content 部分：{len(self.content_text)} 字符，{self.content_tokens} tokens, "
                f"用时：{content_time:.2f} 秒, "
                f"生成速度：{self.content_tokens / content_time if content_time > 0 else 0:.2f} tokens/s"
            )
        
        self._buffer_print(
            f"内容生成：{len(self.reasoning_text + self.content_text)} 字符，{self.completion_tokens} tokens, "
            f"总用时：{total_time:.2f} 秒, "
            f"生成速度：{self.completion_tokens / total_time if total_time > 0 else 0:.2f} tokens/s"
        )
        self._buffer_print("\n***************************\n")
