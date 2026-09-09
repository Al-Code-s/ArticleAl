"""
AI Provider Registry - 定义支持的AI供应商和模型
参考 NewArcReel 的设计模式
"""
from dataclasses import dataclass, field
from typing import Optional, List, Dict


@dataclass(frozen=True)
class ModelInfo:
    """模型信息"""
    id: str
    name: str
    description: Optional[str] = None
    context_window: int = 4096
    supports_streaming: bool = True
    supports_function_calling: bool = False


@dataclass(frozen=True)
class ProviderMeta:
    """供应商元数据"""
    id: str
    display_name: str
    description: str
    required_keys: List[str] = field(default_factory=list)
    optional_keys: List[str] = field(default_factory=list)
    default_base_url: Optional[str] = None
    discovery_format: str = "openai"
    models: Dict[str, ModelInfo] = field(default_factory=dict)

    @property
    def all_keys(self) -> List[str]:
        return self.required_keys + self.optional_keys


# 定义支持的供应商和模型
PROVIDER_REGISTRY: Dict[str, ProviderMeta] = {
    "anthropic": ProviderMeta(
        id="anthropic",
        display_name="Anthropic",
        description="Anthropic Claude 系列模型，擅长学术写作和深度分析",
        required_keys=["api_key"],
        optional_keys=["base_url"],
        default_base_url="https://api.anthropic.com",
        discovery_format="anthropic",
        models={
            "claude-3-5-sonnet-20241022": ModelInfo(
                id="claude-3-5-sonnet-20241022",
                name="Claude 3.5 Sonnet",
                description="最新的 Claude 3.5 Sonnet - 学术写作推荐",
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "claude-3-5-haiku-20241022": ModelInfo(
                id="claude-3-5-haiku-20241022",
                name="Claude 3.5 Haiku",
                description="快速且经济的模型",
                context_window=200000,
                supports_streaming=True,
            ),
            "claude-3-opus-20240229": ModelInfo(
                id="claude-3-opus-20240229",
                name="Claude 3 Opus",
                description="最强大的 Claude 3 模型 - 深度分析",
                context_window=200000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "claude-3-sonnet-20240229": ModelInfo(
                id="claude-3-sonnet-20240229",
                name="Claude 3 Sonnet",
                description="平衡性能的模型",
                context_window=200000,
                supports_streaming=True,
            ),
        },
    ),
    "openai": ProviderMeta(
        id="openai",
        display_name="OpenAI",
        description="OpenAI GPT 系列模型，知识面广泛",
        required_keys=["api_key"],
        optional_keys=["base_url", "organization_id"],
        default_base_url="https://api.openai.com/v1",
        discovery_format="openai",
        models={
            "gpt-4o": ModelInfo(
                id="gpt-4o",
                name="GPT-4o",
                description="最新的 GPT-4 Omni - 多模态能力",
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "gpt-4-turbo": ModelInfo(
                id="gpt-4-turbo",
                name="GPT-4 Turbo",
                description="GPT-4 Turbo - 知识面广",
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "gpt-4": ModelInfo(
                id="gpt-4",
                name="GPT-4",
                description="标准 GPT-4",
                context_window=8192,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "gpt-3.5-turbo": ModelInfo(
                id="gpt-3.5-turbo",
                name="GPT-3.5 Turbo",
                description="快速且经济",
                context_window=16385,
                supports_streaming=True,
                supports_function_calling=True,
            ),
        },
    ),
    "deepseek": ProviderMeta(
        id="deepseek",
        display_name="DeepSeek",
        description="DeepSeek 深度求索 - 性价比之王",
        required_keys=["api_key"],
        optional_keys=["base_url"],
        default_base_url="https://api.deepseek.com/v1",
        discovery_format="openai",
        models={
            "deepseek-chat": ModelInfo(
                id="deepseek-chat",
                name="DeepSeek Chat",
                description="通用对话模型 - 性价比极高 💰",
                context_window=32768,
                supports_streaming=True,
            ),
            "deepseek-coder": ModelInfo(
                id="deepseek-coder",
                name="DeepSeek Coder",
                description="代码生成专用模型",
                context_window=16384,
                supports_streaming=True,
            ),
        },
    ),
    "qwen": ProviderMeta(
        id="qwen",
        display_name="通义千问",
        description="阿里云通义千问 - 中文学术写作优秀",
        required_keys=["api_key"],
        optional_keys=["base_url"],
        default_base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
        discovery_format="openai",
        models={
            "qwen-max": ModelInfo(
                id="qwen-max",
                name="通义千问 Max",
                description="最强性能 - 中文学术写作推荐",
                context_window=8192,
                supports_streaming=True,
            ),
            "qwen-plus": ModelInfo(
                id="qwen-plus",
                name="通义千问 Plus",
                description="平衡性能与成本",
                context_window=32768,
                supports_streaming=True,
            ),
            "qwen-turbo": ModelInfo(
                id="qwen-turbo",
                name="通义千问 Turbo",
                description="快速响应 - 适合大纲生成",
                context_window=8192,
                supports_streaming=True,
            ),
            "qwen-long": ModelInfo(
                id="qwen-long",
                name="通义千问 Long",
                description="长文本模型 - 1M 上下文",
                context_window=1000000,
                supports_streaming=True,
            ),
        },
    ),
    "chatglm": ProviderMeta(
        id="chatglm",
        display_name="智谱 ChatGLM",
        description="智谱 AI ChatGLM - 工具调用优秀",
        required_keys=["api_key"],
        optional_keys=["base_url"],
        default_base_url="https://open.bigmodel.cn/api/paas/v4",
        discovery_format="openai",
        models={
            "glm-4-plus": ModelInfo(
                id="glm-4-plus",
                name="GLM-4 Plus",
                description="最强性能 - 工具调用优秀",
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "glm-4": ModelInfo(
                id="glm-4",
                name="GLM-4",
                description="标准版本 - 中文优秀",
                context_window=128000,
                supports_streaming=True,
                supports_function_calling=True,
            ),
            "glm-4-air": ModelInfo(
                id="glm-4-air",
                name="GLM-4 Air",
                description="轻量快速版",
                context_window=128000,
                supports_streaming=True,
            ),
            "glm-4-flash": ModelInfo(
                id="glm-4-flash",
                name="GLM-4 Flash",
                description="极速响应",
                context_window=128000,
                supports_streaming=True,
            ),
        },
    ),
    "moonshot": ProviderMeta(
        id="moonshot",
        display_name="月之暗面 Moonshot",
        description="月之暗面 Kimi - 超长上下文",
        required_keys=["api_key"],
        optional_keys=["base_url"],
        default_base_url="https://api.moonshot.cn/v1",
        discovery_format="openai",
        models={
            "moonshot-v1-8k": ModelInfo(
                id="moonshot-v1-8k",
                name="Moonshot 8K",
                description="8K 上下文窗口",
                context_window=8192,
                supports_streaming=True,
            ),
            "moonshot-v1-32k": ModelInfo(
                id="moonshot-v1-32k",
                name="Moonshot 32K",
                description="32K 上下文窗口",
                context_window=32768,
                supports_streaming=True,
            ),
            "moonshot-v1-128k": ModelInfo(
                id="moonshot-v1-128k",
                name="Moonshot 128K",
                description="128K 超长上下文 - 文献综述推荐",
                context_window=131072,
                supports_streaming=True,
            ),
        },
    ),
}


def get_provider_meta(provider_id: str) -> Optional[ProviderMeta]:
    """获取供应商元数据"""
    return PROVIDER_REGISTRY.get(provider_id)


def get_model_info(provider_id: str, model_id: str) -> Optional[ModelInfo]:
    """获取模型信息"""
    provider = get_provider_meta(provider_id)
    if not provider:
        return None
    return provider.models.get(model_id)


def list_providers() -> List[ProviderMeta]:
    """列出所有供应商"""
    return list(PROVIDER_REGISTRY.values())


def list_provider_models(provider_id: str) -> List[ModelInfo]:
    """列出供应商的所有模型"""
    provider = get_provider_meta(provider_id)
    if not provider:
        return []
    return list(provider.models.values())
