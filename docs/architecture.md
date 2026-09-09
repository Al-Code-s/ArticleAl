# ArticleAI 架构设计文档

## 系统架构

### 整体架构

ArticleAI采用前后端分离的微服务架构，主要包含以下几个层次：

1. **前端层（Frontend）**
   - React 18 + TypeScript
   - Ant Design UI组件库
   - Zustand状态管理
   - Socket.IO WebSocket客户端

2. **API网关层（API Gateway）**
   - FastAPI框架
   - RESTful API
   - WebSocket支持
   - JWT认证

3. **业务服务层（Business Services）**
   - 用户服务（User Service）
   - 项目服务（Project Service）
   - 智能体服务（Agent Service）
   - 文档服务（Document Service）
   - 导出服务（Export Service）

4. **AI编排层（AI Orchestration）**
   - Agent编排引擎
   - Skill执行引擎
   - MCP服务管理器
   - LLM适配层（Langchain）

5. **数据层（Data Layer）**
   - PostgreSQL（主数据库）
   - Redis（缓存和会话存储）
   - 文件存储（上传和导出）

## 核心模块设计

### 1. 智能体模块（Agent Module）

#### 1.1 项目智能体（Project Agent）

每个项目拥有独立的智能体实例，负责处理该项目的所有AI相关任务。

**核心功能：**
- 自然语言对话交互
- 意图识别和任务分发
- 上下文管理
- 状态跟踪

**技术实现：**
```python
class ProjectAgent:
    def __init__(self, project_id: str):
        self.project_id = project_id
        self.session = None
        self.llm_client = None
        self.skill_registry = SkillRegistry()
    
    async def process_message(self, user_input: str) -> dict:
        # 1. 意图识别
        intent = await self.parse_intent(user_input)
        
        # 2. 选择并执行Skill
        skill = self.skill_registry.get_skill(intent.action)
        result = await skill.execute(intent.params)
        
        # 3. 格式化响应
        return self.format_response(result)
```

#### 1.2 会话管理

**会话生命周期：**
1. 创建：用户启动智能体
2. 活跃：处理用户请求
3. 暂停：用户停止智能体
4. 恢复：重新启动智能体
5. 销毁：项目删除或会话超时

**并发控制：**
- 每个项目同时只能有一个活跃会话
- 使用Redis分布式锁保证会话唯一性
- 支持会话故障恢复

### 2. Skill系统

Skill是可复用的AI能力单元，封装特定的任务逻辑。

**Skill接口定义：**
```python
class Skill:
    name: str
    description: str
    
    async def execute(self, params: dict) -> Any:
        raise NotImplementedError
```

**内置Skill列表：**
- `outline-generation`：大纲生成
- `reference-search`：参考文献搜索
- `task-book-writing`：任务书写作
- `proposal-writing`：开题报告写作
- `literature-review-writing`：文献综述写作
- `paper-writing`：论文写作
- `content-revision`：内容修改

### 3. MCP服务

MCP（Model Context Protocol）服务提供外部能力接入。

#### 3.1 知网搜索MCP

**功能：**
- 搜索学术论文
- 获取论文详情
- 解析引用格式

**工具定义：**
```typescript
{
  name: "searchCNKI",
  description: "搜索知网学术论文",
  parameters: {
    keywords: string[],
    limit: number
  }
}
```

#### 3.2 文档处理MCP

**功能：**
- 解析DOCX文件
- 提取文本内容
- 文档格式转换

### 4. 任务队列系统

使用Bull队列处理异步长时任务。

**队列类型：**
- `document-generation`：文档生成队列
- `paper-writing`：论文写作队列
- `export`：导出队列

**优先级设置：**
- P1：用户主动触发的任务
- P2：Agent自动触发的任务
- P3：后台批处理任务

### 5. WebSocket通信

#### 5.1 消息协议

**客户端 → 服务端：**
```json
{
  "type": "message",
  "content": "用户输入内容"
}
```

**服务端 → 客户端：**
```json
{
  "type": "message|status|result",
  "data": {
    "role": "assistant",
    "content": "AI响应内容",
    "metadata": {}
  }
}
```

#### 5.2 连接管理

- 使用项目ID作为命名空间
- 支持断线重连
- 消息持久化到数据库

## 数据流设计

### 1. 用户发起请求

```
用户输入 
  → 前端验证 
  → WebSocket发送 
  → 后端接收 
  → 意图识别 
  → Skill执行 
  → LLM调用 
  → 结果处理 
  → WebSocket响应 
  → 前端展示
```

### 2. 文档生成流程

```
用户请求生成
  → 创建任务
  → 加入队列
  → 异步执行
    → 读取项目信息
    → 调用LLM生成
    → 流式写入数据库
    → 发送进度通知
  → 生成完成
  → 通知前端
```

## 安全设计

### 1. 认证授权

- JWT Token认证
- 密码bcrypt加密
- API密钥加密存储

### 2. 数据隔离

- 用户级数据隔离
- 项目级数据隔离
- 智能体会话隔离

### 3. 限流策略

- 用户级别限流
- API接口限流
- LLM调用限流

## 扩展性设计

### 1. 水平扩展

- 无状态API服务
- Redis共享会话
- 数据库读写分离

### 2. 插件化

- Skill插件系统
- MCP插件系统
- LLM Provider适配器

### 3. 多租户支持

- 租户隔离
- 配额管理
- 自定义配置

## 监控和日志

### 1. 应用监控

- 服务健康检查
- API性能监控
- 错误追踪

### 2. 业务监控

- 用户活跃度
- AI调用统计
- 文档生成统计

### 3. 日志系统

- 结构化日志
- 日志聚合
- 日志查询

## 性能优化

### 1. 缓存策略

- 用户信息缓存
- 项目信息缓存
- AI配置缓存

### 2. 数据库优化

- 索引优化
- 查询优化
- 连接池管理

### 3. 前端优化

- 代码分割
- 懒加载
- 资源压缩
