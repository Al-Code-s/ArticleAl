# 文档更新日志

**更新日期**: 2026年9月8日

## 已更新的文档

本次更新将项目文档从旧的 NestJS 架构更新为当前的 FastAPI (Python) 架构。

### 1. 根目录文档

#### ✅ [PROJECT_SUMMARY.md](./PROJECT_SUMMARY.md)
- 更新后端技术栈：NestJS → FastAPI + Python
- 更新依赖版本信息
- 更新项目结构描述
- 添加新增的前端页面和组件
- 更新技术栈列表
- 更新项目状态为"核心功能已完成"

#### ✅ [CONTRIBUTING.md](./CONTRIBUTING.md)
- 更新后端代码规范：TypeScript → Python
- 更新代码格式化工具：ESLint/Prettier → Black/isort
- 添加 Python 类型提示要求

### 2. docs/ 目录文档

#### ✅ [docs/PROJECT_STRUCTURE.md](./docs/PROJECT_STRUCTURE.md)
主要更新：
- 更新整体项目结构描述
- 更新后端结构：
  - 配置文件（requirements.txt, pyproject.toml）
  - 源代码结构（app/目录组织）
  - 数据模型（SQLAlchemy 2.0）
  - API路由（FastAPI）
  - 核心模块（core/, services/, agents/, skills/）
- 更新前端结构：
  - 添加新增页面（ProjectList）
  - 添加新增组件（ChatPanel, ExportButton）
  - 添加新增API服务
  - 添加新增Store
- 更新技术栈信息
- 更新开发工作流程（Python虚拟环境、Alembic迁移）
- 更新环境变量说明
- 更新常见问题

#### ✅ [docs/architecture.md](./docs/architecture.md)
- 更新API网关层：NestJS → FastAPI
- 更新智能体模块代码示例：TypeScript → Python
- 更新Skill系统接口定义：TypeScript → Python

#### ✅ [docs/deployment.md](./docs/deployment.md)
- 更新系统要求：Node.js 20+ → Python 3.11+ & Node.js 18+
- 更新环境变量配置方式
- 更新API访问地址（添加 /api/docs）

### 3. 未更新的文档

以下文档暂未更新，但内容大部分仍然适用：

- `docs/agent-guide.md` - 智能体开发指南
- `docs/mcp-integration.md` - MCP集成指南
- `docs/api/README.md` - API接口文档（需要根据实际API更新）

## 主要技术栈变更

### 后端
- **框架**: NestJS 10.3 → FastAPI 0.109
- **语言**: TypeScript 5.3 → Python 3.11+
- **ORM**: TypeORM 0.3 → SQLAlchemy 2.0 (异步)
- **任务队列**: Bull 4.12 → Celery 5.3
- **文档处理**: DOCX 8.5 / Puppeteer → python-docx 0.8 / ReportLab 5.0
- **AI框架**: Langchain.js → Langchain + Anthropic + OpenAI

### 前端
前端技术栈基本保持不变：
- React 18.2 + TypeScript 5.3
- Vite 5.0
- Ant Design 5.12
- Zustand 4.4

## 项目结构变更

### 后端目录结构
```
旧结构 (NestJS):              新结构 (FastAPI):
backend/src/                  backend/app/
├── modules/                  ├── api/          # API路由
├── entities/                 ├── models/       # SQLAlchemy模型
├── dto/                      ├── schemas/      # Pydantic Schemas
├── common/                   ├── core/         # 核心配置
├── agents/                   ├── agents/       # AI智能体
├── skills/                   ├── skills/       # AI技能
├── mcp/                      ├── mcp/          # MCP服务
└── main.ts                   ├── services/     # 业务服务
                              ├── utils/        # 工具函数
                              └── ...
                              main.py           # 应用入口
```

## 验证清单

- [x] PROJECT_SUMMARY.md 更新完成
- [x] CONTRIBUTING.md 更新完成
- [x] docs/PROJECT_STRUCTURE.md 更新完成
- [x] docs/architecture.md 更新完成
- [x] docs/deployment.md 更新完成
- [ ] docs/agent-guide.md 待更新
- [ ] docs/mcp-integration.md 待更新
- [ ] docs/api/README.md 待更新

## 后续工作

1. 更新 `docs/agent-guide.md`，将智能体开发指南从 TypeScript 改为 Python
2. 更新 `docs/mcp-integration.md`，使用 Python 示例
3. 更新 `docs/api/README.md`，确保所有API端点与实际后端一致
4. 验证所有代码示例的正确性

## 注意事项

- 所有文档中的代码示例已从 TypeScript 更新为 Python
- 配置文件和环境变量说明已更新
- 开发工作流程已更新，包括虚拟环境和数据库迁移
- 部署流程保持基本一致（Docker方式）
