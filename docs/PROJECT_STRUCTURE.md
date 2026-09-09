# 项目结构说明

本文档详细说明ArticleAI项目的目录结构和文件组织。

## 整体结构

```
ArticleAl/
├── backend/           # 后端应用（FastAPI + Python）
├── frontend/          # 前端应用（React + TypeScript + Vite）
├── docker/            # Docker配置文件
├── docs/              # 项目文档
├── .env.example       # 环境变量模板
├── .gitignore         # Git忽略文件
├── README.md          # 项目说明
├── LICENSE            # 开源许可证
├── CONTRIBUTING.md    # 贡献指南
└── PROJECT_SUMMARY.md # 项目总结
```

## 后端结构（backend/）

### 配置文件

- `requirements.txt` - Python依赖管理
- `pyproject.toml` - Python项目配置
- `.env.example` - 环境变量模板
- `Dockerfile` - Docker镜像构建文件
- `main.py` - FastAPI应用入口

### 源代码（app/）

#### 核心模块（core/）

- `config.py` - 应用配置（Settings）
- `database.py` - 数据库连接和会话管理
- `redis.py` - Redis连接管理
- `security.py` - JWT认证和密码处理
- `encryption.py` - 数据加密（API密钥加密）

#### 数据模型（models/）

SQLAlchemy 2.0 异步模型：
- `user.py` - 用户模型
- `ai_config.py` - AI配置模型
- `topic.py` - 选题模型
- `project.py` - 项目模型
- `outline.py` - 大纲模型
- `reference.py` - 参考文献模型
- `document.py` - 文档模型
- `paper_section.py` - 论文章节模型
- `agent_session.py` - 智能体会话模型
- `agent_message.py` - 智能体消息模型
- `export_record.py` - 导出记录模型

#### Pydantic Schemas（schemas/）

请求/响应数据验证：
- `user.py` - 用户Schema
- `auth.py` - 认证Schema
- `project.py` - 项目Schema
- `topic.py` - 选题Schema
- `agent.py` - 智能体Schema
- `document.py` - 文档Schema
- 等等...

#### API路由（api/）

FastAPI路由处理器：
- `auth.py` - 认证授权（注册、登录、Token刷新）
- `users.py` - 用户管理
- `topics.py` - 选题管理（AI生成选题）
- `projects.py` - 项目管理（CRUD）
- `outlines.py` - 大纲管理（AI生成大纲）
- `references.py` - 参考文献（AI搜索文献）
- `documents.py` - 文档管理（AI生成文档）
- `chat.py` - WebSocket聊天路由
- `export.py` - 导出服务（Word/PDF）
- `ai_configs.py` - AI配置管理

#### 业务服务（services/）

业务逻辑层：
- `auth_service.py` - 认证服务
- `project_service.py` - 项目服务
- `ai_service.py` - AI调用服务
- 等等...

#### AI智能体（agents/）

- `base_agent.py` - 智能体基类
- `project_agent.py` - 项目智能体
- `chat_agent.py` - 聊天智能体

#### AI技能库（skills/）

- `outline_skill.py` - 大纲生成技能
- `reference_skill.py` - 文献搜索技能
- `document_skill.py` - 文档生成技能

#### MCP集成（mcp/）

- MCP服务器集成（知网搜索等）

#### 工具函数（utils/）

- `doc_generator.py` - Word文档生成
- `pdf_generator.py` - PDF生成
- 其他工具函数

## 前端结构（frontend/）

### 配置文件

- `package.json` - 项目配置和依赖
- `tsconfig.json` - TypeScript配置
- `vite.config.ts` - Vite构建配置
- `.prettierrc` - 代码格式化配置
- `Dockerfile` - Docker镜像构建
- `nginx.conf` - Nginx配置
- `index.html` - HTML入口

### 源代码（src/）

#### 入口文件

- `main.tsx` - 应用入口
- `App.tsx` - 根组件
- `index.css` - 全局样式

#### 页面（pages/）

每个页面包含：
- `index.tsx` - 页面组件
- `*.css` - 页面样式

**主要页面：**
- `Login/` - 登录页
- `Register/` - 注册页
- `TopicHall/` - 选题大厅
- `ProjectList/` - 项目列表
- `ProjectWorkspace/` - 项目工作区
  - 包含智能体对话、大纲、文献、文档等功能
- `Settings/` - 系统设置

#### 组件（components/）

**layouts/ - 布局组件**
- `MainLayout.tsx` - 主布局（头部、侧边栏、内容区）

**业务组件：**
- `ProtectedRoute.tsx` - 路由守卫
- `ChatPanel/` - 聊天面板组件
- `ExportButton/` - 导出按钮组件

#### 服务（services/）

**api/ - API服务**
- `client.ts` - Axios客户端配置
- `auth.ts` - 认证API
- `topic.ts` - 选题API
- `project.ts` - 项目API
- `agent.ts` - 智能体API
- `document.ts` - 文档API
- `outline.ts` - 大纲API
- `reference.ts` - 参考文献API
- `export.ts` - 导出API

**websocket/ - WebSocket服务**
- `agentSocket.ts` - 智能体WebSocket连接
- `chatSocket.ts` - 聊天WebSocket连接

#### 状态管理（stores/）

使用Zustand进行状态管理：
- `userStore.ts` - 用户状态
- `projectStore.ts` - 项目状态
- `agentStore.ts` - 智能体状态
- `chatStore.ts` - 聊天状态

#### 类型定义（types/）

