from abc import ABC, abstractmethod
from openai import OpenAI
from config import API_KEYS, BASE_URLS, MODELS, ENDPOINTS

class BaseProvider(ABC):
    """Base class for all API providers"""
    
    def __init__(self):
        self.client = None
        self.setup_client()
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Provider name"""
        pass
    
    @property
    @abstractmethod
    def api_key(self) -> str:
        """API key"""
        pass
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Base URL"""
        pass
    
    @property
    @abstractmethod
    def model(self) -> str:
        """Model name"""
        pass
    
    def is_available(self) -> bool:
        """Check if provider is available (has valid API key)"""
        return bool(self.api_key)
    
    def setup_client(self):
        """Initialize OpenAI client with provider configuration"""
        if not self.is_available():
            return
        
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    def create_completion(self, messages, stream=True):
        """Create chat completion"""
        if not self.is_available():
            raise ValueError(f"Provider {self.name} is not available (missing API key)")
            
        return self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            stream=stream,
            stream_options={"include_usage": True}
        )

class DeepSeekProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "DeepSeek 官方"
    
    @property
    def api_key(self) -> str:
        return API_KEYS['deepseek']
    
    @property
    def base_url(self) -> str:
        return BASE_URLS['deepseek']
    
    @property
    def model(self) -> str:
        return MODELS['deepseek']

class AliyunProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "阿里云/百炼"
    
    @property
    def api_key(self) -> str:
        return API_KEYS['aliyun']
    
    @property
    def base_url(self) -> str:
        return BASE_URLS['aliyun']
    
    @property
    def model(self) -> str:
        return MODELS['aliyun']

class QianfanProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "百度千帆"
    
    @property
    def api_key(self) -> str:
        return API_KEYS['qianfan']
    
    @property
    def base_url(self) -> str:
        return BASE_URLS['qianfan']
    
    @property
    def model(self) -> str:
        return MODELS['qianfan']

class SiliconFlowProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "硅基流动"
    
    @property
    def api_key(self) -> str:
        return API_KEYS['siliconflow']
    
    @property
    def base_url(self) -> str:
        return BASE_URLS['siliconflow']
    
    @property
    def model(self) -> str:
        return MODELS['siliconflow']

class SiliconFlowProProvider(SiliconFlowProvider):
    @property
    def name(self) -> str:
        return "硅基流动Pro"
    
    @property
    def model(self) -> str:
        return MODELS['siliconflow_pro']

class VolcesProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "火山引擎"
    
    @property
    def api_key(self) -> str:
        return API_KEYS['volces']
    
    @property
    def base_url(self) -> str:
        return BASE_URLS['volces']
    
    @property
    def model(self) -> str:
        return ENDPOINTS['volces']

class TencentCloudProvider(BaseProvider):
    @property
    def name(self) -> str:
        return "腾讯云"
    
    @property
    def api_key(self) -> str:
        return API_KEYS['tencentcloud']
    
    @property
    def base_url(self) -> str:
        return BASE_URLS['tencentcloud']
    
    @property
    def model(self) -> str:
        return MODELS['tencentcloud']

# List of all available providers
AVAILABLE_PROVIDERS = [
    DeepSeekProvider,
    AliyunProvider,
    QianfanProvider,
    SiliconFlowProvider,
    SiliconFlowProProvider,
    VolcesProvider,
    TencentCloudProvider,
]
