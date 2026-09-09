# AI配置升级说明

## 升级内容

将AI配置从单一配置升级为双配置模式，区分**内容生成**和**智能体**两种用途。

## 变更概述

### 1. 数据库变更

**表名**: `ai_configs`

**新增字段**:
- `config_type` VARCHAR(50) NOT NULL - 配置类型
  - `content_generation`: 内容生成AI（用于生成文章、大纲、文献等）
  - `agent`: 智能体AI（用于MCP智能体对话功能）

**执行迁移**:
```bash
# 连接到PostgreSQL数据库
psql -U your_user -d your_database -f backend/migrations/add_config_type_to_ai_configs.sql
```

### 2. 后端变更

#### 2.1 模型变更 (backend/app/models/ai_config.py)
- 添加 `config_type` 字段

#### 2.2 Schema变更 (backend/app/schemas/ai_config.py)
- `AiConfigCreate`: 添加 `config_type` 字段（必填）
- `AiConfigResponse`: 添加 `config_type` 字段
- 新增 `FetchModelsRequest`: 获取模型列表请求
- 新增 `ModelInfo`: 模型信息
- 新增 `FetchModelsResponse`: 获取模型列表响应

#### 2.3 API变更 (backend/app/api/ai_configs.py)
- 添加 `POST /ai-configs/fetch-models` 端点：根据API Key获取可用模型列表
  - 支持 Anthropic API
  - 支持 OpenAI API
  - 如果API不支持列表，返回常用模型

### 3. 前端变更

#### 3.1 Settings页面 (frontend/src/pages/Settings/index.tsx)

**旧版本**：
- 单一AI配置表单
- 手动输入模型名称

**新版本**：
- 分为两个独立配置区域：
  1. **内容生成AI配置** - 用于文章、大纲生成
  2. **智能体AI配置** - 仅支持Anthropic，用于MCP智能体

**新增功能**：
- 点击"获取模型列表"按钮，自动从API获取可用模型
- 从下拉列表中选择模型（包含模型名称和描述）
- 配置类型标签区分

## 配置流程

### 内容生成AI配置
1. 输入配置名称（如：内容生成配置）
2. 选择提供商（Anthropic / OpenAI / 自定义）
3. 输入API Key
4. （可选）输入API Base URL
5. 点击"获取模型列表"
6. 从列表中选择模型
7. 调整Temperature和最大Tokens
8. 保存配置

### 智能体AI配置
1. 输入配置名称（如：智能体配置）
2. 提供商固定为Anthropic
3. 输入API Key
4. （可选）输入API Base URL
5. 点击"获取模型列表"
6. 从列表中选择Claude模型
7. 调整Temperature和最大Tokens
8. 保存配置

## API端点

### 获取模型列表
```
POST /api/ai-configs/fetch-models
```

**请求体**：
```json
{
  "provider": "anthropic",
  "apiKey": "sk-ant-...",
  "baseUrl": "https://api.anthropic.com"  // 可选
}
```

**响应**：
```json
{
  "models": [
    {
      "id": "claude-3-5-sonnet-20241022",
      "name": "Claude 3.5 Sonnet",
      "description": "最新的Claude 3.5 Sonnet模型"
    },
    ...
  ]
}
```

### 创建配置
```
POST /api/ai-configs
```

**请求体**：
```json
{
  "config_type": "content_generation",  // 新增字段
  "name": "内容生成配置",
  "provider": "anthropic",
  "model": "claude-3-5-sonnet-20241022",
  "apiKey": "sk-ant-...",
  "baseUrl": "https://api.anthropic.com",
  "temperature": 0.7,
  "maxTokens": 4096,
  "streamEnabled": true
}
```

## 兼容性说明

- 现有的AI配置数据会自动迁移为 `content_generation` 类型
- 前端向后兼容，可以正确显示旧配置
- 需要执行SQL迁移脚本才能使用新功能

## 测试清单

- [ ] 执行数据库迁移脚本
- [ ] 测试内容生成AI配置的创建和保存
- [ ] 测试智能体AI配置的创建和保存
- [ ] 测试Anthropic模型列表获取
- [ ] 测试OpenAI模型列表获取
- [ ] 验证旧配置数据迁移正确
- [ ] 测试配置列表显示（带类型标签）
- [ ] 测试模型选择下拉框显示

## 后续优化建议

1. 添加配置激活/停用功能
2. 添加配置编辑功能
3. 添加配置删除功能
4. 支持多个同类型配置，用户可切换
5. 添加配置测试功能（测试API Key是否有效）
6. 缓存模型列表，避免重复请求
