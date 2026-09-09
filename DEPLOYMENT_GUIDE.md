# AI 配置接口修复 - 部署指南

## 📋 已完成的修改

### 1. 新增文件
- ✅ `backend/app/config/__init__.py` - 配置模块初始化文件
- ✅ `backend/app/config/provider_registry.py` - AI 供应商注册表（6个供应商，21个模型）

### 2. 修改文件
- ✅ `backend/app/api/ai_configs.py` - AI 配置 API（新增2个接口）
- ✅ `backend/app/schemas/ai_config.py` - 数据模型（新增2个 Schema）

## 🚀 部署步骤

### 步骤 1: 重启后端服务

**方法一：如果使用 Docker**
```bash
cd /e/github/ArticleAl
docker-compose restart backend
```

**方法二：如果直接运行 Python**
```bash
# 1. 停止当前的后端进程（按 Ctrl+C 或关闭终端）

# 2. 重新启动
cd /e/github/ArticleAl/backend
python main.py
# 或者
python -m uvicorn main:app --reload --host 0.0.0.0 --port 3000
```

### 步骤 2: 验证接口

**1. 测试供应商列表接口**
```bash
curl http://localhost:3000/api/ai-configs/providers
```

预期响应：
```json
{
  "providers": [
    {
      "id": "anthropic",
      "display_name": "Anthropic",
      "description": "Anthropic Claude 系列模型，擅长学术写作和深度分析",
      "model_count": 4,
      ...
    },
    ...
  ]
}
```

**2. 测试获取模型列表接口**
```bash
curl -X POST http://localhost:3000/api/ai-configs/actions/fetch-models \
  -H "Content-Type: application/json" \
  -d '{"provider":"anthropic","apiKey":"test-key"}'
```

预期响应：
```json
{
  "models": [
    {
      "id": "claude-3-5-sonnet-20241022",
      "name": "Claude 3.5 Sonnet",
      "description": "最新的 Claude 3.5 Sonnet - 学术写作推荐"
    },
    ...
  ]
}
```

## 📱 前端集成说明

### 更新前端代码

你的前端代码在 `frontend/src/pages/Settings/index.tsx` 中，建议按以下步骤优化：

**1. 先调用供应商列表接口获取所有供应商**
```typescript
const { data: providersData } = useQuery({
  queryKey: ['ai-providers'],
  queryFn: () => apiClient.get('/ai-configs/providers'),
});
```

**2. 用户选择供应商后，调用获取模型接口**
```typescript
const handleFetchModels = async (provider: string, apiKey: string) => {
  const res = await apiClient.post('/ai-configs/actions/fetch-models', {
    provider,
    apiKey,
  });
  setModels(res.models);
};
```

### 优势
- ✅ 用户可以先看到所有支持的 AI 供应商
- ✅ 无需输入 API Key 就能看到每个供应商有哪些模型
- ✅ 只有真正保存配置时才需要真实的 API Key
- ✅ 提供了每个供应商的默认 Base URL

## 🎯 支持的 AI 供应商

| 供应商 | 模型数量 | 特点 |
|--------|----------|------|
| Anthropic | 4 | Claude 系列，擅长学术写作 |
| OpenAI | 4 | GPT 系列，知识面广 |
| DeepSeek | 2 | 性价比之王 |
| 通义千问 | 4 | 中文学术写作优秀 |
| ChatGLM | 4 | 工具调用优秀 |
| Moonshot | 3 | 超长上下文（最高128K）|

## 🔍 故障排查

### 问题 1: 接口返回 404 Not Found
**原因**：后端服务器没有重启，新代码未加载  
**解决**：重启后端服务器

### 问题 2: 接口返回 405 Method Not Allowed
**原因**：路由注册有问题  
**解决**：检查 `backend/app/api/__init__.py` 是否正确导入了 `ai_configs` 路由

### 问题 3: 导入错误
**原因**：`backend/app/config` 目录或文件不存在  
**解决**：确认以下文件存在：
- `backend/app/config/__init__.py`
- `backend/app/config/provider_registry.py`

## 📝 测试清单

完成重启后，依次测试以下内容：

- [ ] `GET /api/health` - 健康检查
- [ ] `GET /api/ai-configs/providers` - 供应商列表
- [ ] `POST /api/ai-configs/actions/fetch-models` (anthropic) - 获取 Anthropic 模型
- [ ] `POST /api/ai-configs/actions/fetch-models` (openai) - 获取 OpenAI 模型
- [ ] `POST /api/ai-configs/actions/fetch-models` (qwen) - 获取通义千问模型
- [ ] 前端页面：访问设置页面，测试 AI 配置功能

## 🎉 完成后的效果

1. 用户打开设置页面，可以看到所有支持的 AI 供应商
2. 选择供应商后，立即显示该供应商的所有可用模型（无需 API Key）
3. 填写 API Key 和其他配置后保存
4. 系统使用保存的配置进行实际的 AI 调用

---

**重要提示**：必须重启后端服务器，新的接口才会生效！
