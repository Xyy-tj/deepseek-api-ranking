import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

def get_env_var(key: str, default: str = None, required: bool = True) -> str:
    """
    Get environment variable with error handling
    
    Args:
        key: Environment variable key
        default: Default value if key not found
        required: Whether this environment variable is required
    
    Returns:
        str: Environment variable value or default or None if not required
    
    Raises:
        ValueError: If key not found and required is True and no default provided
    """
    value = os.getenv(key)
    if value is None:
        if not required:
            return None
        if default is not None:
            print(f"Warning: {key} not found in environment variables, using default value")
            return default
        raise ValueError(f"Environment variable {key} not found. Please check your .env file.")
    return value

# API Keys Configuration
API_KEYS = {
    'deepseek': get_env_var('DEEPSEEK_API_KEY', required=True),
    'aliyun': get_env_var('ALIYUN_API_KEY', required=True),
    'qianfan': get_env_var('QIANFAN_API_KEY', required=False),
    'siliconflow': get_env_var('SILICONFLOW_API_KEY', required=True),
    'volces': get_env_var('VOLCES_API_KEY', required=False),
    'tencentcloud': get_env_var('TENCENTCLOUD_API_KEY', required=False),
}

# Endpoint Configuration
ENDPOINTS = {
    'volces': get_env_var('VOLCES_ENDPOINT', required=False),
}

# Base URLs
BASE_URLS = {
    'deepseek': 'https://api.deepseek.com',
    'aliyun': 'https://dashscope.aliyuncs.com/compatible-mode/v1',
    'qianfan': 'https://qianfan.baidubce.com/v2',
    'siliconflow': 'https://api.siliconflow.cn/v1',
    'volces': 'https://ark.cn-beijing.volces.com/api/v3',
    'tencentcloud': 'https://api.lkeap.cloud.tencent.com/v1',
}

# Model names
MODELS = {
    'deepseek': 'deepseek-reasoner',
    'aliyun': 'deepseek-r1',
    'qianfan': 'deepseek-r1',
    'siliconflow': 'deepseek-ai/DeepSeek-R1',
    'siliconflow_pro': 'Pro/deepseek-ai/DeepSeek-R1',
    'volces': None,  # Will be set from ENDPOINTS['volces']
    'tencentcloud': 'deepseek-r1',
}