TypeScript类型定义：
- `auth.ts` - 认证相关类型
- `topic.ts` - 选题类型
- `project.ts` - 项目类型
- `agent.ts` - 智能体类型
- `document.ts` - 文档类型
- `outline.ts` - 大纲类型
- `reference.ts` - 参考文献类型

#### 工具函数（utils/）

公共工具函数

#### 自定义Hooks（hooks/）

可复用的React Hooks

## Docker配置（docker/）

### 主要文件

- `docker-compose.yml` - 生产环境编排
- `docker-compose.dev.yml` - 开发环境编排

### Nginx配置

- `nginx/nginx.conf` - Nginx配置文件

### PostgreSQL配置

- `postgres/init.sql` - 数据库初始化脚本
- `postgres/init-dev.sql` - 开发环境测试数据

## 文档（docs/）

### 主要文档

- `architecture.md` - 架构设计文档
- `deployment.md` - 部署文档
- `agent-guide.md` - 智能体开发指南
- `mcp-integration.md` - MCP集成指南
- `api/README.md` - API接口文档

## 数据库设计

### 核心表

1. **用户相关**
   - `users` - 用户表
   - `ai_configs` - AI配置表

2. **选题和项目**
   - `topics` - 选题表
   - `projects` - 项目表

3. **项目内容**
   - `outlines` - 大纲表
   - `references` - 参考文献表
   - `documents` - 文档表（任务书、开题报告、文献综述）
   - `paper_sections` - 论文章节表

4. **智能体**
   - `agent_sessions` - 智能体会话表
   - `agent_messages` - 智能体消息表

5. **其他**
   - `revisions` - 修改记录表
   - `export_records` - 导出记录表
   - `job_queue` - 任务队列表

## 关键技术栈

### 后端

- **框架**: FastAPI 0.109
- **语言**: Python 3.11+
- **数据库**: PostgreSQL 16
- **缓存**: Redis 7
- **ORM**: SQLAlchemy 2.0 (异步)
- **任务队列**: Celery 5.3
- **AI框架**: Langchain 0.1+
- **AI API**: Anthropic 0.18+ / OpenAI 1.12+
- **文档处理**: python-docx 0.8 / ReportLab 5.0
- **异步HTTP**: HTTPX 0.26 / AIOHTTP 3.9+

### 前端

- **框架**: React 18.2
- **语言**: TypeScript 5.3
- **构建**: Vite 5.0
- **UI**: Ant Design 5.12
- **状态**: Zustand 4.4
- **请求**: Axios 1.6 + TanStack Query 5.17
- **WebSocket**: Socket.IO Client 4.6
- **Markdown**: React Markdown 9.0

### 部署

- **容器**: Docker
- **编排**: Docker Compose
- **代理**: Nginx

## 开发工作流

### 1. 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# Linux/Mac
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 启动开发服务器
python main.py
```

### 2. 前端开发

```bash
cd frontend
npm install
npm run dev
```

### 3. 数据库管理

```bash
cd backend

# 创建数据库迁移
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 4. 代码检查

```bash
# 后端
cd backend
black app/              # 代码格式化
isort app/              # import排序
mypy app/               # 类型检查
pytest                  # 运行测试

# 前端
cd frontend
npm run lint            # ESLint检查
npm run format          # Prettier格式化
```

### 5. Docker开发

```bash
# 启动开发环境（仅数据库和Redis）
cd docker
docker-compose -f docker-compose.dev.yml up -d

# 启动完整服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 环境变量说明

查看 `.env.example` 文件了解所有可配置的环境变量。

### 后端环境变量

关键变量：
- `DATABASE_URL` - PostgreSQL数据库连接URL
- `DATABASE_ECHO` - 是否打印SQL日志
- `REDIS_URL` - Redis连接URL
- `SECRET_KEY` - JWT密钥
- `ACCESS_TOKEN_EXPIRE_MINUTES` - Token过期时间
- `CORS_ORIGINS` - CORS允许的源
- `ANTHROPIC_API_KEY` - Claude API密钥
- `OPENAI_API_KEY` - OpenAI API密钥
- `CELERY_BROKER_URL` - Celery消息队列URL
- `CELERY_RESULT_BACKEND` - Celery结果存储URL

### 前端环境变量

- `VITE_API_URL` - 后端API地址
- `VITE_WS_URL` - WebSocket服务地址

## 端口分配

- `80` - Nginx（生产环境）
- `3000` - 后端API
- `5173` - 前端开发服务器
- `5432` - PostgreSQL
- `6379` - Redis

## 常见问题

### 1. 如何添加新的API端点？

1. 在 `backend/app/api/` 创建或编辑对应的路由文件
2. 定义FastAPI路由函数
3. 在 `backend/app/schemas/` 添加Pydantic Schema
4. 在 `backend/app/services/` 实现业务逻辑
5. 在前端 `frontend/src/services/api/` 添加调用方法
6. 更新API文档

### 2. 如何添加新的AI技能？

1. 在 `backend/app/skills/` 创建新的skill文件
2. 实现技能类，继承基类
3. 在智能体中注册和调用

### 3. 如何添加新的MCP服务？

1. 在 `backend/app/mcp/` 创建新的MCP服务
2. 实现MCP协议接口
3. 在需要的地方调用MCP服务

### 4. 如何处理数据库迁移？

使用Alembic进行数据库版本管理：
```bash
# 生成迁移脚本
alembic revision --autogenerate -m "描述"

# 执行迁移
alembic upgrade head

# 回滚
alembic downgrade -1
```

## 贡献指南

请查看 [CONTRIBUTING.md](../CONTRIBUTING.md) 了解如何为项目做贡献。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](../LICENSE) 文件了解详情。
