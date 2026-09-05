# ArticleAI 后端 API

基于 FastAPI 的论文写作系统后端服务。

## 技术栈

- **Python 3.11+**
- **FastAPI** - 现代高性能 Web 框架
- **SQLAlchemy 2.0** - 异步 ORM
- **PostgreSQL** - 关系型数据库
- **Redis** - 缓存和会话
- **Pydantic** - 数据验证
- **Langchain** - AI 应用框架
- **Celery** - 异步任务队列

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 配置环境变量

创建 `.env` 文件：

```bash
# 数据库配置
DATABASE_URL=postgresql+asyncpg://postgres:root123@localhost:5433/articleai
DATABASE_ECHO=False

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:5173

# AI API Keys
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

### 启动服务

```bash
python main.py
```

服务将在 `http://localhost:3000` 启动

- API 文档: http://localhost:3000/docs
- 健康检查: http://localhost:3000/health

## API 文档

### 认证模块 (`/api/auth`)

#### POST `/api/auth/register`
用户注册

**请求体：**
```json
{
  "username": "user123",
  "email": "user@example.com",
  "password": "password123"
}
```

**响应：**
```json
{
  "id": 1,
  "username": "user123",
  "email": "user@example.com",
  "created_at": "2024-01-01T00:00:00"
}
```

#### POST `/api/auth/login`
用户登录

**请求体：**
```json
{
  "username": "user123",
  "password": "password123"
}
```

**响应：**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user": {
    "id": 1,
    "username": "user123",
    "email": "user@example.com"
  }
}
```

#### GET `/api/auth/me`
获取当前用户信息（需要认证）

### 项目管理 (`/api/projects`)

#### POST `/api/projects`
创建项目

**请求体：**
```json
{
  "title": "基于AI的论文写作系统研究",
  "major": "计算机科学",
  "education_level": "本科",
  "paper_type": "毕业论文",
  "description": "项目描述"
}
```

#### GET `/api/projects`
获取项目列表（支持分页）

**查询参数：**
- `page`: 页码（默认 1）
- `page_size`: 每页数量（默认 20）

#### GET `/api/projects/{id}`
获取项目详情

#### PUT `/api/projects/{id}`
更新项目

#### DELETE `/api/projects/{id}`
删除项目

### 选题管理 (`/api/topics`)

#### POST `/api/topics/generate`
AI 生成论文选题

**请求体：**
```json
{
  "project_id": 1,
  "major": "计算机科学",
  "education_level": "本科",
  "paper_type": "毕业论文",
  "keywords": ["人工智能", "深度学习"]
}
```

**响应：**
```json
[
  {
    "id": 1,
    "title": "基于深度学习的图像识别研究",
    "description": "研究描述...",
    "major": "计算机科学",
    "education_level": "本科",
    "paper_type": "毕业论文",
    "keywords": ["深度学习", "图像识别"],
    "is_selected": false
  }
]
```

#### GET `/api/topics`
获取选题列表

**查询参数：**
- `project_id`: 项目ID（可选）
- `page`: 页码
- `page_size`: 每页数量

#### GET `/api/topics/{id}`
获取选题详情

#### POST `/api/topics/{id}/select`
选择该选题

#### PUT `/api/topics/{id}`
更新选题

#### DELETE `/api/topics/{id}`
删除选题

### 大纲管理 (`/api/outlines`)

#### POST `/api/outlines/generate`
AI 生成论文大纲

**请求体：**
```json
{
  "project_id": 1,
  "topic_title": "基于深度学习的图像识别研究",
  "requirements": "需要包含实验部分"
}
```

**响应：**
```json
{
  "id": 1,
  "title": "基于深度学习的图像识别研究",
  "content": {
    "sections": [
      {
        "level": 1,
        "title": "1. 引言",
        "order": 1,
        "subsections": [...]
      }
    ]
  },
  "version": 1
}
```

#### GET `/api/outlines`
获取大纲列表

#### GET `/api/outlines/{id}`
获取大纲详情

#### PUT `/api/outlines/{id}`
更新大纲（自动增加版本号）

#### DELETE `/api/outlines/{id}`
删除大纲

### 参考文献 (`/api/references`)

#### POST `/api/references/search`
搜索参考文献

**请求体：**
```json
{
  "keyword": "深度学习",
  "project_id": 1,
  "max_results": 10
}
```

**响应：**
```json
[
  {
    "id": 1,
    "title": "深度学习综述",
    "authors": ["张三", "李四"],
    "publication": "计算机学报",
    "year": 2023,
    "doi": "10.1234/example.2023.001",
    "abstract": "摘要内容...",
    "keywords": ["深度学习", "神经网络"]
  }
]
```

#### POST `/api/references`
手动添加参考文献

#### GET `/api/references`
获取参考文献列表

**查询参数：**
- `project_id`: 项目ID（可选）
- `page`: 页码
- `page_size`: 每页数量

#### GET `/api/references/{id}`
获取参考文献详情

#### PUT `/api/references/{id}`
更新参考文献

#### DELETE `/api/references/{id}`
删除参考文献

### 文档管理 (`/api/documents`)

#### POST `/api/documents/generate`
AI 生成文档

**请求体：**
```json
{
  "project_id": 1,
  "document_type": "thesis",
  "requirements": "需要包含案例分析"
}
```

**文档类型：**
- `proposal`: 开题报告
- `literature_review`: 文献综述
- `thesis`: 论文正文
- `assignment`: 任务书

**响应：**
```json
{
  "id": 1,
  "title": "论文标题 - 开题报告",
  "type": "proposal",
  "content": "文档内容...",
  "status": "draft",
  "word_count": 3500,
  "version": 1
}
```

#### POST `/api/documents`
手动创建文档

#### GET `/api/documents`
获取文档列表

**查询参数：**
- `project_id`: 项目ID（可选）
- `document_type`: 文档类型（可选）
- `status`: 状态（可选）
- `page`: 页码
- `page_size`: 每页数量

#### GET `/api/documents/{id}`
获取文档详情

#### PUT `/api/documents/{id}`
更新文档（自动增加版本号）

#### DELETE `/api/documents/{id}`
删除文档

### WebSocket 实时对话 (`/ws/chat`)

#### 连接 WebSocket
```javascript
const ws = new WebSocket('ws://localhost:3000/ws/chat?token=YOUR_JWT_TOKEN&project_id=1');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('收到消息:', data);
};

