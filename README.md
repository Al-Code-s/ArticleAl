# ArticleAI - AI论文写作系统

基于AI智能体的论文写作辅助系统，支持从选题、大纲、参考文献到完整论文的全流程生成。

## 主要特性

- 🎯 **智能选题**：基于专业、学历、论文类型自动生成候选题目
- 🤖 **项目智能体**：每个项目拥有独立的AI助手，支持自然语言交互
- 📝 **全流程生成**：任务书、开题报告、文献综述、论文正文一站式生成
- 📚 **知网文献搜索**：集成知网搜索，自动查找和引用学术文献
- 📄 **多格式导出**：支持导出为Word、PDF格式
- ⚙️ **多模型支持**：支持Claude、OpenAI等多种AI模型，可自定义API
- 🔄 **并发操作**：支持多项目同时进行，每个项目独立运行

## 技术栈

### 前端
- React 18 + TypeScript
- Ant Design
- Vite
- Zustand（状态管理）
- TanStack Query（数据请求）
- Axios（HTTP 客户端）

### 后端
- **Python 3.11+**
- **FastAPI** - 现代高性能 Web 框架
- **PostgreSQL** - 关系型数据库
- **Redis** - 缓存和会话存储
- **SQLAlchemy 2.0** - 异步ORM
- **Langchain** - AI 应用框架
- **Celery** - 异步任务队列

### AI能力
- Claude API (Anthropic)
- OpenAI API (GPT-4/GPT-3.5)
- MCP服务器（知网搜索）
- 自定义Agent编排

## 快速开始

### 环境要求

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- Redis 5.0+

### 本地开发

#### 1. 克隆项目

```bash
git clone https://github.com/yourusername/ArticleAI.git
cd ArticleAI
```

#### 2. 启动后端

```bash
cd backend

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
cp .env.example .env
# 编辑 .env 文件，配置数据库连接和 API 密钥

# 启动服务
python main.py
```

后端将在 http://localhost:3000 启动
- API文档: http://localhost:3000/docs
- 健康检查: http://localhost:3000/health

#### 3. 启动前端

```bash
cd frontend

# 安装依赖
npm install

# 配置环境变量
cp .env.example .env

# 启动开发服务器
npm run dev
```

前端将在 http://localhost:5173 启动

### 使用 Docker（可选）

```bash
# 启动数据库和 Redis
cd docker
docker-compose -f docker-compose.dev.yml up -d

# 或者启动完整服务
docker-compose up -d
```

## 项目结构

```
ArticleAI/
├── frontend/                 # 前端应用（React + TypeScript）
│   ├── src/
│   │   ├── api/             # API 请求
│   │   ├── components/      # React 组件
│   │   ├── pages/           # 页面
│   │   ├── store/           # Zustand 状态管理
│   │   └── types/           # TypeScript 类型定义
│   └── package.json
│
├── backend/                  # 后端 API（Python + FastAPI）
│   ├── app/
│   │   ├── api/             # API 路由
│   │   ├── core/            # 核心配置
│   │   ├── models/          # 数据库模型
│   │   ├── schemas/         # Pydantic Schemas
│   │   ├── services/        # 业务逻辑
│   │   ├── agents/          # AI 智能体
│   │   ├── skills/          # AI 技能库
│   │   └── utils/           # 工具函数
│   ├── main.py              # 应用入口
│   └── requirements.txt     # Python 依赖
│
├── docker/                   # Docker 配置
│   ├── docker-compose.yml           # 生产环境
│   ├── docker-compose.dev.yml      # 开发环境
│   └── nginx/                       # Nginx 配置
│
└── docs/                     # 文档
```

## 功能模块

### 1. 用户认证
- 用户注册/登录
- JWT token 认证
- 用户信息管理

### 2. 项目管理
- 创建论文项目
- 配置专业、学历、论文类型
- 项目列表和详情查看
- 项目编辑和删除

### 3. 选题模块
- AI 生成论文题目
- 支持按专业、学历、论文类型筛选
- 一键保存选题到项目

### 4. 大纲生成
- 基于选题自动生成论文大纲
- 支持手动编辑和调整
- 章节层级管理

### 5. 参考文献
- 知网文献搜索
- 文献信息管理
- 自动生成引用格式

### 6. 智能体对话
- 自然语言交互
- 实时 WebSocket 通信
- 支持生成大纲、搜索文献、撰写内容
- 智能意图识别
- 可随时停止/重启

### 7. 文档生成
- 任务书生成
- 开题报告生成
- 文献综述生成
- 论文正文撰写

### 8. 导出功能
- Word 格式（.docx）
- PDF 格式
- 自定义模板支持

## 数据库设计

系统使用 PostgreSQL 数据库，主要表结构：

- **users** - 用户信息
- **ai_configs** - AI 配置
- **projects** - 论文项目
- **topics** - 选题
- **outlines** - 大纲
- **references** - 参考文献
- **documents** - 文档内容
- **paper_sections** - 论文章节
- **agent_sessions** - 智能体会话
- **agent_messages** - 智能体消息
- **export_records** - 导出记录

