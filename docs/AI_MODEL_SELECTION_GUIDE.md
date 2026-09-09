# AI 模型选择指南

## 内容生成 AI 配置 - 模型选择建议

### 一、主流模型对比

| 模型提供商 | 推荐模型 | 优势 | 适用场景 | 价格 |
|-----------|---------|------|---------|------|
| **Anthropic Claude** | claude-3-5-sonnet-20241022 | 长文本理解强、逻辑性好、中英文都优秀 | 学术论文、研究报告、复杂大纲 | 较高 |
| **DeepSeek** | deepseek-chat / deepseek-v3 | 性价比极高、中文优秀、推理能力强 | 通用文章生成、大纲、综述 | 极低 |
| **阿里千问** | qwen-max / qwen-turbo | 中文生成流畅、知识面广、速度快 | 中文论文、新闻稿、通用内容 | 低 |
| **OpenAI GPT** | gpt-4-turbo / gpt-4o | 创造性强、知识面广、稳定性高 | 创意写作、多语言内容 | 高 |
| **智谱 ChatGLM** | glm-4 / glm-4-plus | 中文优秀、工具调用强 | 中文学术写作 | 中 |
| **百度文心** | ernie-4.0 / ernie-3.5 | 中文理解深、SEO友好 | 中文内容创作、营销文案 | 低 |
| **讯飞星火** | spark-max / spark-3.5 | 教育场景优秀、中文流畅 | 教学材料、科普文章 | 中 |
| **月之暗面 Kimi** | moonshot-v1 | 超长上下文（200k）、摘要能力强 | 文献综述、长文档分析 | 中 |

### 二、按使用场景推荐

#### 1. 学术论文写作（中文）
**首选：**
- DeepSeek V3（性价比）
- 阿里千问 qwen-max（中文流畅度）
- Claude 3.5 Sonnet（质量最高）

**API配置：**
```
DeepSeek:
  Base URL: https://api.deepseek.com
  模型: deepseek-chat

千问:
  Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
  模型: qwen-max
```

#### 2. 英文论文/国际期刊
**首选：**
- Claude 3.5 Sonnet（学术规范性最好）
- GPT-4 Turbo（知识面广）

#### 3. 文献综述
**首选：**
- Moonshot（超长上下文）
- Claude 3 Opus（深度分析）
- DeepSeek V3（性价比）

#### 4. 通用内容生成
**首选：**
- DeepSeek Chat（最佳性价比）
- 千问 Turbo（速度快）
- GLM-4（中文稳定）

#### 5. 预算有限
**首选：**
- DeepSeek（1元/百万tokens）
- 千问 Turbo（0.3元/百万tokens）
- 文心 3.5（0.8元/百万tokens）

### 三、API 配置示例

#### DeepSeek
```
提供商: 自定义
API Base URL: https://api.deepseek.com/v1
API Key: sk-...
模型名称: deepseek-chat 或 deepseek-v3
```

#### 阿里千问
```
提供商: 自定义
API Base URL: https://dashscope.aliyuncs.com/compatible-mode/v1
API Key: sk-...
模型名称: qwen-max / qwen-turbo / qwen-plus
```

#### 智谱 ChatGLM
```
提供商: 自定义
API Base URL: https://open.bigmodel.cn/api/paas/v4
API Key: ...
模型名称: glm-4 / glm-4-plus / glm-4-flash
```

#### 百度文心
```
提供商: 自定义
API Base URL: https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop
API Key: （需要用Access Token）
模型名称: ernie-4.0-turbo / ernie-3.5
```

#### 讯飞星火
```
提供商: 自定义
API Base URL: https://spark-api.xf-yun.com/v3.5
API Key: ...
模型名称: spark-max / spark-3.5
```

#### Moonshot (Kimi)
```
提供商: 自定义
API Base URL: https://api.moonshot.cn/v1
API Key: sk-...
模型名称: moonshot-v1-8k / moonshot-v1-32k / moonshot-v1-128k
```

### 四、推荐配置方案

#### 方案A：质量优先（预算充足）
- **内容生成**: Claude 3.5 Sonnet
- **智能体**: Claude 3.5 Sonnet
- **总成本**: $$$$

#### 方案B：性价比最优（推荐）
- **内容生成**: DeepSeek V3（或千问 Max）
- **智能体**: Claude 3.5 Haiku（轻量快速）
- **总成本**: $

#### 方案C：全国产方案
- **内容生成**: 千问 Max
- **智能体**: GLM-4
- **总成本**: $$

#### 方案D：超长文本场景
- **内容生成**: Moonshot 128k
- **智能体**: Claude 3.5 Sonnet
- **总成本**: $$$

### 五、参数建议

#### Temperature（创造性）
- **学术论文**: 0.3-0.5（更准确）
- **通用文章**: 0.7（平衡）
- **创意写作**: 0.8-1.0（更有创意）

#### Max Tokens
- **短文章/大纲**: 2048
- **标准论文**: 4096
- **长论文/综述**: 8192
- **超长文档**: 16384+

### 六、注意事项

1. **兼容性**: 大多数国产模型都支持 OpenAI 格式的 API，可以选择"自定义"提供商
2. **API Key 获取**:
   - DeepSeek: https://platform.deepseek.com
   - 千问: https://dashscope.console.aliyun.com
   - ChatGLM: https://open.bigmodel.cn
   - 文心: https://console.bce.baidu.com/qianfan
   - 星火: https://console.xfyun.cn
   - Moonshot: https://platform.moonshot.cn

3. **成本控制**: 建议先用小模型测试，满意后再用大模型正式生成

4. **模型切换**: 不同部分可以用不同模型
   - 大纲: 用便宜的快速模型（如千问 Turbo）
   - 正文: 用质量好的模型（如 Claude / DeepSeek V3）
   - 文献综述: 用长上下文模型（如 Moonshot）

### 七、实测推荐（2026年9月）

**最推荐的组合：**
1. **DeepSeek V3** - 内容生成主力（性价比之王）
2. **Claude 3.5 Sonnet** - 智能体对话（体验最好）

**理由：**
- DeepSeek V3 的质量已经接近 GPT-4，但价格只有1/100
- 中英文都优秀，特别适合学术写作
- Claude 智能体的工具调用和对话体验最好

**总成本：** 生成一篇10000字论文约0.5-1元人民币