// 发送消息
ws.send(JSON.stringify({
  type: 'chat',
  message: '请帮我生成一个选题'
}));
```

**消息类型：**
- `chat`: 用户消息
- `response`: AI 响应
- `progress`: 生成进度
- `error`: 错误消息

**示例响应：**
```json
{
  "type": "response",
  "message": "我为您生成了3个选题建议...",
  "timestamp": "2024-01-20T10:30:00Z"
}
```

### 文档导出 (`/api/export`)

#### POST `/api/export/document/{document_id}`
导出已保存的文档

**查询参数：**
- `format`: 导出格式（`word` 或 `pdf`）

**响应：**
文件下载流（application/octet-stream）

#### POST `/api/export/custom`
导出自定义内容

**请求体：**
```json
{
  "title": "我的论文",
  "content": "论文内容（Markdown格式）",
  "format": "word"
}
```

**响应：**
文件下载流

**支持的格式：**
- `word`: Microsoft Word (.docx)
- `pdf`: PDF 文档

## 数据库模型

### User (用户)
- id: 主键
- username: 用户名（唯一）
- email: 邮箱（唯一）
- hashed_password: 加密密码
- is_active: 是否激活
- created_at: 创建时间

### Project (项目)
- id: 主键
- user_id: 用户ID（外键）
- title: 项目标题
- major: 专业
- education_level: 学历
- paper_type: 论文类型
- description: 项目描述
- status: 项目状态
- created_at, updated_at: 时间戳

### Topic (选题)
- id: 主键
- user_id, project_id: 外键
- title: 题目
- description: 描述
- keywords: 关键词（JSON）
- is_selected: 是否被选中

### Outline (大纲)
- id: 主键
- user_id, project_id: 外键
- title: 标题
- content: 大纲内容（JSON）
- version: 版本号

### Reference (参考文献)
- id: 主键
- user_id, project_id: 外键
- title: 文献标题
- authors: 作者列表（JSON）
- publication: 出版物
- year: 年份
- doi: DOI
- abstract: 摘要
- keywords: 关键词（JSON）

### Document (文档)
- id: 主键
- user_id, project_id: 外键
- title: 文档标题
- type: 文档类型（枚举）
- content: 文档内容
- status: 状态（草稿/完成）
- word_count: 字数
- version: 版本号

## 开发指南

### 添加新的 API

1. 在 `app/models/` 创建数据库模型
2. 在 `app/schemas/` 创建 Pydantic schemas
3. 在 `app/api/` 创建路由文件
4. 在 `app/api/__init__.py` 注册路由

### 运行测试

```bash
pytest
```

### 代码格式化

```bash
black app/
isort app/
```

## 部署

### Docker 部署

```bash
docker build -t articleai-backend .
docker run -p 3000:3000 --env-file .env articleai-backend
```

### 生产环境

使用 Gunicorn + Uvicorn workers：

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:3000
```

## 许可证

MIT License