详细的数据库设计请参考 [backend/app/models](./backend/app/models)。

## API 文档

后端 API 采用 RESTful 设计，主要端点：

### 认证 API
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 项目 API
- `POST /api/projects` - 创建项目
- `GET /api/projects` - 获取项目列表
- `GET /api/projects/{id}` - 获取项目详情
- `PUT /api/projects/{id}` - 更新项目
- `DELETE /api/projects/{id}` - 删除项目

### 选题 API
- `POST /api/topics/generate` - AI 生成选题
- `GET /api/topics` - 获取选题列表
- `POST /api/topics/{id}/select` - 选择选题
- `PUT /api/topics/{id}` - 更新选题
- `DELETE /api/topics/{id}` - 删除选题

### 大纲 API
- `POST /api/outlines/generate` - AI 生成大纲
- `GET /api/outlines` - 获取大纲列表
- `GET /api/outlines/{id}` - 获取大纲详情
- `PUT /api/outlines/{id}` - 更新大纲（自动版本控制）
- `DELETE /api/outlines/{id}` - 删除大纲

### 参考文献 API
- `POST /api/references/search` - AI 搜索参考文献
- `POST /api/references` - 手动添加文献
- `GET /api/references` - 获取文献列表
- `GET /api/references/{id}` - 获取文献详情
- `PUT /api/references/{id}` - 更新文献
- `DELETE /api/references/{id}` - 删除文献

### 文档 API
- `POST /api/documents/generate` - AI 生成文档
- `POST /api/documents` - 手动创建文档
- `GET /api/documents` - 获取文档列表
- `GET /api/documents/{id}` - 获取文档详情
- `PUT /api/documents/{id}` - 更新文档（自动版本控制）
- `DELETE /api/documents/{id}` - 删除文档

### WebSocket API
- `WS /ws/chat` - 实时对话连接（需要 JWT token）

### 导出 API
- `POST /api/export/document/{id}` - 导出文档为 Word/PDF
- `POST /api/export/custom` - 导出自定义内容

完整的 API 文档访问: http://localhost:3000/docs

## 配置说明

### 环境变量

#### 后端 (.env)

```bash
# 数据库
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/articleai
DATABASE_ECHO=False

# Redis
REDIS_URL=redis://localhost:6379/0

# JWT
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# CORS
CORS_ORIGINS=http://localhost:5173

# AI API
ANTHROPIC_API_KEY=sk-ant-xxx
OPENAI_API_KEY=sk-xxx

# Celery
CELERY_BROKER_URL=redis://localhost:6379/1
CELERY_RESULT_BACKEND=redis://localhost:6379/2
```

#### 前端 (.env)

```bash
VITE_API_URL=http://localhost:3000
VITE_WS_URL=ws://localhost:3000
```

### AI 模型配置

系统支持配置多个 AI 模型：

1. **Claude (Anthropic)** - 推荐用于论文生成
2. **OpenAI GPT-4** - 备选方案
3. 自定义 API 端点

在用户设置页面可以添加和管理 AI 配置。

## 开发指南

### 后端开发

```bash
cd backend

# 安装开发依赖
pip install -r requirements.txt

# 运行测试
pytest

# 代码格式化
black app/
isort app/

# 类型检查
mypy app/
```

### 前端开发

```bash
cd frontend

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build

# 代码检查
npm run lint

# 类型检查
npm run type-check
```

## 部署

### Docker 部署（推荐）

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 手动部署

请参考 [部署文档](./docs/deployment.md)

## 常见问题

### Q: 数据库连接失败？
A: 请确保 PostgreSQL 正在运行，并检查 `.env` 文件中的数据库连接字符串是否正确。

### Q: AI API 调用失败？
A: 请检查 API 密钥是否正确配置，并确保有足够的配额。

### Q: 前端无法连接后端？
A: 检查 CORS 配置，确保前端地址在 `CORS_ORIGINS` 中。

## 开发文档

详细的开发文档请查看 [docs](./docs) 目录：

- [架构设计](./docs/architecture.md)
- [API 文档](./docs/api/README.md)
- [智能体开发指南](./docs/agent-guide.md)
- [MCP 集成指南](./docs/mcp-integration.md)
- [部署文档](./docs/deployment.md)

## 更新日志

### v1.0.0 (2024)
- ✅ 用户认证系统
- ✅ 项目管理功能
- ✅ 数据库模型设计
- ✅ 选题生成功能（AI集成）
- ✅ 大纲生成功能（AI集成）
- ✅ 参考文献搜索（AI集成）
- ✅ 文档生成功能（AI集成）
- ✅ WebSocket 实时对话
- ✅ Word/PDF 导出功能
- ✅ 前端 API 集成
- 🚧 前端 UI 界面完善

## 许可证

MIT License

## 贡献

欢迎提交 Issue 和 Pull Request！

## 联系方式

如有问题或建议，请提交 Issue。
